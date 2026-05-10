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
    BOLD = '\033[1m'

# Wordlists de respaldo
FALLBACK_WORDLIST = ["admin", "login", "index", "robots.txt", "backup", "db", "config", "test", "api", "wp-admin", "secret", "hidden", ".git", "dev", "dashboard", "uploads", "files", "images", "static", "assets", "js", "css", "php", "old", "bak"]

FALLBACK_VHOST_WORDLIST = ["admin", "dev", "staging", "test", "api", "mail", "webmail", "ftp", "ssh", "vpn", "portal", "internal", "intranet", "corp", "secure", "beta", "legacy", "monitor", "dashboard", "git", "gitlab", "jenkins", "jira", "confluence", "backup", "db", "database", "shop", "store", "blog", "forum", "support", "helpdesk", "ns1", "ns2", "mx"]

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

# ─── VHost / Subdomain Fuzzer ───────────────────────────────────

async def fetch_vhost(session, base_url, subdomain, domain, sem, baseline_size, baseline_title):
    """Prueba un subdominio via cabecera Host y detecta cambios en la respuesta."""
    async with sem:
        host_header = f"{subdomain}.{domain}"
        headers_vhost = {
            "Host": host_header,
            "User-Agent": "Mozilla/5.0 (Farei_0x Vhost Scanner)",
        }
        try:
            async with session.get(base_url, headers=headers_vhost, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=8)) as res:
                body = await res.text(errors='ignore')
                size = len(body)
                status = res.status

                # Detectar cambios respecto a la respuesta base
                size_diff = abs(size - baseline_size)
                is_different = (
                    status not in (400, 404, 302) and
                    size_diff > 50  # más de 50 bytes de diferencia = sospechoso
                )

                # También detectar si hay redirección a ese subdominio
                location = res.headers.get('Location', '')
                if subdomain.lower() in location.lower():
                    is_different = True

                if is_different:
                    from core import db
                    db.add_directory(base_url, f"[VHOST] {host_header}", size, status)

                    color = Colors.OKGREEN if status == 200 else Colors.WARNING
                    sys.stdout.buffer.write(
                        f"{color}[VHOST FOUND]{Colors.ENDC} {Colors.BOLD}{host_header}{Colors.ENDC} "
                        f"[Status: {status}] [Size: {size}] [Diff: +{size_diff}B]\n".encode('utf-8')
                    )
                    sys.stdout.buffer.flush()
        except Exception:
            pass

async def vhost_fuzzer(url, domain, wordlist_path, concurrency=50):
    """Fuzzing de VHosts/Subdominios via cabecera Host."""
    words = []
    if os.path.exists(wordlist_path):
        try:
            with open(wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"{Colors.FAIL}[-] Error leyendo wordlist: {e}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}[!] Wordlist no encontrada. Usando lista de respaldo de {len(FALLBACK_VHOST_WORDLIST)} subdominios.{Colors.ENDC}")
        words = FALLBACK_VHOST_WORDLIST

    if not words:
        return

    print(f"{Colors.OKCYAN}[*] Obteniendo respuesta base para calibración...{Colors.ENDC}")
    baseline_size = 0
    baseline_title = ""

    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as res:
                body = await res.text(errors='ignore')
                baseline_size = len(body)
                print(f"{Colors.OKCYAN}[*] Respuesta base: {res.status} | Tamaño: {baseline_size} bytes{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[-] No se pudo conectar a {url}: {e}{Colors.ENDC}")
            return

        print(f"{Colors.OKCYAN}[*] Lanzando {len(words)} pruebas de VHost contra {domain}...{Colors.ENDC}\n")
        sem = asyncio.Semaphore(concurrency)
        tasks = [fetch_vhost(session, url, w, domain, sem, baseline_size, baseline_title) for w in words]
        await asyncio.gather(*tasks)

# ─── Entry Points ─────────────────────────────────────────────────

def run(url, wordlist, mode="dir", domain=None):
    if mode == "vhost":
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}  MÓDULO FUZZER v2.0 — Modo VHOST (Obsidian Tier){Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[*] Target URL: {url} | Dominio base: {domain}{Colors.ENDC}")
        try:
            asyncio.run(vhost_fuzzer(url, domain, wordlist))
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] VHost fuzzing interrumpido.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[-] Error en VHost Fuzzer: {e}{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}  MÓDULO FUZZER v2.0 — Modo DIR (Obsidian Tier){Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        try:
            asyncio.run(fuzzer(url, wordlist))
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] Fuzzing interrumpido por el usuario.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[-] Error crítico en el Fuzzer: {e}{Colors.ENDC}")
