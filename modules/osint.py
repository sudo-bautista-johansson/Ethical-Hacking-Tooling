import urllib.request
import urllib.parse
import json
import sys
import ssl
import re

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _cmd(c): sys.stdout.buffer.write(f"    {Colors.OKGREEN}{c}{Colors.ENDC}\n".encode('utf-8')); sys.stdout.buffer.flush()
def _tip(c): print(f"    {Colors.OKCYAN}# {c}{Colors.ENDC}")
def _header(t): print(f"\n{Colors.BOLD}── {t} ──{Colors.ENDC}\n")
def _found(label, value): sys.stdout.buffer.write(f"  {Colors.OKGREEN}[{label}]{Colors.ENDC} {value}\n".encode('utf-8')); sys.stdout.buffer.flush()

def _request(url, headers=None, timeout=12):
    default_headers = {'User-Agent': 'Mozilla/5.0 (Farei_0x OSINT)'}
    if headers: default_headers.update(headers)
    req = urllib.request.Request(url, headers=default_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.read().decode('utf-8', errors='ignore')
    except ssl.SSLError:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception:
        return None

# ─── FASE 1: WHOIS via RDAP ────────────────────────────────────────

def whois_lookup(domain):
    _header("FASE 1: WHOIS / RDAP")
    url = f"https://rdap.org/domain/{domain}"
    data = _request(url)
    if data:
        try:
            j = json.loads(data)
            _found("Dominio", j.get('ldhName', domain))
            for event in j.get('events', []):
                action = event.get('eventAction', '')
                date = event.get('eventDate', '')[:10]
                if action in ('registration', 'expiration', 'last changed'):
                    _found(action.capitalize(), date)
            ns_list = [ns.get('ldhName', '') for ns in j.get('nameservers', [])]
            if ns_list:
                _found("Nameservers", ', '.join(ns_list))
            for entity in j.get('entities', []):
                roles = entity.get('roles', [])
                vcard = entity.get('vcardArray', [])
                if vcard and len(vcard) > 1:
                    for field in vcard[1]:
                        if field[0] == 'fn':
                            _found(', '.join(roles), field[3])
        except:
            print(f"  {Colors.WARNING}[Raw]{Colors.ENDC} {data[:300]}")
    else:
        print(f"  {Colors.FAIL}[-] WHOIS no disponible. Usá: whois {domain}{Colors.ENDC}")

# ─── FASE 2: DNS Records ─────────────────────────────────────────

def dns_lookup(domain):
    _header("FASE 2: Registros DNS (via Cloudflare DoH)")
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']
    for rtype in record_types:
        url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={rtype}"
        req = urllib.request.Request(url, headers={'Accept': 'application/dns-json', 'User-Agent': 'Farei_0x'})
        try:
            with urllib.request.urlopen(req, timeout=8) as res:
                j = json.loads(res.read())
                answers = j.get('Answer', [])
                if answers:
                    print(f"  {Colors.WARNING}[{rtype}]{Colors.ENDC}")
                    for ans in answers[:5]:
                        sys.stdout.buffer.write(f"    {Colors.OKGREEN}{ans.get('data','')}{Colors.ENDC}\n".encode('utf-8'))
                    sys.stdout.buffer.flush()
        except: pass

# ─── FASE 3: Subdominios via crt.sh ──────────────────────────────

def subdomain_crtsh(domain):
    _header("FASE 3: Subdominios via Certificate Transparency (crt.sh)")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    data = _request(url, timeout=20)
    found = set()
    if data:
        try:
            entries = json.loads(data)
            for entry in entries:
                for sub in entry.get('name_value', '').split('\n'):
                    sub = sub.strip().lstrip('*.')
                    if sub.endswith(domain) and sub != domain and ' ' not in sub:
                        found.add(sub)
        except: pass

    if found:
        print(f"  {Colors.OKGREEN}[+] {len(found)} subdominios encontrados:{Colors.ENDC}\n")
        for sub in sorted(found)[:40]:
            sys.stdout.buffer.write(f"    {Colors.OKGREEN}→ {sub}{Colors.ENDC}\n".encode('utf-8'))
        sys.stdout.buffer.flush()
        if len(found) > 40:
            print(f"    ... y {len(found)-40} más.")
        print(f"\n  {Colors.WARNING}[!] Agregá los encontrados a /etc/hosts y fuzzeá con:{Colors.ENDC}")
        _cmd(f"python Farei_0x.py fuzz IP --vhost --domain {domain}")
    else:
        print(f"  {Colors.WARNING}[-] No se encontraron subdominios en crt.sh.{Colors.ENDC}")

# ─── FASE 4: Tecnologías Web ─────────────────────────────────────

def tech_fingerprint(domain):
    _header("FASE 4: Fingerprinting de Tecnologías Web")
    url = f"http://{domain}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as res:
            headers = dict(res.headers)
            body = res.read(8192).decode('utf-8', errors='ignore')

        tech_found = []

        # Headers de servidor
        server = headers.get('Server', headers.get('server', ''))
        if server: tech_found.append(f"Server: {server}")
        powered = headers.get('X-Powered-By', headers.get('x-powered-by', ''))
        if powered: tech_found.append(f"X-Powered-By: {powered}")

        # Cookies
        cookie = headers.get('Set-Cookie', headers.get('set-cookie', ''))
        if 'PHPSESSID' in cookie: tech_found.append("PHP (PHPSESSID cookie)")
        if 'JSESSIONID' in cookie: tech_found.append("Java/Tomcat (JSESSIONID)")
        if 'ASP.NET' in cookie or 'ASPXAUTH' in cookie: tech_found.append("ASP.NET")
        if 'rails_session' in cookie: tech_found.append("Ruby on Rails")

        # Body fingerprints
        body_checks = [
            ('wp-content', 'WordPress'), ('wp-includes', 'WordPress'),
            ('Joomla', 'Joomla'), ('drupal', 'Drupal'),
            ('laravel_session', 'Laravel'), ('__utma', 'Google Analytics'),
            ('react', 'React.js'), ('vue', 'Vue.js'), ('angular', 'Angular'),
            ('jquery', 'jQuery'), ('bootstrap', 'Bootstrap'),
            ('nginx', 'Nginx'), ('apache', 'Apache'),
            ('flask', 'Flask'), ('django', 'Django'),
            ('express', 'Express.js'), ('tomcat', 'Apache Tomcat'),
        ]
        for keyword, name in body_checks:
            if keyword.lower() in body.lower():
                tech_found.append(name)

        if tech_found:
            unique_tech = list(dict.fromkeys(tech_found))
            for tech in unique_tech:
                _found("Tecnología", tech)
        else:
            print(f"  {Colors.WARNING}[-] No se detectaron tecnologías conocidas.{Colors.ENDC}")

    except Exception as e:
        print(f"  {Colors.FAIL}[-] No se pudo conectar a {url}: {e}{Colors.ENDC}")
        print(f"  {Colors.WARNING}[!] Usá Wappalyzer (extensión browser) para detección manual.{Colors.ENDC}")

# ─── FASE 5: Zone Transfer ───────────────────────────────────────

def zone_transfer(domain):
    _header("FASE 5: Zone Transfer (DNS Axfr) — Comandos Manuales")
    _tip("Si el DNS está mal configurado, podés obtener TODOS los subdominios de una vez")
    cmds = [
        f"dig axfr @ns1.{domain} {domain}",
        f"dig axfr {domain}",
        f"host -t axfr {domain}",
        f"dnsrecon -d {domain} -t axfr",
        f"fierce --domain {domain}",
    ]
    for cmd in cmds:
        _cmd(cmd)

# ─── FASE 6: Email Harvesting ────────────────────────────────────

def email_hints(domain):
    _header("FASE 6: Email Harvesting y Personas")
    _tip("Herramientas activas (Kali):")
    _cmd(f"theHarvester -d {domain} -b google,bing,linkedin,github -l 200")
    _cmd(f"theHarvester -d {domain} -b all")
    _tip("Herramientas pasivas online:")
    print(f"  {Colors.WARNING}[Hunter.io]{Colors.ENDC}")
    sys.stdout.buffer.write(f"    {Colors.OKGREEN}https://hunter.io/domain-search?domain={domain}{Colors.ENDC}\n".encode('utf-8'))
    print(f"  {Colors.WARNING}[Phonebook.cz (emails/subdomains/URLs)]{Colors.ENDC}")
    sys.stdout.buffer.write(f"    {Colors.OKGREEN}https://phonebook.cz/?query={domain}&type=email{Colors.ENDC}\n".encode('utf-8'))
    sys.stdout.buffer.flush()

# ─── FASE 7: Google Dorks ────────────────────────────────────────

def google_dorks(domain):
    _header("FASE 7: Google Dorks Avanzados")
    dorks = [
        (f"site:{domain}", "Páginas indexadas"),
        (f"site:{domain} filetype:pdf OR filetype:doc OR filetype:xls OR filetype:xlsx", "Documentos expuestos"),
        (f"site:{domain} inurl:admin OR inurl:login OR inurl:panel OR inurl:dashboard", "Paneles admin"),
        (f"site:{domain} inurl:config OR inurl:backup OR inurl:.env OR inurl:debug", "Archivos sensibles"),
        (f'site:{domain} ext:php intitle:"index of"', "Directory listing"),
        (f'site:{domain} intext:"sql syntax" OR intext:"mysql_fetch" OR intext:"ORA-"', "Errores SQL expuestos"),
        (f'site:{domain} intext:"password" OR intext:"username" filetype:txt', "Credenciales en texto"),
        (f'"@{domain}" email', "Emails del dominio"),
        (f'site:github.com "{domain}" password OR secret OR api_key OR token', "Secretos en GitHub"),
        (f'site:pastebin.com "{domain}"', "Pastes con el dominio"),
        (f'site:trello.com "{domain}"', "Boards de Trello con info del dominio"),
        (f'inurl:"{domain}" intitle:"Gitlab"', "Instancias de GitLab"),
        (f'"{domain}" site:shodan.io', "Shodan — dispositivos expuestos"),
    ]
    for dork, desc in dorks:
        print(f"  {Colors.WARNING}[{desc}]{Colors.ENDC}")
        encoded = urllib.parse.quote(dork)
        sys.stdout.buffer.write(f"    {Colors.OKGREEN}https://www.google.com/search?q={encoded}{Colors.ENDC}\n".encode('utf-8'))
        sys.stdout.buffer.flush()

# ─── FASE 8: Recomendaciones Activas ─────────────────────────────

def active_tools(domain):
    _header("FASE 8: Herramientas Activas de Enumeración (Kali)")
    tools = [
        (f"amass enum -passive -d {domain}", "Subdominios pasivos (muy completo)"),
        (f"subfinder -d {domain} -silent", "Subfinder — rápido y preciso"),
        (f"dnsx -d {domain} -a -aaaa -mx -ns -txt -silent", "Resolución masiva DNS"),
        (f"httpx -l subdominios.txt -status-code -title -tech-detect", "Detectar qué subdominios están activos"),
        (f"nmap --script dns-brute {domain}", "Brute force DNS con nmap"),
        (f"gobuster dns -d {domain} -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt", "Fuerza bruta de subdominios"),
    ]
    for cmd, desc in tools:
        print(f"  {Colors.WARNING}[{desc}]{Colors.ENDC}")
        _cmd(cmd)
        print()

# ─── Entry Point ─────────────────────────────────────────────────

def run(domain):
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO OSINT v2.0 — OBSIDIAN TIER{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"\n{Colors.OKCYAN}[*] Objetivo: {domain}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Iniciando reconocimiento pasivo completo...{Colors.ENDC}\n")

    whois_lookup(domain)
    dns_lookup(domain)
    tech_fingerprint(domain)
    subdomain_crtsh(domain)
    zone_transfer(domain)
    email_hints(domain)
    google_dorks(domain)
    active_tools(domain)

    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Una vez que tenés subdominios → python Farei_0x.py fuzz IP --vhost --domain {domain}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Para recon de puertos → python Farei_0x.py recon IP{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
