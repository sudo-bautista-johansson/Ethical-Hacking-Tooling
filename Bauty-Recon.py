#!/usr/bin/env python3
import subprocess
import argparse
import os
import re
import concurrent.futures

# Colores ANSI para una terminal con estilo
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(msg):
    print(f"{Colors.OKBLUE}[*]{Colors.ENDC} {msg}")

def print_success(msg):
    print(f"{Colors.OKGREEN}[+]{Colors.ENDC} {msg}")

def print_warning(msg):
    print(f"{Colors.WARNING}[!]{Colors.ENDC} {msg}")

def print_error(msg):
    print(f"{Colors.FAIL}[-]{Colors.ENDC} {msg}")

def run_cmd(cmd, outfile=None):
    """Ejecuta un comando en la shell. Si se da outfile, guarda el output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if outfile:
            with open(outfile, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n--- ERRORES ---\n")
                    f.write(result.stderr)
        return result.stdout
    except Exception as e:
        print_error(f"Fallo al ejecutar: {cmd}\nExcepción: {e}")
        return ""

def fast_port_scan(ip):
    """Escaneo veloz de todos los puertos usando Nmap."""
    print_status(f"Iniciando escaneo rápido (65535 puertos) contra {ip}...")
    cmd = f"nmap -p- --min-rate 5000 -T4 -n -Pn {ip}"
    output = run_cmd(cmd)
    
    # Extraer puertos con Regex
    ports = re.findall(r'^(\d+)/tcp\s+open', output, re.MULTILINE)
    return ports

def service_enum(ip, port, outdir):
    """Lógica inteligente de enumeración según el puerto."""
    outfile = os.path.join(outdir, f"port_{port}_enum.txt")
    
    if port in ['80', '443', '8080']:
        print_status(f"Puerto WEB detectado ({port}). Lanzando dirb en segundo plano...")
        protocol = "https" if port == '443' else "http"
        # Usamos wordlist común de dirb, puedes cambiarla por SecLists
        cmd = f"dirb {protocol}://{ip}:{port}/ /usr/share/wordlists/dirb/common.txt -r -w"
        run_cmd(cmd, outfile)
        print_success(f"Fuzzing web en {port} completado. Resultados en {outfile}")
        
    elif port == '445':
        print_status(f"Puerto SMB detectado (445). Probando acceso anónimo y enum4linux...")
        cmd_smb = f"smbclient -N -L //'{ip}'"
        cmd_enum = f"enum4linux -a {ip}"
        
        out1 = run_cmd(cmd_smb)
        out2 = run_cmd(cmd_enum)
        
        with open(outfile, 'w') as f:
            f.write("=== SMBCLIENT ANÓNIMO ===\n")
            f.write(out1 + "\n\n")
            f.write("=== ENUM4LINUX ===\n")
            f.write(out2)
        print_success(f"Enumeración SMB completada. Resultados en {outfile}")
        
    elif port == '21':
        print_status(f"Puerto FTP detectado (21). Comprobando login anónimo...")
        cmd = f"nmap -p 21 --script ftp-anon {ip}"
        run_cmd(cmd, outfile)
        print_success(f"Chequeo FTP completado. Resultados en {outfile}")
        
    else:
        # Para el resto de puertos, hacemos un escaneo de versión básico de Nmap
        print_status(f"Analizando versión del puerto {port}...")
        cmd = f"nmap -p {port} -sV -sC -Pn {ip}"
        run_cmd(cmd, outfile)
        print_success(f"Escaneo de puerto {port} completado. Resultados en {outfile}")

def main():
    parser = argparse.ArgumentParser(description="Bauty-Recon: Nmap automatizado para CTFs")
    parser.add_argument("ip", help="Dirección IP objetivo")
    args = parser.parse_args()
    
    ip = args.ip
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=======================================")
    print("      BAUTY-RECON (Auto-Recon)         ")
    print("=======================================")
    print(f"{Colors.ENDC}")
    
    # Crear directorio de trabajo
    outdir = f"recon_{ip.replace('.', '_')}"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print_success(f"Directorio creado: {outdir}/")
    else:
        print_warning(f"El directorio {outdir}/ ya existe. Se sobrescribirán archivos.")
        
    # 1. Encontrar puertos abiertos rápidamente
    open_ports = fast_port_scan(ip)
    
    if not open_ports:
        print_error(f"No se encontraron puertos abiertos en {ip} o el host está caído.")
        return
        
    print_success(f"Puertos abiertos encontrados: {', '.join(open_ports)}")
    
    # 2. Enumerar los servicios concurrentemente para ganar velocidad
    print_status("Iniciando escaneos específicos por servicio...")
    
    # Usamos ThreadPoolExecutor para lanzar las tareas en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(service_enum, ip, port, outdir) for port in open_ports]
        concurrent.futures.wait(futures)
        
    print(f"\n{Colors.HEADER}{Colors.BOLD}>>> RECONOCIMIENTO COMPLETADO <<<{Colors.ENDC}")
    print_success(f"Revisa la carpeta '{outdir}/' para ver todos los resultados.")

if __name__ == "__main__":
    main()
