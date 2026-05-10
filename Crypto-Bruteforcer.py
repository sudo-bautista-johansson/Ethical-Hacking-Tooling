#!/usr/bin/env python3
import argparse
import base64
import urllib.parse
import string

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def rot_alpha(n):
    """Genera una función de rotación César para un N dado."""
    from string import ascii_lowercase as lc, ascii_uppercase as uc
    lookup = str.maketrans(lc + uc, lc[n:] + lc[:n] + uc[n:] + uc[:n])
    return lambda s: s.translate(lookup)

def try_base64(text):
    try:
        # Añadir padding si falta
        padding = 4 - (len(text) % 4)
        if padding != 4:
            text += "=" * padding
        decoded_bytes = base64.b64decode(text, validate=True)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return None

def try_base32(text):
    try:
        # Añadir padding si falta
        padding = 8 - (len(text) % 8)
        if padding != 8:
            text += "=" * padding
        decoded_bytes = base64.b32decode(text, validate=True)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return None

def try_hex(text):
    try:
        decoded_bytes = bytes.fromhex(text)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return None

def check_for_flag(text, keywords=["THM{", "HTB{", "FLAG{"]):
    """Verifica si el texto decodificado contiene un formato de flag conocido."""
    if not text:
        return False
    for kw in keywords:
        if kw in text.upper():
            return True
    return False

def print_result(method, result, is_flag=False):
    if result:
        # Filtrar solo caracteres imprimibles para no romper la consola
        printable_result = ''.join(filter(lambda x: x in string.printable, result))
        if is_flag:
            print(f"\n{Colors.WARNING}>>>>> FLAG ENCONTRADA <<<<<{Colors.ENDC}")
            print(f"{Colors.OKGREEN}[+] {method}: {printable_result}{Colors.ENDC}\n")
        else:
            # Solo mostrar si es corto o parece texto legible
            if len(printable_result) < 200:
                 print(f"[*] {method}:\n    {printable_result}")

def main():
    parser = argparse.ArgumentParser(description="Desencriptador Criptográfico Bruto (Identificador de Flags)")
    parser.add_argument("string", help="Cadena encriptada/encodeada a analizar")
    args = parser.parse_args()

    cipher = args.string.strip()
    print(f"{Colors.OKCYAN}[*] Analizando cadena: {cipher[:50]}{'...' if len(cipher)>50 else ''}{Colors.ENDC}\n")

    # 1. URL Decode
    url_decoded = urllib.parse.unquote(cipher)
    if url_decoded != cipher:
        print_result("URL Decode", url_decoded, check_for_flag(url_decoded))
        cipher = url_decoded # Usar la versión decodeada para los siguientes pasos

    # 2. Base64
    b64 = try_base64(cipher)
    if b64:
        print_result("Base64", b64, check_for_flag(b64))

    # 3. Base32
    b32 = try_base32(cipher)
    if b32:
        print_result("Base32", b32, check_for_flag(b32))

    # 4. Hexadecimal
    hex_dec = try_hex(cipher)
    if hex_dec:
        print_result("Hexadecimal", hex_dec, check_for_flag(hex_dec))

    # 5. Rotaciones César (ROT1 a ROT25)
    for i in range(1, 26):
        rot_func = rot_alpha(i)
        rotated = rot_func(cipher)
        # En ROT, generalmente solo imprimimos si encontramos la flag para no hacer spam,
        # O si el usuario lo pide explícitamente, pero aquí buscamos flags.
        if check_for_flag(rotated):
             print_result(f"ROT-{i}", rotated, True)
             
    # TODO: Añadir XOR en futuras versiones

    print("\n[*] Análisis completado.")

if __name__ == "__main__":
    main()
