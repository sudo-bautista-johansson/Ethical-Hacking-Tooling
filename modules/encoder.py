import sys
import string

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _cmd(c): sys.stdout.buffer.write(f"    {Colors.OKGREEN}{c}{Colors.ENDC}\n".encode('utf-8')); sys.stdout.buffer.flush()
def _tip(c): print(f"    {Colors.OKCYAN}# {c}{Colors.ENDC}")
def _header(t): print(f"\n{Colors.BOLD}── {t} ──{Colors.ENDC}\n")
def check_flag(text): return any(kw in text.upper() for kw in ["THM{","HTB{","FLAG{","CTF{","PICO{","DARK{"])

# ─── Decoders ────────────────────────────────────────

def morse_decode(text):
    MORSE = {'.-':'A','-.':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I',
             '.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q',
             '.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y',
             '--..':'Z','-----':'0','.----':'1','..---':'2','...--':'3','....-':'4','.....':'5',
             '-....':'6','--...':'7','---..':'8','----.':'9','.-.-.-':'.','--..--':',','..--..':'?'}
    try:
        words = text.strip().split('   ')
        return ' '.join(''.join(MORSE.get(c,'?') for c in w.split()) for w in words)
    except: return None

def atbash(text):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr(base + 25 - (ord(c) - base)))
        else: result.append(c)
    return ''.join(result)

def vigenere(text, key):
    key = key.upper(); result = []; ki = 0
    for c in text:
        if c.isalpha():
            shift = ord(key[ki % len(key)]) - ord('A')
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base - shift) % 26 + base)); ki += 1
        else: result.append(c)
    return ''.join(result)

def rail_fence(text, rails):
    n = len(text); pattern = []; rail = 0; direction = 1
    for i in range(n):
        pattern.append(rail)
        if rail == 0: direction = 1
        elif rail == rails - 1: direction = -1
        rail += direction
    indices = sorted(range(n), key=lambda i: pattern[i])
    result = [''] * n
    for i, char in zip(indices, text): result[i] = char
    return ''.join(result)

def bacon_decode(text):
    BACON = {'AAAAA':'A','AAAAB':'B','AAABA':'C','AAABB':'D','AABAA':'E','AABAB':'F','AABBA':'G',
             'AABBB':'H','ABAAA':'I','ABAAB':'J','ABABA':'K','ABABB':'L','ABBAA':'M','ABBAB':'N',
             'ABBBA':'O','ABBBB':'P','BAAAA':'Q','BAAAB':'R','BAABA':'S','BAABB':'T','BABAA':'U',
             'BABAB':'V','BABBA':'W','BABBB':'X','BBAAA':'Y','BBAAB':'Z'}
    t = text.upper().replace(' ','')
    if len(t) % 5 != 0: return None
    result = ''.join(BACON.get(t[i:i+5],'?') for i in range(0,len(t),5))
    return result if '?' not in result else None

def xor_brute(text):
    """Fuerza bruta XOR de byte único contra texto hex o raw."""
    results = []
    try:
        raw = bytes.fromhex(text.replace(' ','').replace('0x',''))
    except:
        raw = text.encode('latin-1', errors='replace')
    for key in range(1, 256):
        decoded = bytes(b ^ key for b in raw)
        try:
            s = decoded.decode('ascii')
            printable_ratio = sum(c in string.printable for c in s) / len(s)
            if printable_ratio > 0.85:
                results.append((key, s))
        except: pass
    return results

def rot47(text):
    result = []
    for c in text:
        n = ord(c)
        if 33 <= n <= 126:
            result.append(chr(33 + (n - 33 + 47) % 94))
        else:
            result.append(c)
    return ''.join(result)

def from_binary(text):
    """Convierte binario (01010101...) a texto."""
    clean = text.replace(' ', '')
    if not all(c in '01' for c in clean) or len(clean) % 8 != 0:
        return None
    try:
        return ''.join(chr(int(clean[i:i+8], 2)) for i in range(0, len(clean), 8))
    except: return None

def from_decimal(text):
    """Convierte números decimales separados por espacio a texto."""
    try:
        nums = [int(x) for x in text.split()]
        if all(32 <= n <= 126 for n in nums):
            return ''.join(chr(n) for n in nums)
    except: pass
    return None

def auto_detect(text):
    """Intenta detectar el tipo de cifrado automáticamente."""
    hints = []
    clean = text.strip()
    if all(c in '.- /' for c in clean) and ('.' in clean or '-' in clean):
        hints.append("📡 Parece Morse Code (usa '. -' y espacios)")
    if all(c in 'ABab ' for c in clean) and len(clean) >= 5:
        hints.append("🥓 Parece Bacon Cipher (solo A y B)")
    if all(c in '01 ' for c in clean) and len(clean.replace(' ','')) % 8 == 0:
        hints.append("💻 Parece Binario (grupos de 8 bits)")
    if all(c.isdigit() or c == ' ' for c in clean) and ' ' in clean:
        hints.append("🔢 Parece ASCII Decimal (números separados por espacio)")
    if all(c in '0123456789abcdefABCDEF ' for c in clean):
        hints.append("🔵 Parece Hexadecimal")
    if all(c.isalpha() or c in ' {}!_-.' for c in clean):
        hints.append("🔄 Parece sustitución (Atbash, ROT, Vigenere)")
    return hints

# ─── Main ────────────────────────────────────────────

def run(text, key=None):
    print(f"{Colors.BOLD}{'='*55}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  ENCODER v2.0 — OBSIDIAN TIER{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*55}{Colors.ENDC}")
    print(f"\n{Colors.OKCYAN}[*] Input: {text[:70]}{Colors.ENDC}\n")

    flag_found = False
    results = []

    # Auto-detect hints
    hints = auto_detect(text)
    if hints:
        _header("Auto-Detección de Cifrado")
        for h in hints:
            print(f"  {Colors.WARNING}{h}{Colors.ENDC}")

    _header("Resultados de Decodificación")

    # Morse
    morse = morse_decode(text)
    if morse and morse != text:
        results.append(("Morse Code", morse))

    # ROT47
    r47 = rot47(text)
    if r47 != text:
        results.append(("ROT-47", r47))

    # Atbash
    atb = atbash(text)
    if atb != text:
        results.append(("Atbash", atb))

    # Vigenere con key
    if key:
        vig = vigenere(text, key)
        results.append((f"Vigenere (key='{key}')", vig))

    # Rail Fence 2-5 rails
    for rails in range(2, 6):
        try:
            rf = rail_fence(text, rails)
            if rf != text:
                results.append((f"Rail Fence ({rails} rails)", rf))
        except: pass

    # Bacon
    if all(c in 'ABab ' for c in text):
        bacon = bacon_decode(text)
        if bacon:
            results.append(("Bacon Cipher", bacon))

    # Binary
    bin_result = from_binary(text)
    if bin_result:
        results.append(("Binary", bin_result))

    # Decimal
    dec_result = from_decimal(text)
    if dec_result:
        results.append(("ASCII Decimal", dec_result))

    # XOR brute force
    xor_results = xor_brute(text)
    if xor_results:
        _header(f"XOR Brute Force — {len(xor_results)} candidatos legibles")
        for key_byte, decoded in xor_results[:10]:
            if check_flag(decoded):
                print(f"\n{Colors.FAIL}>> FLAG ENCONTRADA (XOR key=0x{key_byte:02x}) <<{Colors.ENDC}")
                print(f"{Colors.OKGREEN}[+] {decoded}{Colors.ENDC}\n")
                flag_found = True
            else:
                s = ''.join(c for c in decoded if c in string.printable)
                sys.stdout.buffer.write(f"  [key=0x{key_byte:02x}] {s[:80]}\n".encode('utf-8'))
        sys.stdout.buffer.flush()

    # Mostrar resultados
    for method, decoded in results:
        printable = ''.join(c for c in decoded if c in string.printable)
        if not printable.strip(): continue
        if check_flag(printable):
            print(f"\n{Colors.FAIL}>> FLAG ENCONTRADA ({method}) <<{Colors.ENDC}")
            print(f"{Colors.OKGREEN}[+] {printable}{Colors.ENDC}\n")
            flag_found = True
        else:
            sys.stdout.buffer.write(f"  [{method:25s}] {printable[:100]}\n".encode('utf-8'))
            sys.stdout.buffer.flush()

    if not flag_found:
        print(f"\n{Colors.WARNING}[-] No se encontraron flags. Revisá los resultados manualmente.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[*] También probá: python Farei_0x.py crypto \"{text[:30]}\"  (Base64/Hex/ROT recursivo){Colors.ENDC}")
        print(f"{Colors.OKCYAN}[*] CyberChef: https://gchq.github.io/CyberChef/{Colors.ENDC}")

    print(f"\n{Colors.BOLD}{'='*55}{Colors.ENDC}")
