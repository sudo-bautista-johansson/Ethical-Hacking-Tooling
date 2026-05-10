import urllib.parse
import base64
import string

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

def rot_alpha(n):
    from string import ascii_lowercase as lc, ascii_uppercase as uc
    lookup = str.maketrans(lc + uc, lc[n:] + lc[:n] + uc[n:] + uc[:n])
    return lambda s: s.translate(lookup)

def try_decode(text, method):
    try:
        if method == "b64": return base64.b64decode(text + "=" * (4 - len(text) % 4)).decode('utf-8')
        if method == "b32": return base64.b32decode(text + "=" * (8 - len(text) % 8)).decode('utf-8')
        if method == "hex": return bytes.fromhex(text).decode('utf-8')
    except: return None

def check_for_flag(text):
    return any(kw in text.upper() for kw in ["THM{", "HTB{", "FLAG{"]) if text else False

def run(cipher):
    print(f"[*] Analizando cadena: {cipher[:50]}...")
    url_decoded = urllib.parse.unquote(cipher)
    cipher = url_decoded

    for method, key in [("Base64", "b64"), ("Base32", "b32"), ("Hexadecimal", "hex")]:
        dec = try_decode(cipher, key)
        if dec:
            printable = ''.join(filter(lambda x: x in string.printable, dec))
            if check_for_flag(printable): print(f"{Colors.WARNING}>> FLAG ENCONTRADA <<\n{Colors.OKGREEN}[+] {method}: {printable}{Colors.ENDC}")
            elif len(printable) < 200: print(f"[*] {method}: {printable}")

    for i in range(1, 26):
        rotated = rot_alpha(i)(cipher)
        if check_for_flag(rotated): print(f"{Colors.WARNING}>> FLAG ENCONTRADA <<\n{Colors.OKGREEN}[+] ROT-{i}: {rotated}{Colors.ENDC}")
