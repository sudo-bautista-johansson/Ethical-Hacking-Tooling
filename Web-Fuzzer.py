#!/usr/bin/env python3
import asyncio
import aiohttp
import argparse
import sys

class Colors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

async def fetch(session, url, path, sem):
    async with sem:  # Limit concurrent requests
        target_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
        try:
            async with session.get(target_url, allow_redirects=False, timeout=5) as response:
                status = response.status
                length = response.content_length
                
                # Omitir 404
                if status != 404:
                    color = Colors.OKGREEN if status == 200 else (Colors.WARNING if status in [301, 302] else Colors.FAIL)
                    print(f"{color}[Status: {status}]{Colors.ENDC} [Size: {length}] - {target_url}")
        except Exception:
            pass # Ignorar errores de conexión (timeouts, etc) para no ensuciar la salida

async def fuzzer(url, wordlist_path, concurrency=50):
    print(f"{Colors.OKBLUE}[*]{Colors.ENDC} Iniciando Web Fuzzer Asíncrono...")
    print(f"{Colors.OKCYAN}[*]{Colors.ENDC} Target: {url}")
    print(f"{Colors.OKCYAN}[*]{Colors.ENDC} Concurrencia: {concurrency}")
    print("-" * 50)
    
    try:
        with open(wordlist_path, 'r', encoding='latin-1') as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"{Colors.FAIL}[-] Archivo de diccionario no encontrado: {wordlist_path}{Colors.ENDC}")
        sys.exit(1)

    sem = asyncio.Semaphore(concurrency)
    
    # Custom headers, útil para bypassear protecciones simples
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "127.0.0.1" # Simple WAF bypass
    }

    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        tasks = []
        for word in words:
            task = asyncio.ensure_future(fetch(session, url, word, sem))
            tasks.append(task)
            
        await asyncio.gather(*tasks)

def main():
    parser = argparse.ArgumentParser(description="Web Fuzzer Inteligente (Async)")
    parser.add_argument("-u", "--url", required=True, help="URL objetivo (ej. http://10.10.10.10)")
    parser.add_argument("-w", "--wordlist", required=True, help="Ruta al diccionario (wordlist)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Nivel de concurrencia (por defecto: 50)")
    args = parser.parse_args()

    # Ejecutar loop asíncrono
    try:
        asyncio.run(fuzzer(args.url, args.wordlist, args.threads))
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Fuzzing interrumpido por el usuario.{Colors.ENDC}")

if __name__ == "__main__":
    main()
