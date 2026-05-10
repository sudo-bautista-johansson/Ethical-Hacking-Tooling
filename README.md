# 🦇 Farei_0x — Obsidian Tier CTF Arsenal

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Modules](https://img.shields.io/badge/Modules-15-red)
![Tier](https://img.shields.io/badge/Tier-Obsidian-black)
![Status](https://img.shields.io/badge/Status-Active-success)

**Farei_0x** es un framework de automatización ofensiva de alto rendimiento diseñado exclusivamente para competiciones CTF (TryHackMe, HackTheBox) y entornos de laboratorio controlados.

Su filosofía es simple: **Velocidad de élite y cero fricción.** Elimina el tiempo muerto de la enumeración manual, centraliza los hallazgos en SQLite y aplica lógicas de evasión avanzada para que puedas concentrarte en lo que importa: hackear.

---

## ⚠️ DISCLAIMER LEGAL

> **ESTRICTAMENTE PARA USO ÉTICO Y EDUCATIVO.**
> Creado únicamente para CTFs, laboratorios legales y auditorías autorizadas.
> El autor **NO se hace responsable** del mal uso. Si usás esto, asumís total responsabilidad.

---

## 🧠 ¿Qué hace a Farei_0x diferente?

1. **Memoria de Estado (SQLite):** Recon guarda, Fuzzer lee y ataca. No copiás IPs todo el tiempo.
2. **Fuzzer Anti-Rabbit-Hole:** Calibra contra páginas falsas antes de atacar. No te perdés en 200 OK que no existen.
3. **3 Fases de Recon:** Fast Scan → Deep Service Scan → Sugerencias inteligentes según servicios encontrados.
4. **Auto-Reporte:** Al terminar la máquina, genera `Bauty_Report.md` con todos los hallazgos.
5. **15 Módulos Obsidian:** De recon hasta IA de combate, todo en un solo framework.

---

## 🛠️ Módulos — Referencia Completa

### RECONOCIMIENTO

#### `recon` — Escaneo Inteligente 3 Fases
```bash
python3 Farei_0x.py recon 10.10.10.X
```
- Fase 1: Nmap `-p- --min-rate 5000` (todos los puertos)
- Fase 2: `-sCV` solo en puertos abiertos (versiones + scripts)
- Fase 3: Sugerencias automáticas según servicios + detección de CVEs conocidos

#### `fuzz` — Fuzzing Web + VHost
```bash
python3 Farei_0x.py fuzz 10.10.10.X                          # Directorios
python3 Farei_0x.py fuzz 10.10.10.X --vhost --domain htb.htb  # VHosts/Subdominios
python3 Farei_0x.py fuzz 10.10.10.X -w /ruta/wordlist.txt     # Wordlist custom
```
- Async 50 conexiones simultáneas
- Anti-Rabbit-Hole automático
- VHost: detecta cambios de +50 bytes en respuestas HTTP

#### `osint` — OSINT Pasivo Completo
```bash
python3 Farei_0x.py osint target.htb
```
- WHOIS via RDAP, DNS records (A/MX/NS/TXT/SRV)
- Fingerprinting de tecnologías web (headers + body)
- Subdominios via Certificate Transparency (crt.sh) — sin fuerza bruta
- Google Dorks avanzados (GitHub secrets, Shodan, Pastebin)
- Email harvesting (theHarvester + Hunter.io)

---

### EXPLOTACIÓN

#### `cve` — Auto-CVE con NVD + GitHub
```bash
python3 Farei_0x.py cve "Apache 2.4.49"    # Por servicio
python3 Farei_0x.py cve "CVE-2021-41773"   # Por CVE-ID directo
```
- Consulta API oficial NIST NVD v2.0
- Score CVSS + Severidad (CRITICAL/HIGH/MEDIUM)
- Busca PoCs en GitHub específicos para los CVEs encontrados
- Links de PacketStorm, Exploit-DB, Rapid7

#### `sqli` — Inyección SQL + SSTI
```bash
python3 Farei_0x.py sqli --url "http://10.10.10.X/login"
```
- Payloads de detección para MySQL, MSSQL, PostgreSQL, Oracle, SQLite, **MongoDB/NoSQL**
- UNION-based step by step (columnas → dump → file read → webshell)
- WAF bypass techniques (space2comment, case mix, double encode)
- sqlmap automatizado con tamper scripts
- **SSTI payloads** (Jinja2, Twig, Freemarker, Velocity)

#### `payload` — Reverse Shells + TTY Upgrade
```bash
python3 Farei_0x.py payload 10.10.14.5 4444          # 10 shells
python3 Farei_0x.py payload 10.10.14.5 4444 --base64  # Evadir WAF
python3 Farei_0x.py payload --upgrade                 # TTY upgrade guide
```
- 10 tipos de shell (Bash, Python, Perl, Ruby, Awk, Socat, PowerShell, CMD...)
- Base64 encoding (PowerShell usa UTF-16LE automático)
- URL encoding para exploits web

---

### POST-EXPLOTACIÓN

#### `privesc` — Escalada de Privilegios
```bash
python3 Farei_0x.py privesc --os linux    # 15+ vectores Linux
python3 Farei_0x.py privesc --os windows  # 12+ vectores Windows
```
**Linux:** SUID GTFOBins (15 binarios), sudo abuses (12), grupos peligrosos (docker/lxd/disk/shadow), cron wildcard injection, path hijacking, kernel exploits (DirtyPipe, PwnKit), LinPEAS  
**Windows:** Potato attacks (PrintSpoofer/GodPotato/JuicyPotato), SeImpersonate, SeBackupPrivilege, AlwaysInstallElevated, Unquoted Service Path, WinPEAS

#### `payload --upgrade` — Shell Stabilization + Pivoting
```bash
python3 Farei_0x.py payload --upgrade
```
- Python PTY + stty raw, Socat TTY perfecta, rlwrap para Windows
- Port Forwarding: SSH local/remote, **Chisel**, **Ligolo-ng**
- Transferencia de archivos: HTTP, SMB, Base64, certutil, wget/curl

#### `smb` — Enumeración SMB Completa
```bash
python3 Farei_0x.py smb 10.10.10.X                      # Sesión nula
python3 Farei_0x.py smb 10.10.10.X -u admin -p Pass123  # Con credenciales
```
- Null session: enum4linux-ng, rpcclient, ldapdomaindump, lookupsid
- Con credenciales: smbmap spider, secretsdump SAM/LSA/NTDS, BloodHound
- Ataques: AS-REP Roasting, Kerberoasting, ZeroLogon, NTLM Relay
- Ejecución: psexec, wmiexec, smbexec, evil-winrm, Pass-the-Hash, DCSync

---

### ANÁLISIS CRIPTOGRÁFICO

#### `crypto` — Decodificador Recursivo
```bash
python3 Farei_0x.py crypto "VkVoTmUyUnZkV0pzWlgwPQ=="
```
- Base64, Base32, Hex, URL Encode (auto + recursivo hasta 5 capas)
- ROT1-25 con detección automática de flags
- Detección binaria + extracción a .bin

#### `encoder` — Cifrados Clásicos + XOR Brute Force
```bash
python3 Farei_0x.py encoder "... --- --"            # Morse
python3 Farei_0x.py encoder "ZYLWREVHSZO"            # Atbash auto
python3 Farei_0x.py encoder "48656c6c6f"             # XOR brute force
python3 Farei_0x.py encoder "TEXTO" --key CLAVE      # Vigenere
```
- Morse, Atbash, Vigenere, Rail Fence (2-5 rails), Bacon Cipher
- ROT-47, Binary, ASCII Decimal
- **XOR single-byte brute force** (todos los keys 0x01-0xFF)
- Auto-detección del tipo de cifrado

---

### CEREBRO TÁCTICO (IA)

#### `ai` — Entidad Ofensiva Interactiva
```bash
# Exportar primero la API Key de Google Gemini
$env:GEMINI_API_KEY="TU_API_KEY"  # Windows
export GEMINI_API_KEY="TU_API_KEY" # Linux

python3 Farei_0x.py ai
```
- **Memoria Contextual:** Lee y comprende el estado completo de tu SQLite (`bauty_state.db`).
- **Auto-Coder:** Te programa exploits personalizados (ej. RCE) sobre la marcha en base a versiones descubiertas.
- **Modo Chat:** Loop interactivo para guiarte paso a paso durante toda la máquina.

---

### OTROS

#### `hashes` — Identificador + Extractor (17 tipos)
```bash
python3 Farei_0x.py hashes /etc/shadow
python3 Farei_0x.py hashes secretsdump.txt
```
Detecta: bcrypt, SHA512-Crypt, SHA256-Crypt, MD5-Crypt, PHPass (WordPress), **Kerberos AS-REP (18200)**, **Kerberoast (13100)**, NTLMv1, **NTLMv2 (5600)**, MySQL, SHA-512/256/1, MD5/NTLM  
Parsea formatos: `/etc/shadow`, secretsdump, Responder NTLMv2

#### `ad` — Active Directory
```bash
python3 Farei_0x.py ad 10.10.10.X corp.local
python3 Farei_0x.py ad --parse users.json
```
- Comandos Impacket: AS-REP, Kerberoast, BloodHound, secretsdump, PSExec
- Parser BloodHound offline (sin Neo4j): detecta usuarios vulnerables

#### `crypto` + `report`
```bash
python3 Farei_0x.py report   # Genera Bauty_Report.md con todos los hallazgos
```

---

## 📋 Cheatsheet Rápido

```bash
python3 Farei_0x.py recon 10.10.10.X
python3 Farei_0x.py fuzz 10.10.10.X
python3 Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb
python3 Farei_0x.py osint target.htb
python3 Farei_0x.py cve "Apache 2.4.49"
python3 Farei_0x.py sqli --url "http://10.10.10.X/login"
python3 Farei_0x.py smb 10.10.10.X
python3 Farei_0x.py payload 10.10.14.5 4444 --base64
python3 Farei_0x.py payload --upgrade
python3 Farei_0x.py privesc --os linux
python3 Farei_0x.py privesc --os windows
python3 Farei_0x.py crypto "VEhNe2ZsYWd9"
python3 Farei_0x.py encoder "... --- ..."
python3 Farei_0x.py hashes /etc/shadow
python3 Farei_0x.py ad 10.10.10.X corp.local
python3 Farei_0x.py ai
python3 Farei_0x.py report
```

---

## 💻 Instalación

```bash
git clone https://github.com/sudo-bautista-johansson/Ethical-Hacking-Tooling.git
cd "Ethical Hacking tooling"
pip install -r requirements.txt
python3 Farei_0x.py --help
```

**Dependencias:**
- Python 3.8+
- `pip install aiohttp` (Fuzzer async)
- Nmap en el PATH (`sudo apt install nmap`)
- Herramientas opcionales: impacket, crackmapexec, evil-winrm, enum4linux-ng, bloodhound-python

---

*Hecho con agresividad competitiva para speedrunear Insane VMs.* 🦇💀
