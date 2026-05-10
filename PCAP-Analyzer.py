#!/usr/bin/env python3
import sys
import argparse

# Opcional: Instalar scapy -> pip install scapy
try:
    from scapy.all import rdpcap, TCP, UDP, Raw
except ImportError:
    print("[-] Error: Scapy no está instalado.")
    print("[-] Por favor instala scapy: pip install scapy")
    sys.exit(1)

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def analyze_pcap(filepath):
    print(f"{Colors.OKCYAN}[*] Cargando PCAP (puede tardar en archivos grandes): {filepath}{Colors.ENDC}")
    try:
        packets = rdpcap(filepath)
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error leyendo el archivo PCAP: {e}{Colors.ENDC}")
        return

    print(f"[+] PCAP cargado. Total de paquetes: {len(packets)}\n")
    print(f"{Colors.WARNING}--- EXTRACCIÓN DE CREDENCIALES (HTTP / FTP / TELNET) ---{Colors.ENDC}")

    # Palabras clave comunes usadas en peticiones de autenticación en texto plano
    auth_keywords = [b"USER ", b"PASS ", b"login=", b"username=", b"password=", b"pwd=", b"Authorization: Basic"]
    
    found_creds = []

    for pkt in packets:
        if pkt.haslayer(Raw):
            payload = pkt[Raw].load
            
            # Buscar keywords
            for kw in auth_keywords:
                if kw in payload:
                    try:
                        decoded_payload = payload.decode('utf-8', errors='ignore').strip()
                        # Si es muy largo, cortarlo para no saturar la pantalla
                        if len(decoded_payload) > 150:
                             decoded_payload = decoded_payload[:150] + "..."
                        
                        # Guardar paquete único basado en payload
                        if decoded_payload not in found_creds:
                            found_creds.append(decoded_payload)
                    except:
                        pass

    if found_creds:
        for cred in found_creds:
            print(f"{Colors.OKGREEN}[+] Posible Credencial: {cred}{Colors.ENDC}")
    else:
        print("[-] No se encontraron credenciales en texto plano aparentes.")

    # Buscar también posibles flags enviadas en el tráfico
    print(f"\n{Colors.WARNING}--- BÚSQUEDA DE FLAGS (THM{{}} / HTB{{}}) ---{Colors.ENDC}")
    flags_found = set()
    for pkt in packets:
         if pkt.haslayer(Raw):
             payload = pkt[Raw].load.decode('utf-8', errors='ignore')
             import re
             matches = re.findall(r'(THM{[^}]+}|HTB{[^}]+})', payload)
             for m in matches:
                 flags_found.add(m)
                 
    if flags_found:
         for flag in flags_found:
              print(f"{Colors.OKGREEN}>> FLAG ENCONTRADA EN TRÁFICO: {flag} <<{Colors.ENDC}")
    else:
         print("[-] No se encontraron flags en el tráfico.")

def main():
    parser = argparse.ArgumentParser(description="Analizador de Tráfico PCAP Rápido")
    parser.add_argument("pcap_file", help="Ruta al archivo .pcap o .pcapng")
    args = parser.parse_args()

    analyze_pcap(args.pcap_file)

if __name__ == "__main__":
    main()
