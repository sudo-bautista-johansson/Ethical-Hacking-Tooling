#!/usr/bin/env python3
import re
import argparse
import sys

# Códigos Hashcat comunes:
# MD5: 0
# SHA512 (Unix): 1800
# bcrypt: 3200
# NTLM: 1000

def identify_hash(h):
    """Identifica el tipo de hash basado en patrones Regex"""
    # bcrypt (típico en bases de datos web modernas)
    if re.match(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$", h):
        return ("bcrypt", 3200)
    
    # SHA512-Crypt (típico de /etc/shadow en Linux modernos)
    elif re.match(r"^\$6\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{86}$", h):
        return ("SHA512-Crypt", 1800)
        
    # MD5-Crypt (sistemas Linux más antiguos)
    elif re.match(r"^\$1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}$", h):
        return ("MD5-Crypt", 500)
        
    # NTLM / MD5 puro (32 caracteres hexadecimales)
    elif re.match(r"^[a-fA-F0-9]{32}$", h):
        # Es imposible distinguir MD5 puro de NTLM solo por la longitud, 
        # asumimos MD5 genérico como fallback, pero sugerimos NTLM.
        return ("MD5 / NTLM", "0 / 1000")
        
    # SHA1 puro (40 caracteres hexadecimales)
    elif re.match(r"^[a-fA-F0-9]{40}$", h):
        return ("SHA1", 100)
        
    # SHA256 puro (64 caracteres hexadecimales)
    elif re.match(r"^[a-fA-F0-9]{64}$", h):
        return ("SHA256", 1400)
        
    return ("Desconocido", "?")

def parse_shadow_file(filepath):
    print(f"[*] Parseando /etc/shadow: {filepath}")
    results = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    user = parts[0]
                    hash_val = parts[1]
                    # Solo ignorar cuentas sin hash válido
                    if hash_val not in ['*', '!', '!!', 'x']:
                        results.append((user, hash_val))
    except Exception as e:
        print(f"[-] Error leyendo el archivo: {e}")
    return results

def parse_generic_file(filepath):
    print(f"[*] Buscando hashes puros en archivo genérico: {filepath}")
    results = []
    # Regex genérico para buscar cadenas que parezcan hashes dentro de texto
    hash_pattern = re.compile(r"(\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}|\$6\$[a-zA-Z0-9./]{1,16}\$[a-zA-Z0-9./]{86}|\$1\$[a-zA-Z0-9./]{1,8}\$[a-zA-Z0-9./]{22}|[a-fA-F0-9]{32,64})")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            matches = hash_pattern.findall(content)
            for m in matches:
                # Filtrar falsos positivos de secuencias de números (ej. IPv6 o IDs)
                if not re.match(r"^\d+$", m):
                     results.append(("?", m))
    except Exception as e:
        print(f"[-] Error leyendo el archivo: {e}")
    
    # Eliminar duplicados
    return list(set(results))

def main():
    parser = argparse.ArgumentParser(description="Extractor de Hashes y Auto-Crack Command Generator")
    parser.add_argument("file", help="Archivo a analizar (puede ser /etc/shadow o un volcado SQL)")
    parser.add_argument("--shadow", action="store_true", help="Forzar el modo de parseo de /etc/shadow")
    args = parser.parse_args()

    results = []
    if args.shadow or "shadow" in args.file.lower():
        results = parse_shadow_file(args.file)
    else:
        results = parse_generic_file(args.file)

    if not results:
        print("[-] No se encontraron hashes válidos.")
        sys.exit(0)

    print("\n[+] HASHES ENCONTRADOS:\n" + "-"*50)
    
    # Escribir a un archivo limpio para pasarlo a hashcat
    out_file = "hashes_extraidos.txt"
    with open(out_file, 'w') as f_out:
        for user, hash_val in results:
            tipo, hashcat_mode = identify_hash(hash_val)
            print(f"Usuario/ID: {user}")
            print(f"Hash:       {hash_val[:30]}... (Truncado)")
            print(f"Tipo:       {tipo}")
            print(f"Modo Hashcat: -m {hashcat_mode}\n")
            
            f_out.write(f"{hash_val}\n")

    print(f"[*] Se han guardado los hashes limpios en '{out_file}'")
    
    print("\n[+] COMANDOS SUGERIDOS PARA HASHCAT:\n" + "-"*50)
    print("rockyou.txt es el diccionario por defecto en Kali.")
    
    # Extraer los modos únicos detectados para sugerir comandos
    modos_detectados = set([identify_hash(h)[1] for _, h in results])
    for modo in modos_detectados:
        if modo != "?":
            print(f"hashcat -m {modo} -a 0 {out_file} /usr/share/wordlists/rockyou.txt")

if __name__ == "__main__":
    main()
