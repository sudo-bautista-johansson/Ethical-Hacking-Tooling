import urllib.parse
import base64
import string
import sys

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def rot_alpha(n):
    from string import ascii_lowercase as lc, ascii_uppercase as uc
    lookup = str.maketrans(lc + uc, lc[n:] + lc[:n] + uc[n:] + uc[:n])
    return lambda s: s.translate(lookup)

def try_decode(text, method):
    try:
        if method == "b64": return base64.b64decode(text + "=" * (4 - len(text) % 4))
        if method == "b32": return base64.b32decode(text + "=" * (8 - len(text) % 8))
        if method == "hex": return bytes.fromhex(text)
    except: return None

def check_for_flag(text):
    return any(kw in text.upper() for kw in ["THM{", "HTB{", "FLAG{", "CTF{"]) if text else False

def run(cipher):
    if not cipher or not cipher.strip():
        print(f"{Colors.WARNING}[-] No se proporcionó ninguna cadena para analizar.{Colors.ENDC}")
        return

    print(f"{Colors.OKGREEN}[*]{Colors.ENDC} Analizando cadena: {cipher[:50]}...")
    url_decoded = urllib.parse.unquote(cipher)
    cipher = url_decoded

    flag_found = False

    for method, key in [("Base64", "b64"), ("Base32", "b32"), ("Hexadecimal", "hex")]:
        dec_bytes = try_decode(cipher, key)
        if dec_bytes:
            # Intentar decodificar como UTF-8 normal
            try:
                dec_str = dec_bytes.decode('utf-8')
                is_binary = False
            except UnicodeDecodeError:
                dec_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in dec_bytes)
                is_binary = True
                
            printable = ''.join(filter(lambda x: x in string.printable, dec_str.replace('.', '')))
            
            if check_for_flag(printable): 
                print(f"{Colors.WARNING}>> FLAG ENCONTRADA <<\n{Colors.OKGREEN}[+] {method}: {printable}{Colors.ENDC}")
                flag_found = True
            elif is_binary:
                # Solo alertar si el binario tiene tamaño significativo (>20 bytes)
                # para evitar falsos positivos con cadenas cortas
                if len(dec_bytes) > 20:
                    print(f"\n{Colors.WARNING}[!] ALERTA BINARIA: La cadena {method} parece ser un archivo binario u objeto serializado (Ej. Ticket Kerberos/Rubeus).{Colors.ENDC}")
                    out_name = f"payload_extraido_{method.lower()}.bin"
                    with open(out_name, "wb") as f:
                        f.write(dec_bytes)
                    print(f"{Colors.OKGREEN}[+] Binario guardado como: {out_name}{Colors.ENDC}")
                    print(f"[*] Textos legibles extraídos: {printable[:200]}...")
            elif len(printable) < 200: 
                print(f"[*] {method}: {printable}")
                # --- DECODIFICACIÓN RECURSIVA ---
                # Si el resultado parece ser otra cadena codificada, intentar decodificar de nuevo
                nested_result = try_recursive_decode(printable, depth=0)
                if nested_result:
                    flag_found = True

    for i in range(1, 26):
        rotated = rot_alpha(i)(cipher)
        if check_for_flag(rotated): 
            print(f"{Colors.WARNING}>> FLAG ENCONTRADA <<\n{Colors.OKGREEN}[+] ROT-{i}: {rotated}{Colors.ENDC}")
            flag_found = True

    if not flag_found:
        print(f"\n{Colors.WARNING}[-] No se encontraron flags automáticamente. Revisa los resultados manualmente.{Colors.ENDC}")


def try_recursive_decode(text, depth=0):
    """Intenta decodificar recursivamente hasta 5 capas de profundidad."""
    if depth >= 5:
        return False
    
    for method, key in [("Base64", "b64"), ("Base32", "b32"), ("Hexadecimal", "hex")]:
        dec_bytes = try_decode(text.strip(), key)
        if dec_bytes:
            try:
                dec_str = dec_bytes.decode('utf-8')
            except UnicodeDecodeError:
                continue
            
            printable = ''.join(filter(lambda x: x in string.printable, dec_str))
            
            if check_for_flag(printable):
                layers = "->".join([method] * (depth + 1))
                print(f"{Colors.WARNING}>> FLAG ENCONTRADA (Capa {depth + 2}: {method}) <<\n{Colors.OKGREEN}[+] {printable}{Colors.ENDC}")
                return True
            elif len(printable) > 3:
                # Mostrar capa intermedia y seguir buscando
                result = try_recursive_decode(printable, depth + 1)
                if result:
                    return True
    return False
