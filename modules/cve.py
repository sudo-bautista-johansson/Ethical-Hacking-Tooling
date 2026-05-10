import urllib.parse
import urllib.request
import json
import re
import ssl
import sys

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ─── Utilidades ───────────────────────────────────────────────────

def _request(url, timeout=15):
    """Petición HTTP robusta con fallback de SSL para entornos Windows/VPN."""
    headers = {'User-Agent': 'Mozilla/5.0 (Farei_0x CVE Scanner)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        # Intento 1: Con verificación SSL normal
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode('utf-8'))
    except ssl.SSLError:
        # Intento 2: Sin verificación (redes corporativas / VPN)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
            return json.loads(res.read().decode('utf-8'))

def _severity_color(severity):
    s = str(severity).upper()
    if s in ("CRITICAL",): return Colors.FAIL + Colors.BOLD
    if s in ("HIGH",): return Colors.FAIL
    if s in ("MEDIUM",): return Colors.WARNING
    return Colors.OKGREEN

# ─── Motor NVD (NIST) ────────────────────────────────────────────

def search_nvd(query):
    """Consulta la API oficial de NIST NVD v2.0."""
    is_cve = bool(re.match(r'^CVE-\d{4}-\d{4,}$', query.strip().upper()))
    
    if is_cve:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={query.strip().upper()}"
    else:
        encoded = urllib.parse.quote(query)
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={encoded}&resultsPerPage=10"
    
    try:
        data = _request(url)
        return data.get('vulnerabilities', [])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"{Colors.WARNING}[!] NVD API Rate-Limit alcanzado. Esperá 30 segundos e intentá de nuevo.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[-] Error HTTP {e.code} consultando NVD.{Colors.ENDC}")
        return []
    except Exception as e:
        print(f"{Colors.FAIL}[-] Error de red consultando NVD: {e}{Colors.ENDC}")
        return []

def parse_nvd_entry(vuln):
    """Extrae info limpia de un resultado de NVD."""
    cve = vuln.get('cve', {})
    cve_id = cve.get('id', '???')
    
    # Descripción en inglés
    descs = cve.get('descriptions', [])
    desc = next((d['value'] for d in descs if d.get('lang') == 'en'), 'Sin descripción disponible')
    
    # CVSS Score (intentar v3.1, luego v3.0, luego v2)
    metrics = cve.get('metrics', {})
    score, severity = "?", "?"
    for key in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
        entries = metrics.get(key, [])
        if entries:
            cvss = entries[0].get('cvssData', {})
            score = cvss.get('baseScore', '?')
            severity = cvss.get('baseSeverity', cvss.get('severity', '?'))
            break
    
    # Referencias útiles (exploit-db, github, packetstorm)
    refs = cve.get('references', [])
    exploit_refs = [r['url'] for r in refs if any(k in r.get('url', '').lower() 
                    for k in ['exploit-db', 'github.com', 'packetstorm', 'rapid7'])]
    
    return {
        'id': cve_id,
        'desc': desc,
        'score': score,
        'severity': str(severity).upper(),
        'exploit_refs': exploit_refs[:3]
    }

# ─── Motor GitHub ────────────────────────────────────────────────

def search_github(query, max_results=3):
    """Búsqueda inteligente en GitHub."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc"
    
    try:
        data = _request(url, timeout=10)
        items = data.get('items', [])[:max_results]
        return [{
            'name': r.get('full_name', '?'),
            'url': r.get('html_url', ''),
            'clone': r.get('clone_url', ''),
            'stars': r.get('stargazers_count', 0),
            'desc': (r.get('description') or '')[:100],
            'lang': r.get('language', '?')
        } for r in items]
    except:
        return []

# ─── Función Principal ───────────────────────────────────────────

def run(service_name):
    is_cve_id = bool(re.match(r'^CVE-\d{4}-\d{4,}$', service_name.strip().upper()))
    
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO AUTO-CVE v2.0 (Obsidian Tier){Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    if is_cve_id:
        print(f"\n{Colors.OKCYAN}[*] Modo: Búsqueda directa por CVE ID → {service_name.upper()}{Colors.ENDC}")
    else:
        print(f"\n{Colors.OKCYAN}[*] Modo: Búsqueda por servicio → \"{service_name}\"{Colors.ENDC}")
    
    # ──────────────── FASE 1: NVD/NIST ────────────────
    print(f"\n{Colors.BOLD}── FASE 1: Base de Datos Nacional de Vulnerabilidades (NVD) ──{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Consultando API de NIST...{Colors.ENDC}")
    
    vulns = search_nvd(service_name)
    cve_ids_found = []
    
    if vulns:
        print(f"{Colors.OKGREEN}[+] {len(vulns)} CVE(s) encontrado(s):{Colors.ENDC}\n")
        
        for v in vulns[:8]:
            entry = parse_nvd_entry(v)
            cve_ids_found.append(entry['id'])
            
            color = _severity_color(entry['severity'])
            desc_short = entry['desc'][:120] + "..." if len(entry['desc']) > 120 else entry['desc']
            
            sys.stdout.buffer.write(f"  {color}[{entry['severity']} {entry['score']}]{Colors.ENDC} {Colors.BOLD}{entry['id']}{Colors.ENDC}\n".encode('utf-8'))
            sys.stdout.buffer.write(f"  {desc_short}\n".encode('utf-8'))
            
            if entry['exploit_refs']:
                for ref in entry['exploit_refs']:
                    sys.stdout.buffer.write(f"  {Colors.WARNING}↳ {ref}{Colors.ENDC}\n".encode('utf-8'))
            
            sys.stdout.buffer.write(b"\n")
            sys.stdout.buffer.flush()
    else:
        print(f"{Colors.WARNING}[-] NVD no devolvió resultados para esta consulta.{Colors.ENDC}")
    
    # ──────────────── FASE 2: GitHub Exploits ────────────────
    print(f"{Colors.BOLD}── FASE 2: Exploits y PoCs en GitHub ──{Colors.ENDC}")
    
    from core import db
    found_any = False
    
    if cve_ids_found:
        # Búsqueda precisa: por cada CVE encontrado en NVD
        print(f"{Colors.OKCYAN}[*] Buscando PoCs para {len(cve_ids_found[:5])} CVEs identificados...{Colors.ENDC}\n")
        
        for cve_id in cve_ids_found[:5]:
            repos = search_github(f"{cve_id} PoC exploit", max_results=2)
            if repos:
                found_any = True
                print(f"  {Colors.OKGREEN}📦 {cve_id}:{Colors.ENDC}")
                for r in repos:
                    print(f"    ⭐ {r['stars']} | {r['lang']} | {r['desc']}")
                    sys.stdout.buffer.write(f"    🔗 {r['url']}\n".encode('utf-8'))
                    sys.stdout.buffer.write(f"    💻 git clone {r['clone']}\n".encode('utf-8'))
                    sys.stdout.buffer.flush()
                    db.add_exploit(service_name, r['url'], f"{cve_id} | ⭐{r['stars']} | {r['lang']}")
                print()
    
    if not found_any:
        # Búsqueda amplia como fallback
        print(f"{Colors.OKCYAN}[*] Búsqueda amplia en GitHub...{Colors.ENDC}\n")
        repos = search_github(f"{service_name} exploit PoC RCE", max_results=5)
        if repos:
            found_any = True
            for r in repos:
                print(f"    ⭐ {r['stars']} | {r['lang']} | {r['desc']}")
                sys.stdout.buffer.write(f"    🔗 {r['url']}\n".encode('utf-8'))
                sys.stdout.buffer.write(f"    💻 git clone {r['clone']}\n".encode('utf-8'))
                sys.stdout.buffer.flush()
                db.add_exploit(service_name, r['url'], f"⭐{r['stars']} | {r['lang']}")
                print()
        else:
            print(f"{Colors.WARNING}[-] No se encontraron repositorios de exploits públicos.{Colors.ENDC}\n")
    
    # ──────────────── FASE 3: Comandos Manuales ────────────────
    print(f"{Colors.BOLD}── FASE 3: Búsquedas Manuales Recomendadas ──{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}  [Exploit-DB Local]{Colors.ENDC}")
    print(f"    searchsploit \"{service_name}\"")
    
    print(f"\n{Colors.OKGREEN}  [Google Dorks]{Colors.ENDC}")
    if cve_ids_found:
        top_cve = cve_ids_found[0]
        print(f"    \"{top_cve}\" exploit site:github.com")
        print(f"    \"{top_cve}\" site:exploit-db.com")
    else:
        print(f"    \"{service_name}\" exploit PoC site:github.com")
        print(f"    \"{service_name}\" site:exploit-db.com")
    print(f"    \"{service_name}\" site:cvedetails.com")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
