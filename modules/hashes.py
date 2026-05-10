import re
import sys
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ─── Base de Datos de Hashes (Obsidian Tier) ──────────────────────
# Ordenados de más específico a menos específico para evitar falsos positivos.

HASH_PATTERNS = [
    # Kerberos
    (r"^\$krb5asrep\$23\$.*", "Kerberos AS-REP", 18200),
    (r"^\$krb5tgs\$23\$.*", "Kerberos TGS (Kerberoast)", 13100),
    
    # Unix/Linux Crypt
    (r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$", "bcrypt", 3200),
    (r"^\$6\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{86}$", "SHA512-Crypt", 1800),
    (r"^\$5\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{43}$", "SHA256-Crypt", 7400),
    (r"^\$1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}$", "MD5-Crypt", 500),
    (r"^\$apr1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}$", "Apache APR1", 1600),
    (r"^\$P\$[a-zA-Z0-9./]{31}$", "PHPass (WordPress/Drupal)", 400),
    (r"^\$H\$[a-zA-Z0-9./]{31}$", "PHPass (phpBB)", 400),
    
    # Windows / NTLM
    (r"^[a-zA-Z0-9._-]+::\w+:[a-fA-F0-9]{16}:[a-fA-F0-9]{32}:[a-fA-F0-9]+$", "NTLMv2 (Net-NTLMv2)", 5600),
    (r"^[a-zA-Z0-9._-]+::\w+:[a-fA-F0-9]+:[a-fA-F0-9]{48}:[a-fA-F0-9]+$", "NTLMv1", 5500),
    
    # Base de datos
    (r"^\*[A-F0-9]{40}$", "MySQL 4.1+ (sha1)", 300),
    
    # Hashes puros (del más largo al más corto para evitar conflictos)
    (r"^[a-fA-F0-9]{128}$", "SHA-512", 1700),
    (r"^[a-fA-F0-9]{96}$", "SHA-384", 10800),
    (r"^[a-fA-F0-9]{64}$", "SHA-256", 1400),
    (r"^[a-fA-F0-9]{40}$", "SHA-1", 100),
    (r"^[a-fA-F0-9]{32}$", "MD5 / NTLM", "0 o 1000"),
]

def identify_hash(h):
    """Identifica el tipo de hash comparando contra la base de patrones."""
    h = h.strip()
    for pattern, name, mode in HASH_PATTERNS:
        if re.match(pattern, h):
            return (name, mode)
    return ("Desconocido", "?")

# ─── Parser Inteligente de Archivos ───────────────────────────────

def parse_file(filepath):
    """Extrae hashes de cualquier archivo, detectando formato user:hash."""
    results = []
    if not os.path.exists(filepath):
        print(f"{Colors.FAIL}[-] Error: El archivo '{filepath}' no existe.{Colors.ENDC}")
        return results

    print(f"{Colors.OKCYAN}[*] Parseando archivo: {filepath}{Colors.ENDC}")
    
    # Patrones de extracción (ordenados de más específico a más genérico)
    patterns = [
        # Kerberos tickets (AS-REP / Kerberoast)
        re.compile(r"(\$krb5(?:asrep|tgs)\$23\$[^\s:]+)"),
        # Formato user:hash (shadow, hashdump, secretsdump)
        re.compile(r"^([a-zA-Z0-9._$-]+):(\$[^\s:]+)"),
        # Formato user:uid:lm:ntlm (secretsdump NTDS.dit)
        re.compile(r"^([a-zA-Z0-9._$-]+):\d+:([a-fA-F0-9]{32}):([a-fA-F0-9]{32}):::?$"),
        # NTLMv2 responses (Responder / Inveigh)
        re.compile(r"^([a-zA-Z0-9._-]+::\w+:[a-fA-F0-9:]+)$"),
        # MySQL hashes
        re.compile(r"(\*[A-F0-9]{40})"),
        # PHPass (WordPress)
        re.compile(r"(\$[PH]\$[a-zA-Z0-9./]{31})"),
        # Unix crypt hashes
        re.compile(r"(\$(?:1|5|6|2[aby]|apr1)\$[^\s:]+)"),
        # Hashes hex puros (32-128 chars)
        re.compile(r"\b([a-fA-F0-9]{32,128})\b"),
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                for pattern in patterns:
                    match = pattern.search(line)
                    if match:
                        groups = match.groups()
                        if len(groups) == 3:
                            # Formato user:lm:ntlm (secretsdump)
                            user = groups[0]
                            lm_hash = groups[1]
                            ntlm_hash = groups[2]
                            # Ignorar LM si es vacío (aad3b435...)
                            if not lm_hash.startswith('aad3b435'):
                                results.append((user, lm_hash))
                            results.append((user, ntlm_hash))
                        elif len(groups) == 2:
                            # Formato user:hash
                            results.append((groups[0], groups[1]))
                        else:
                            # Hash solo
                            hash_val = groups[0]
                            if not re.match(r"^\d+$", hash_val):
                                results.append(("?", hash_val))
                        break  # Solo el primer patrón que matchea por línea
                        
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error crítico al leer: {e}{Colors.ENDC}")
    
    # Deduplicar manteniendo el orden
    seen = set()
    unique = []
    for user, h in results:
        if h not in seen:
            seen.add(h)
            unique.append((user, h))
    
    return unique

# ─── Función Principal ────────────────────────────────────────────

def run(filepath):
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO HASH CRACKER v2.0 (Obsidian Tier){Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    results = parse_file(filepath)
    if not results:
        print(f"{Colors.WARNING}[-] No se encontraron hashes válidos en el archivo.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.OKGREEN}[+] {len(results)} HASHES ENCONTRADOS:{Colors.ENDC}\n" + "─"*60)
    
    out_file = "hashes_extraidos.txt"
    hash_groups = {}  # Agrupar por tipo para sugerencias
    
    try:
        from core import db
        with open(out_file, 'w', encoding='utf-8') as f_out:
            for user, hash_val in results:
                tipo, hashcat_mode = identify_hash(hash_val)
                
                # Color según tipo
                if tipo == "Desconocido":
                    color = Colors.WARNING
                elif "NTLM" in tipo or "Kerberos" in tipo:
                    color = Colors.FAIL
                else:
                    color = Colors.OKGREEN
                
                user_display = f"{Colors.OKCYAN}{user}{Colors.ENDC}" if user != "?" else "?"
                hash_display = hash_val if len(hash_val) <= 50 else f"{hash_val[:50]}..."
                
                sys.stdout.buffer.write(
                    f"  {color}[{tipo}]{Colors.ENDC} {user_display} → {hash_display} (mode: {hashcat_mode})\n".encode('utf-8')
                )
                sys.stdout.buffer.flush()
                
                f_out.write(f"{hash_val}\n")
                db.add_cred(filepath, user if user != "?" else "ExtractedUser", hash_val, tipo)
                
                # Agrupar
                if hashcat_mode != "?":
                    mode_key = str(hashcat_mode)
                    if mode_key not in hash_groups:
                        hash_groups[mode_key] = tipo
        
        print(f"\n{'─'*60}")
        print(f"{Colors.OKCYAN}[*] Hashes guardados en '{out_file}' y en la Base de Datos.{Colors.ENDC}")
        
        # Sugerencias de cracking por tipo
        if hash_groups:
            print(f"\n{Colors.BOLD}── Comandos de Cracking Sugeridos ──{Colors.ENDC}\n")
            for mode, tipo in hash_groups.items():
                if " o " in str(mode):
                    # Manejar "0 o 1000" para MD5/NTLM
                    for m in str(mode).split(" o "):
                        m = m.strip()
                        sys.stdout.buffer.write(
                            f"  {Colors.WARNING}[{tipo} → mode {m}]{Colors.ENDC}\n".encode('utf-8')
                        )
                        sys.stdout.buffer.write(
                            f"  hashcat -m {m} -a 0 {out_file} /usr/share/wordlists/rockyou.txt\n\n".encode('utf-8')
                        )
                else:
                    sys.stdout.buffer.write(
                        f"  {Colors.WARNING}[{tipo} → mode {mode}]{Colors.ENDC}\n".encode('utf-8')
                    )
                    sys.stdout.buffer.write(
                        f"  hashcat -m {mode} -a 0 {out_file} /usr/share/wordlists/rockyou.txt\n\n".encode('utf-8')
                    )
                sys.stdout.buffer.flush()
            
            print(f"  {Colors.OKCYAN}[Tip]{Colors.ENDC} Para John the Ripper:")
            print(f"  john --wordlist=/usr/share/wordlists/rockyou.txt {out_file}")
            
    except PermissionError:
        print(f"{Colors.FAIL}[-] Error: No hay permisos para escribir en el directorio actual.{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
