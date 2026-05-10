import asyncio
import aiohttp
import sys
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Wordlist de respaldo si no hay ninguna en el sistema
FALLBACK_WORDLIST = ["admin", "login", "index", "robots.txt", "backup", "db", "config", "test", "api", "wp-admin", "secret", "hidden", ".git", "dev"]

async def calibrate(session, url):
    """
    Envía una petición a un directorio que seguro no existe para detectar
    si el servidor miente (devuelve 200 en lugar de 404).
    """
    fake_path = "xxyyzz123_non_existent"
    target = f"{url.rstrip('/')}/{fake_path}"
    try:
        async with session.get(target, allow_redirects=False, timeout=5) as res:
            if res.status == 200:
                print(f"{Colors.WARNING}[!] CUIDADO: El servidor devuelve 200 OK en páginas que no existen (Rabbit Hole).{Colors.ENDC}")
                print(f"{Colors.WARNING}[!] Tamaño de página falsa: {res.content_length} bytes. Aislando tamaño...{Colors.ENDC}")
                return res.content_length
    except:
        pass
    return -1

async def fetch(session, url, path, sem, false_size):
    async with sem:
        target = f"{url.rstrip('/')}/{path.lstrip('/')}"
        try:
            async with session.get(target, allow_redirects=False, timeout=5) as res:
                if res.status != 404:
                    # Lógica Anti-Rabbit-Hole
                    if res.status == 200 and false_size != -1:
                        # Un margen de 10 bytes por si hay un script de "tiempo de respuesta" en la página
                        if false_size - 10 <= res.content_length <= false_size + 10:
                            return # Ignoramos este resultado, es basura.

                    from core import db
                    db.add_directory(url, path, res.content_length, res.status)

                    color = Colors.OKGREEN if res.status == 200 else Colors.WARNING
                    print(f"{color}[Status: {res.status}]{Colors.ENDC} [Size: {res.content_length}] - {target}")
        except Exception as e:
            pass # Ignoramos timeouts y caídas para mantener el output limpio

async def fuzzer(url, wordlist_path, concurrency=50):
    words = []
    if os.path.exists(wordlist_path):
        try:
            with open(wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"{Colors.FAIL}[-] Error leyendo diccionario: {e}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}[!] Diccionario {wordlist_path} no encontrado. Usando wordlist de respaldo.{Colors.ENDC}")
        words = FALLBACK_WORDLIST

    if not words: return

    print(f"{Colors.OKCYAN}[*] Calibrando escáner (Anti-Rabbit-Hole)...{Colors.ENDC}")
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "127.0.0.1" 
    }
    
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        false_size = await calibrate(session, url)
        
        print(f"{Colors.OKCYAN}[*] Iniciando fuzzing de {len(words)} rutas...{Colors.ENDC}")
        tasks = [asyncio.ensure_future(fetch(session, url, w, sem, false_size)) for w in words]
        await asyncio.gather(*tasks)

def run(url, wordlist):
    print(f"{Colors.OKGREEN}=== Módulo Fuzzer v2.0 (Obsidian Tier) ==={Colors.ENDC}")
    try:
        asyncio.run(fuzzer(url, wordlist))
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Fuzzing interrumpido por el usuario.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error crítico en el Fuzzer: {e}{Colors.ENDC}")
