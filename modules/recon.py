import subprocess
import os
import re
from core import db

class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_status(msg): print(f"{Colors.OKBLUE}[*]{Colors.ENDC} {msg}")
def print_success(msg): print(f"{Colors.OKGREEN}[+]{Colors.ENDC} {msg}")
def print_error(msg): print(f"{Colors.FAIL}[-]{Colors.ENDC} {msg}")
def print_warning(msg): print(f"{Colors.WARNING}[!]{Colors.ENDC} {msg}")

def fast_port_scan(ip):
    print_status(f"Nmap Fast Scan (65535 puertos) contra {ip}...")
    try:
        # Check if nmap is installed
        subprocess.run(["nmap", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        result = subprocess.run(["nmap", "-p-", "--min-rate", "5000", "-T4", "-n", "-Pn", ip], 
                                capture_output=True, text=True, check=False)
        return re.findall(r'^(\d+)/tcp\s+open\s+([a-zA-Z0-9?-]+)', result.stdout, re.MULTILINE)
    except FileNotFoundError:
        print_error("ERROR FATAL: 'nmap' no está instalado o no está en el PATH.")
        print_warning("Si estás en Windows puro, instala Nmap o corre Farei_0x dentro de WSL/Kali Linux.")
        return None
    except Exception as e:
        print_error(f"Error inesperado ejecutando Nmap: {e}")
        return None

def run(ip):
    db.add_host(ip)
    ports = fast_port_scan(ip)
    
    if ports is None:
        return # Fallo la ejecución de nmap
        
    if not ports:
        print_warning(f"No se encontraron puertos abiertos en {ip}. El host podría estar ignorando pings (-Pn no fue suficiente) o bloqueando el escaneo.")
        return
        
    print_success(f"Puertos abiertos encontrados: {', '.join([p[0] for p in ports])}")
    
    for port, service in ports:
        if port in ['80', '443', '8080', '8000', '8443']: service = 'http'
        db.add_port(ip, int(port), service)
        print_success(f"-> Puerto {port} ({service}) guardado en la Base de Datos.")
        
    print_status("Reconocimiento guardado en el estado del framework.")
