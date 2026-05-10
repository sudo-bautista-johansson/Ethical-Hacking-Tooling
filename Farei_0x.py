#!/usr/bin/env python3
import argparse
import datetime
import sys
import os
from core import db

class Colors:
    HEADER = '\033[95m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=======================================")
    print("        BAUTY-CORE ARSENAL V2          ")
    print("=======================================")
    print(f"{Colors.ENDC}")

def handle_report(args):
    print(f"{Colors.OKCYAN}[*] Generando Súper-Reporte a partir de la Base de Datos...{Colors.ENDC}")
    state = db.get_all_state()
    report_file = "Bauty_Report.md"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🏴‍☠️ Reporte de Inteligencia CTF - Farei_0x\n")
        f.write(f"**Generado el:** {current_time}\n")
        f.write("---\n\n")
        
        f.write("## 1. 🖥️ Superficie de Ataque (Hosts)\n")
        if not state.get("hosts"): f.write("> No se registraron hosts en esta sesión.\n")
        else:
            for h in state["hosts"]: f.write(f"- 🟢 **IP:** `{h[0]}` (Fecha: {h[2]})\n")
            
        f.write("\n## 2. 🚪 Vectores de Red (Puertos)\n")
        if not state.get("ports"): f.write("> No se registraron puertos.\n")
        else:
            f.write("| IP | Puerto | Servicio | Estado |\n|---|---|---|---|\n")
            for p in state["ports"]: f.write(f"| `{p[1]}` | **{p[2]}** | {p[3]} | {p[4]} |\n")
            
        f.write("\n## 3. 🌐 Mapeo Web (Fuzzing)\n")
        if not state.get("directories"): f.write("> No se registró fuzzing exitoso.\n")
        else:
            f.write("| URL Base | Ruta Descubierta | Tamaño (Bytes) | Status HTTP |\n|---|---|---|---|\n")
            for d in state["directories"]: f.write(f"| {d[1]} | **/{d[2]}** | {d[3]} | {d[4]} |\n")

        f.write("\n## 4. ☢️ Arsenal y Exploits (CVEs)\n")
        if not state.get("exploits"): f.write("> No se buscaron exploits en esta sesión.\n")
        else:
            f.write("| Servicio Vulnerable | Link del Exploit (GitHub) | Detalles |\n|---|---|---|\n")
            for e in state["exploits"]: f.write(f"| **{e[1]}** | [Link]({e[2]}) | {e[3]} |\n")

        f.write("\n## 5. 🗝️ Credenciales y Hashes\n")
        if not state.get("creds"): f.write("> No se extrajeron credenciales.\n")
        else:
            f.write("| Origen | Usuario | Credencial/Hash | Tipo |\n|---|---|---|---|\n")
            for c in state["creds"]: f.write(f"| `{c[1]}` | {c[2]} | `{c[3]}` | {c[4]} |\n")
            
        f.write("\n## 6. 🏰 Infraestructura Active Directory\n")
        if not state.get("ad_findings"): f.write("> No se encontraron vulnerabilidades de dominio.\n")
        else:
            f.write("| Objetivo | Vulnerabilidad | Cuenta Afectada |\n|---|---|---|\n")
            for a in state["ad_findings"]: f.write(f"| `{a[1]}` | **{a[2]}** | `{a[3]}` |\n")
        
        f.write("\n---\n> Reporte de Inteligencia Total generado automáticamente por Farei_0x Core.\n")
            
    print(f"{Colors.OKGREEN}[+] Súper-Reporte generado exitosamente en: {report_file}{Colors.ENDC}")

def main():
    # Inicializar Base de Datos siempre al arrancar
    db.init_db()

    parser = argparse.ArgumentParser(description="Bauty-Core: Framework Central de CTFs")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando Recon
    parser_recon = subparsers.add_parser("recon", help="Escaneo inteligente de puertos (3 fases)")
    parser_recon.add_argument("ip", help="IP objetivo")
    
    # Comando Fuzz
    parser_fuzz = subparsers.add_parser("fuzz", help="Fuzzing web de directorios o VHosts")
    parser_fuzz.add_argument("ip", nargs="?", help="IP objetivo (opcional si ya se hizo recon)")
    parser_fuzz.add_argument("-w", "--wordlist", default="/usr/share/wordlists/dirb/common.txt")
    parser_fuzz.add_argument("--vhost", action="store_true", help="Modo VHost: fuzzear subdominios via cabecera Host")
    parser_fuzz.add_argument("--domain", help="Dominio base para VHost fuzzing (ej: target.htb)")
    
    # Comando Payload
    parser_payload = subparsers.add_parser("payload", help="Generador de reverse shells + TTY upgrade")
    parser_payload.add_argument("ip", nargs="?", help="Tu IP atacante")
    parser_payload.add_argument("port", nargs="?", help="Tu puerto de escucha")
    parser_payload.add_argument("--base64", action="store_true", help="Codifica la shell en Base64 para evadir WAFs")
    parser_payload.add_argument("--urlencode", action="store_true", help="Aplica URL-Encode a la shell")
    parser_payload.add_argument("--upgrade", action="store_true", help="Muestra pasos para upgrade de shell a TTY completa")
    
    # Comando Crypto
    parser_crypto = subparsers.add_parser("crypto", help="Desencriptador: Base64/32/Hex/ROT (recursivo)")
    parser_crypto.add_argument("string", help="Cadena a desencriptar")

    # Comando Encoder
    parser_encoder = subparsers.add_parser("encoder", help="Cifrados clásicos: Morse, Atbash, Vigenere, Rail Fence")
    parser_encoder.add_argument("string", help="Cadena a decodificar")
    parser_encoder.add_argument("--key", help="Clave para Vigenere (opcional)")

    # Comando Hashes
    parser_hashes = subparsers.add_parser("hashes", help="Extractor de hashes (17 tipos, incluyendo Kerberos)")
    parser_hashes.add_argument("file", help="Ruta al archivo (ej. /etc/shadow, secretsdump.txt)")

    # Comando AD (Active Directory)
    parser_ad = subparsers.add_parser("ad", help="Comandos de automatización para Active Directory")
    parser_ad.add_argument("dc_ip", nargs="?", help="IP del Domain Controller (Requerido si no usas --parse)")
    parser_ad.add_argument("domain", nargs="?", help="Nombre del dominio (Requerido si no usas --parse)")
    parser_ad.add_argument("--parse", help="Ruta a un archivo JSON de BloodHound para parsear automáticamente")

    # Comando SMB
    parser_smb = subparsers.add_parser("smb", help="Enumeración completa de SMB (null session + creds)")
    parser_smb.add_argument("ip", help="IP objetivo")
    parser_smb.add_argument("-u", "--user", help="Usuario (opcional)", default=None)
    parser_smb.add_argument("-p", "--password", help="Contraseña (opcional)", default=None)

    # Comando SQLi
    parser_sqli = subparsers.add_parser("sqli", help="Payloads SQLi + comandos sqlmap")
    parser_sqli.add_argument("--url", help="URL objetivo (ej: http://10.10.10.X/page?id=1)", default=None)

    # Comando PrivEsc
    parser_privesc = subparsers.add_parser("privesc", help="Vectores de escalada de privilegios Linux/Windows")
    parser_privesc.add_argument("--os", choices=["linux", "windows"], default="linux",
                                help="Sistema operativo objetivo (default: linux)")

    # Comando CVE
    parser_cve = subparsers.add_parser("cve", help="Auto-búsqueda de exploits y CVEs (NVD + GitHub)")
    parser_cve.add_argument("service", help="Nombre del servicio o CVE-ID (ej. 'Apache 2.4.49' o 'CVE-2021-41773')")

    # Comando OSINT
    parser_osint = subparsers.add_parser("osint", help="OSINT pasivo: WHOIS, DNS, subdominios, dorks")
    parser_osint.add_argument("domain", help="Dominio objetivo (ej: target.htb)")

    # Comando AI
    parser_ai = subparsers.add_parser("ai", help="Asistente interactivo: Chatbot ofensivo con memoria (Obsidian Tier)")

    # Comando Report
    subparsers.add_parser("report", help="Genera reporte Markdown completo desde la Base de Datos")

    args = parser.parse_args()

    print_banner()

    if args.command == "recon":
        from modules import recon
        recon.run(args.ip)
    elif args.command == "fuzz":
        from modules import fuzzer
        target_ip = args.ip
        if not target_ip:
            state = db.get_all_state()
            ips_with_web = list(set([p[1] for p in state["ports"] if p[2] in (80, 443, 8080)]))
            if ips_with_web:
                target_ip = ips_with_web[0]
                print(f"{Colors.WARNING}[!] Auto-Fuzz: Seleccionando objetivo de la DB -> {target_ip}{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] No se proveyó IP y no hay servicios web en DB.{Colors.ENDC}")
                sys.exit(1)
        url = f"http://{target_ip}"
        if args.vhost:
            if not args.domain:
                print(f"{Colors.FAIL}[-] El modo --vhost requiere especificar --domain (ej: --domain target.htb){Colors.ENDC}")
                sys.exit(1)
            fuzzer.run(url, args.wordlist, mode="vhost", domain=args.domain)
        else:
            fuzzer.run(url, args.wordlist, mode="dir")
    elif args.command == "payload":
        if args.upgrade:
            from modules import shell_upgrade
            ip = args.ip or "TU_IP"
            port = args.port or "4444"
            shell_upgrade.run(ip, port)
        else:
            if not args.ip or not args.port:
                print(f"{Colors.FAIL}[-] Error: 'payload' requiere IP y PUERTO (o usa --upgrade para TTY){Colors.ENDC}")
                sys.exit(1)
            from modules import payloads
            payloads.run(args.ip, args.port, use_base64=args.base64, use_urlencode=args.urlencode)
    elif args.command == "crypto":
        from modules import crypto
        crypto.run(args.string)
    elif args.command == "encoder":
        from modules import encoder
        encoder.run(args.string, key=args.key)
    elif args.command == "hashes":
        from modules import hashes
        hashes.run(args.file)
    elif args.command == "ad":
        if not args.parse and (not args.dc_ip or not args.domain):
            print(f"{Colors.FAIL}[-] Error: Debes proveer 'dc_ip' y 'domain' si no estás usando '--parse'.{Colors.ENDC}")
            sys.exit(1)
        from modules import ad
        ad.run(args.dc_ip, args.domain, args.parse)
    elif args.command == "smb":
        from modules import smb
        smb.run(args.ip, user=args.user, password=args.password)
    elif args.command == "sqli":
        from modules import sqli
        sqli.run(url=args.url)
    elif args.command == "privesc":
        from modules import privesc
        privesc.run(args.os)
    elif args.command == "cve":
        from modules import cve
        cve.run(args.service)
    elif args.command == "osint":
        from modules import osint
        osint.run(args.domain)
    elif args.command == "ai":
        from modules import ai
        ai.run()
    elif args.command == "report":
        handle_report(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
