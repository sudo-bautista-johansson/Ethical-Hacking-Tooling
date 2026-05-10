import subprocess
import os
import re
import sys
from core import db

class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(msg): print(f"{Colors.OKBLUE}[*]{Colors.ENDC} {msg}")
def print_success(msg): print(f"{Colors.OKGREEN}[+]{Colors.ENDC} {msg}")
def print_error(msg): print(f"{Colors.FAIL}[-]{Colors.ENDC} {msg}")
def print_warning(msg): print(f"{Colors.WARNING}[!]{Colors.ENDC} {msg}")

def _check_nmap():
    """Verifica si Nmap está instalado."""
    try:
        subprocess.run(["nmap", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        print_error("ERROR FATAL: 'nmap' no está instalado o no está en el PATH.")
        print_warning("Instala Nmap o corre Farei_0x dentro de WSL/Kali Linux.")
        return False

def _run_nmap(args, ip):
    """Ejecuta Nmap con los argumentos dados y devuelve stdout."""
    cmd = ["nmap"] + args + [ip]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=300)
        return result.stdout
    except subprocess.TimeoutExpired:
        print_warning("Nmap tardó demasiado (>5 min). Considerá usar --min-rate más alto.")
        return ""
    except Exception as e:
        print_error(f"Error ejecutando Nmap: {e}")
        return ""

# ─── FASE 1: Escaneo Rápido de Puertos ───────────────────────────

def fast_port_scan(ip):
    """Escaneo ultra-rápido de los 65535 puertos TCP."""
    print(f"\n{Colors.BOLD}── FASE 1: Escaneo Rápido de Puertos (TCP) ──{Colors.ENDC}")
    print_status(f"Escaneando 65,535 puertos contra {ip}...")
    
    stdout = _run_nmap(["-p-", "--min-rate", "5000", "-T4", "-n", "-Pn", "--open"], ip)
    if not stdout:
        return []
    
    ports = re.findall(r'^(\d+)/tcp\s+open\s+([a-zA-Z0-9?-]+)', stdout, re.MULTILINE)
    
    if not ports:
        print_warning(f"No se encontraron puertos TCP abiertos en {ip}.")
        return []
    
    port_list = [p[0] for p in ports]
    print_success(f"Puertos abiertos: {Colors.BOLD}{', '.join(port_list)}{Colors.ENDC}")
    return ports

# ─── FASE 2: Escaneo Profundo de Servicios ────────────────────────

def deep_service_scan(ip, ports):
    """Escaneo detallado de versiones y scripts en los puertos encontrados."""
    print(f"\n{Colors.BOLD}── FASE 2: Detección de Versiones y Scripts ──{Colors.ENDC}")
    
    port_str = ",".join([p[0] for p in ports])
    print_status(f"Escaneando servicios en puertos: {port_str}")
    print_status("Esto puede tardar 30-60 segundos...")
    
    stdout = _run_nmap(["-sCV", "-p", port_str, "-n", "-Pn"], ip)
    if not stdout:
        return ports  # Devolver los puertos básicos si falla
    
    # Parsear resultados detallados
    detailed = re.findall(
        r'^(\d+)/tcp\s+open\s+(\S+)\s*(.*?)$', 
        stdout, re.MULTILINE
    )
    
    if detailed:
        print_success("Resultados detallados:\n")
        for port, service, version in detailed:
            version = version.strip()
            if version:
                sys.stdout.buffer.write(
                    f"  {Colors.OKGREEN}[{port}]{Colors.ENDC} {service} → {Colors.BOLD}{version}{Colors.ENDC}\n".encode('utf-8')
                )
            else:
                sys.stdout.buffer.write(
                    f"  {Colors.OKGREEN}[{port}]{Colors.ENDC} {service}\n".encode('utf-8')
                )
            sys.stdout.buffer.flush()
        return detailed
    
    return ports

# ─── FASE 3: Sugerencias Inteligentes ─────────────────────────────

def suggest_next_steps(ip, ports):
    """Sugiere los próximos pasos según los servicios encontrados."""
    print(f"\n{Colors.BOLD}── FASE 3: Análisis Inteligente y Próximos Pasos ──{Colors.ENDC}")
    
    port_numbers = [p[0] for p in ports]
    services_raw = " ".join([p[1] if len(p) > 1 else "" for p in ports])
    versions_raw = " ".join([p[2] if len(p) > 2 else "" for p in ports])
    all_info = (services_raw + " " + versions_raw).lower()
    
    suggestions = []
    
    # Web
    web_ports = [p for p in port_numbers if p in ('80', '443', '8080', '8000', '8443', '8888', '3000', '5000')]
    if web_ports:
        suggestions.append(("🌐 Servidor Web detectado", [
            f"Farei_0x.py fuzz {ip}",
            f"Abrir navegador: http://{ip}:{web_ports[0]}",
            f"Ctrl+U para ver código fuente",
            f"nikto -host {ip} -port {','.join(web_ports)}"
        ]))
    
    # SMB
    if '445' in port_numbers or '139' in port_numbers:
        suggestions.append(("📁 SMB/Samba detectado", [
            f"smbclient -L //{ip}/ -N",
            f"crackmapexec smb {ip} -u '' -p '' --shares",
            f"enum4linux -a {ip}"
        ]))
    
    # SSH
    if '22' in port_numbers:
        suggestions.append(("🔑 SSH detectado", [
            f"Si tenés credenciales: ssh user@{ip}",
            f"Fuerza bruta: hydra -l admin -P rockyou.txt ssh://{ip}"
        ]))
    
    # Active Directory / Kerberos
    if '88' in port_numbers or '389' in port_numbers or '636' in port_numbers:
        suggestions.append(("🏰 Active Directory / Kerberos detectado", [
            f"Farei_0x.py ad {ip} DOMINIO.LOCAL",
            f"crackmapexec smb {ip} -u '' -p '' --users",
            f"ldapsearch -x -H ldap://{ip} -b 'DC=dominio,DC=local'"
        ]))
    
    # FTP
    if '21' in port_numbers:
        suggestions.append(("📂 FTP detectado", [
            f"ftp {ip} (probar anonymous:anonymous)",
            f"Fuerza bruta: hydra -l admin -P rockyou.txt ftp://{ip}"
        ]))
    
    # MySQL / MSSQL / PostgreSQL
    db_ports = {'3306': 'MySQL', '1433': 'MSSQL', '5432': 'PostgreSQL', '27017': 'MongoDB'}
    for port, name in db_ports.items():
        if port in port_numbers:
            suggestions.append((f"🗄️ {name} detectado", [
                f"Intentar acceso sin credenciales",
                f"Fuerza bruta: hydra -l root -P rockyou.txt {ip} {name.lower()}"
            ]))
    
    # RDP
    if '3389' in port_numbers:
        suggestions.append(("🖥️ RDP (Escritorio Remoto) detectado", [
            f"xfreerdp /u:admin /p:password /v:{ip}",
            f"Probar credenciales por defecto"
        ]))
    
    # WinRM
    if '5985' in port_numbers or '5986' in port_numbers:
        suggestions.append(("⚡ WinRM detectado", [
            f"evil-winrm -i {ip} -u usuario -p password",
            f"crackmapexec winrm {ip} -u user -p pass"
        ]))
    
    # DNS
    if '53' in port_numbers:
        suggestions.append(("🌍 DNS detectado", [
            f"dig axfr @{ip} dominio.local",
            f"dnsrecon -d dominio.local -n {ip}"
        ]))
    
    # Versiones específicas con CVEs conocidos
    version_checks = [
        ("apache 2.4.49", "CVE-2021-41773 (Path Traversal + RCE)"),
        ("apache 2.4.50", "CVE-2021-42013 (Path Traversal + RCE)"),
        ("vsftpd 2.3.4", "CVE-2011-2523 (Backdoor)"),
        ("proftpd 1.3.5", "CVE-2015-3306 (mod_copy RCE)"),
        ("openssh 7.2", "CVE-2016-6210 (User Enumeration)"),
        ("iis 6.0", "CVE-2017-7269 (Buffer Overflow RCE)"),
        ("tomcat", "Manager panel: /manager/html (admin:admin)"),
        ("webmin", "CVE-2019-15107 (RCE sin autenticación)"),
        ("exchange", "ProxyLogon / ProxyShell"),
        ("elasticsearch", "CVE-2015-1427 (RCE)"),
        ("jenkins", "Script Console: /script (RCE)"),
        ("redis", "Acceso sin autenticación: redis-cli -h"),
    ]
    
    for keyword, cve_info in version_checks:
        if keyword in all_info:
            suggestions.append((f"☢️ VULNERABILIDAD CONOCIDA: {cve_info}", [
                f"Farei_0x.py cve \"{keyword}\""
            ]))
    
    if suggestions:
        for title, cmds in suggestions:
            print(f"\n  {Colors.WARNING}{title}{Colors.ENDC}")
            for cmd in cmds:
                sys.stdout.buffer.write(f"    {Colors.OKCYAN}→{Colors.ENDC} {cmd}\n".encode('utf-8'))
                sys.stdout.buffer.flush()
    else:
        print_status("No se detectaron servicios comunes conocidos. Investigá manualmente.")
    
    # Sugerir escaneo UDP
    print(f"\n  {Colors.WARNING}🔊 Sugerencia: Escaneo UDP (servicios ocultos){Colors.ENDC}")
    print(f"    {Colors.OKCYAN}→{Colors.ENDC} nmap -sU --top-ports 20 -n -Pn {ip}")

# ─── Función Principal ────────────────────────────────────────────

def run(ip):
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO RECON v2.0 (Obsidian Tier){Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    if not _check_nmap():
        return
    
    db.add_host(ip)
    
    # FASE 1: Escaneo rápido
    ports = fast_port_scan(ip)
    if not ports:
        return
    
    # Guardar puertos básicos en BD
    for port, service in ports:
        if port in ('80', '443', '8080', '8000', '8443'): service = 'http'
        db.add_port(ip, int(port), service)
    
    # FASE 2: Escaneo profundo de versiones
    detailed_ports = deep_service_scan(ip, ports)
    
    # Actualizar BD con versiones detalladas
    for entry in detailed_ports:
        if len(entry) >= 3 and entry[2].strip():
            port_num = int(entry[0])
            full_service = f"{entry[1]} {entry[2].strip()}"
            db.add_port(ip, port_num, full_service)
    
    # FASE 3: Sugerencias inteligentes
    suggest_next_steps(ip, detailed_ports)
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print_success(f"Reconocimiento completo. {len(ports)} puertos guardados en la Base de Datos.")
    print_status("Ejecutá 'Farei_0x.py report' para ver el estado completo.")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
