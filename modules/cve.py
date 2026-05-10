import urllib.parse
import urllib.request
import json

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def run(service_name):
    print(f"{Colors.OKCYAN}[*] Módulo Auto-CVE activado para: {service_name}{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] Recordatorio: Mantén la base de datos de searchsploit actualizada (searchsploit -u){Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}[+] Comando de búsqueda local (Exploit-DB):{Colors.ENDC}")
    print(f"    searchsploit \"{service_name}\"")
    
    # Integración con GitHub API
    print(f"\n{Colors.OKCYAN}[*] Consultando API REST de GitHub en busca de PoCs/Exploits 0-day...{Colors.ENDC}")
    query = urllib.parse.quote(f"{service_name} CVE Exploit OR PoC")
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data['total_count'] > 0:
                print(f"{Colors.OKGREEN}[+] ¡Repositorios encontrados! Mostrando los 3 más votados:{Colors.ENDC}")
                for i, repo in enumerate(data['items'][:3]):
                    print(f"\n    ⭐ Estrellas: {repo['stargazers_count']}")
                    print(f"    🔗 Enlace: {repo['html_url']}")
                    print(f"    💻 Comando: git clone {repo['clone_url']}")
            else:
                print(f"{Colors.WARNING}[-] GitHub API no arrojó resultados claros de repositorios para este servicio.{Colors.ENDC}")
                
    except urllib.error.URLError as e:
        print(f"{Colors.FAIL}[-] Error de red al consultar GitHub: {e}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error parseando datos de GitHub: {e}{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}[+] Búsqueda en Google (Dorks para NIST y CVE-Details):{Colors.ENDC}")
    print(f"    site:cvedetails.com \"{service_name}\" exploit")
    print(f"    site:nvd.nist.gov \"{service_name}\" vulnerability")
