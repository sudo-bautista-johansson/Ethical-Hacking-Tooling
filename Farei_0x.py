#!/usr/bin/env python3
import argparse
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

def handle_recon(args):
    print(f"{Colors.OKCYAN}[*] Módulo Recon activado para: {args.ip}{Colors.ENDC}")
    db.add_host(args.ip)
    
    # Aquí en el futuro importaremos modules.recon y ejecutaremos la lógica.
    # Por ahora simulamos que encontramos un puerto y lo guardamos.
    print("[*] Ejecutando Nmap (Simulado)...")
    db.add_port(args.ip, 80, "http")
    db.add_port(args.ip, 22, "ssh")
    print(f"{Colors.OKGREEN}[+] Reconocimiento finalizado. Puertos guardados en BD.{Colors.ENDC}")

def handle_fuzz(args):
    # Si no se provee IP, buscar en BD las IPs que tienen puerto 80/443
    if not args.ip:
        state = db.get_all_state()
        ips_with_web = list(set([p[1] for p in state["ports"] if p[2] in (80, 443, 8080)]))
        if not ips_with_web:
            print(f"{Colors.FAIL}[-] No se proveyó IP y no hay servicios web en la base de datos.{Colors.ENDC}")
            return
        target_ip = ips_with_web[0]
        print(f"{Colors.WARNING}[!] Auto-Fuzz: Seleccionando objetivo de la DB -> {target_ip}{Colors.ENDC}")
    else:
        target_ip = args.ip

    print(f"{Colors.OKCYAN}[*] Módulo Fuzzer activado para: {target_ip}{Colors.ENDC}")
    # Aquí llamaremos a modules.fuzzer

def handle_report(args):
    print(f"{Colors.OKCYAN}[*] Generando reporte a partir de la Base de Datos...{Colors.ENDC}")
    state = db.get_all_state()
    
    report_file = "Bauty_Report.md"
    with open(report_file, 'w') as f:
        f.write("# Reporte Final de CTF\n\n")
        f.write("## 1. Hosts Descubiertos\n")
        for h in state["hosts"]:
            f.write(f"- IP: **{h[0]}** (Escaneado el: {h[2]})\n")
            
        f.write("\n## 2. Puertos Abiertos\n")
        for p in state["ports"]:
            f.write(f"- IP: {p[1]} | Puerto: **{p[2]}** | Servicio: {p[3]}\n")
            
        f.write("\n## 3. Credenciales Extraídas\n")
        for c in state["creds"]:
            f.write(f"- IP: {c[1]} | User: {c[2]} | Pass/Hash: `{c[3]}` | Tipo: {c[4]}\n")
            
    print(f"{Colors.OKGREEN}[+] Reporte generado exitosamente en: {report_file}{Colors.ENDC}")

def main():
    # Inicializar Base de Datos siempre al arrancar
    db.init_db()

    parser = argparse.ArgumentParser(description="Bauty-Core: Framework Central de CTFs")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Comando Recon
    parser_recon = subparsers.add_parser("recon", help="Escaneo inteligente de puertos")
    parser_recon.add_argument("ip", help="IP objetivo")
    
    # Comando Fuzz
    parser_fuzz = subparsers.add_parser("fuzz", help="Fuzzing web de directorios")
    parser_fuzz.add_argument("--ip", help="IP objetivo (opcional si ya se hizo recon)")
    parser_fuzz.add_argument("-w", "--wordlist", default="/usr/share/wordlists/dirb/common.txt")
    
    # Comando Payload
    parser_payload = subparsers.add_parser("payload", help="Generador de reverse shells")
    parser_payload.add_argument("ip", help="Tu IP atacante")
    parser_payload.add_argument("port", help="Tu puerto de escucha")
    
    # Comando Crypto
    parser_crypto = subparsers.add_parser("crypto", help="Desencriptador de fuerza bruta criptográfica")
    parser_crypto.add_argument("string", help="Cadena a desencriptar")

    # Comando Hashes
    parser_hashes = subparsers.add_parser("hashes", help="Extractor de hashes desde archivos")
    parser_hashes.add_argument("file", help="Ruta al archivo (ej. /etc/shadow)")

    # Comando AD (Active Directory)
    parser_ad = subparsers.add_parser("ad", help="Comandos de automatización para Active Directory")
    parser_ad.add_argument("dc_ip", help="IP del Domain Controller")
    parser_ad.add_argument("domain", help="Nombre del dominio (ej. corp.local)")
    parser_ad.add_argument("--parse", help="Ruta a un archivo JSON de BloodHound para parsear automáticamente")

    # Comando CVE
    parser_cve = subparsers.add_parser("cve", help="Auto-búsqueda de exploits y CVEs")
    parser_cve.add_argument("service", help="Nombre del servicio y versión (ej. 'Apache 2.4.49')")

    # Comando Report
    parser_report = subparsers.add_parser("report", help="Genera reporte en Markdown desde la BD")

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
        fuzzer.run(url, args.wordlist)
    elif args.command == "payload":
        from modules import payloads
        payloads.run(args.ip, args.port)
    elif args.command == "crypto":
        from modules import crypto
        crypto.run(args.string)
    elif args.command == "hashes":
        from modules import hashes
        hashes.run(args.file)
    elif args.command == "ad":
        from modules import ad
        ad.run(args.dc_ip, args.domain, args.parse)
    elif args.command == "cve":
        from modules import cve
        cve.run(args.service)
    elif args.command == "report":
        handle_report(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
