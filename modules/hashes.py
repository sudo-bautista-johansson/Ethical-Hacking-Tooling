import re
import sys
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def identify_hash(h):
    if re.match(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$", h): return ("bcrypt", 3200)
    elif re.match(r"^\$6\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{86}$", h): return ("SHA512-Crypt", 1800)
    elif re.match(r"^\$1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}$", h): return ("MD5-Crypt", 500)
    elif re.match(r"^[a-fA-F0-9]{32}$", h): return ("MD5 / NTLM", "0 / 1000")
    elif re.match(r"^[a-fA-F0-9]{40}$", h): return ("SHA1", 100)
    elif re.match(r"^[a-fA-F0-9]{64}$", h): return ("SHA256", 1400)
    return ("Desconocido", "?")

def parse_file(filepath):
    results = []
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}[-] Error: El archivo '{filepath}' no existe.{Colors.ENDC}")
        return results

    print(f"{Colors.OKCYAN}[*] Parseando archivo (Ignorando errores de codificación binaria)...{Colors.ENDC}")
    hash_pattern = re.compile(r"(\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}|\$6\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{86}|\$1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}|[a-fA-F0-9]{32,64})")
    
    try:
        # Usamos errors='ignore' para evitar crashear si le pasamos un archivo SQLite o binario
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                matches = hash_pattern.findall(line)
                for m in matches:
                    if not re.match(r"^\d+$", m): results.append(("?", m))
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error crítico al leer: {e}{Colors.ENDC}")
        
    return list(set(results))

def run(filepath):
    results = parse_file(filepath)
    if not results:
        print(f"{Colors.WARNING}[-] No se encontraron hashes válidos en el archivo.{Colors.ENDC}")
        return
        
    print(f"\n{Colors.OKGREEN}[+] HASHES ENCONTRADOS:{Colors.ENDC}\n" + "-"*50)
    out_file = "hashes_extraidos.txt"
    try:
        from core import db
        with open(out_file, 'w', encoding='utf-8') as f_out:
            for user, hash_val in results:
                tipo, hashcat_mode = identify_hash(hash_val)
                print(f"Hash: {hash_val[:30]}... | Tipo: {tipo} | Modo: {hashcat_mode}")
                f_out.write(f"{hash_val}\n")
                db.add_cred(filepath, "ExtractedUser", hash_val, tipo)
        print(f"\n{Colors.OKCYAN}[*] Hashes guardados limpios en '{out_file}' y en la DB.{Colors.ENDC}")
        modos = set([identify_hash(h)[1] for _, h in results])
        for modo in modos:
            if modo != "?": 
                print(f"{Colors.WARNING}Sugerencia: hashcat -m {modo} -a 0 {out_file} /usr/share/wordlists/rockyou.txt{Colors.ENDC}")
    except PermissionError:
        print(f"{Colors.FAIL}[-] Error: No hay permisos para escribir en el directorio actual.{Colors.ENDC}")
