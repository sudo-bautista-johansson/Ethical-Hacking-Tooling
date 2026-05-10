# 🦇 Farei_0x - Obsidian Tier CTF Arsenal

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Bash](https://img.shields.io/badge/Bash-Script-green)
![PowerShell](https://img.shields.io/badge/PowerShell-Native-blueviolet)
![Status](https://img.shields.io/badge/Status-Active-success)

**Farei_0x** es un framework de automatización ofensiva de alto rendimiento diseñado exclusivamente para competiciones de Capture The Flag (CTF) como TryHackMe, HackTheBox y entornos de laboratorio controlados. 

Su filosofía es simple: **Velocidad de élite y cero fricción.** Elimina el tiempo muerto de la enumeración manual, centraliza el descubrimiento en una base de datos local (SQLite) y aplica lógicas de evasión avanzada (Anti-Rabbit-Hole) para que puedas concentrarte en lo que importa: hackear la lógica de la máquina.

---

## ⚠️ DESCARGO DE RESPONSABILIDAD LEGAL (DISCLAIMER)
> **ESTRICTAMENTE PARA USO ÉTICO Y EDUCATIVO.**
> Este conjunto de herramientas fue creado **única y exclusivamente** para ser utilizado en entornos de laboratorio legales (CTFs), entornos autorizados para auditorías de seguridad (Red Teaming) y plataformas educativas.
> 
> El autor **NO se hace responsable** del mal uso, daño o implicaciones legales que puedan derivarse de la utilización de estas herramientas contra infraestructuras sin el consentimiento expreso y por escrito de los propietarios. Si descargas este software, asumes total responsabilidad de tus acciones. **No seas un cibercriminal, usa esto para aprender.**

---

## 🧠 ¿Qué hace a Farei_0x diferente? (Características Core)

A diferencia de tener decenas de scripts de Python y Bash tirados por tu escritorio, `Farei_0x` orquesta todo mediante un único punto de entrada: `Farei_0x.py`.

1. **Memoria de Estado (SQLite):** El módulo de escaneo guarda lo que descubre. El módulo de fuzzing lee esos descubrimientos y ataca de forma autónoma. No tienes que copiar y pegar IPs todo el tiempo.
2. **Fuzzer "Anti-Rabbit-Hole":** Las máquinas nivel *Insane* suelen devolver código HTTP `200 OK` en rutas que no existen para inundar tus escaneos. `Farei_0x` detecta esto mediante auto-calibración previa, aísla el peso de la página falsa y la ignora durante el ataque real.
3. **Cero Dependencias Pesadas:** Olvídate de bases de datos pesadas en segundo plano como Neo4j o PostgreSQL. `Farei_0x` parsea JSONs masivos en memoria con Python puro.
4. **Auto-Reporte:** Al terminar la máquina, extrae todo lo que hiciste y te genera un archivo Markdown impecable para tus Writeups.

---

## 🛠️ Uso de Módulos Centrales (`Farei_0x.py`)

Todos estos comandos se ejecutan desde tu máquina atacante (Kali Linux / Parrot OS / WSL).

### 1. RECON (`Farei_0x.py recon <IP>`)
Lanza un Nmap de 65535 puertos a velocidad máxima (`--min-rate 5000`). Parsea los puertos abiertos y los guarda en la base de datos interna.
*   **Ejemplo:** `python3 Farei_0x.py recon 10.10.10.5`

### 2. FUZZ (`Farei_0x.py fuzz`)
Ejecuta un fuzzer web asíncrono ultra-rápido. Si no le pasas una IP, ataca automáticamente a la IP web guardada por el módulo `recon`. Aplica evasión Anti-Rabbit-Hole.
*   **Ejemplo:** `python3 Farei_0x.py fuzz`

### 3. PAYLOAD (`Farei_0x.py payload <Tu_IP> <Puerto>`)
Genera un arsenal de **Reverse Shells** listas para copiar y pegar en los lenguajes más utilizados e inusuales (Bash, Python, Perl, Ruby, Awk, Socat, CMD, PowerShell).
*   **Ejemplo:** `python3 Farei_0x.py payload 10.10.14.5 4444`

### 4. CRYPTO (`Farei_0x.py crypto "<Hash/Cadena>"`)
Un cuchillo suizo criptográfico. Descifra automáticamente Base64, Base32, Hexadecimal, URL Encode y fuerza bruta de rotaciones (ROT1-25). Si encuentra una flag (ej. `THM{`), te avisa en verde.
*   **Ejemplo:** `python3 Farei_0x.py crypto "VEhNe2hhY2tlZH0="`

### 5. HASHES (`Farei_0x.py hashes <Archivo>`)
Le pasas un volcado de base de datos o un `/etc/shadow`. Limpia la basura binaria, extrae los hashes válidos, identifica si es MD5/Bcrypt/SHA512 y te escupe el comando exacto de `hashcat` para romperlo.
*   **Ejemplo:** `python3 Farei_0x.py hashes dump.sql`

### 6. AUTO-CVE (`Farei_0x.py cve "<Servicio>"`)
Conecta con la API REST oficial de GitHub. Busca repositorios que contengan exploits de 0-days (PoCs) para la versión exacta de tu servicio y te da el comando `git clone` del repositorio más votado de internet.
*   **Ejemplo:** `python3 Farei_0x.py cve "Apache 2.4.49"`

### 7. AD-CORE (`Farei_0x.py ad <IP_DC> <Dominio>`)
Automatización extrema para Active Directory. Te da los comandos exactos de Impacket para *AS-REP Roasting* y *Kerberoasting*. **Nivel Dios:** Permite analizar archivos JSON de BloodHound en offline para encontrar caminos críticos sin usar Neo4j.
*   **Ejemplo:** `python3 Farei_0x.py ad 10.10.10.10 corp.local --parse users.json`

### 8. REPORT (`Farei_0x.py report`)
Lee la base de datos de tu sesión actual y te genera el archivo `Bauty_Report.md` con tus IPs, puertos y credenciales para tus apuntes de Obsidian o GitHub.
*   **Ejemplo:** `python3 Farei_0x.py report`

---

## 🦠 Herramientas "Standalone" (Para la Víctima)

A diferencia del Core, estos archivos están pensados para subirse y ejecutarse **dentro de la máquina víctima** para escalar privilegios o mantener persistencia.

*   **`LSE-Exhaustivo.sh`**: El escáner definitivo para Linux. Detecta binarios SUID raros, tareas Cron, Capabilities y contraseñas ocultas. Ejecutar con `./LSE-Exhaustivo.sh`.
*   **`WinPrivEsc.ps1`**: Buscador de rutas no entrecomilladas (*Unquoted Service Paths*), credenciales de AutoLogon e historiales de PowerShell en entornos Windows.
*   **`Exfil-Script.cpp`**: Código en C++ para ser compilado en un binario. Exfiltra las flags `user.txt` y `root.txt` silenciosamente usando Webhooks de Discord.
*   **`Auto-Pivot.py`**: Utilidad matemática para calcular y escupir comandos de `Chisel` y SSH Port Forwarding perfectos.
*   **`PCAP-Analyzer.py`**: Analizador de capturas de red `.pcap`. Busca contraseñas de FTP y HTTP viajando en texto plano por la red interceptada.
*   **`Shell-Stabilizer.py`**: Una guía/script paso a paso para estabilizar tu Netcat reversa en una TTY interactiva y que `CTRL+C` no mate tu conexión.

---

## 💻 Requisitos e Instalación

Para que el framework funcione a su máxima capacidad:
1. Python 3.8+ instalado.
2. Nmap instalado en el sistema (`sudo apt install nmap`).
3. (Opcional) Instalar librería asíncrona para Fuzzer: `pip install aiohttp`

```bash
# Clonar el repositorio
git clone https://github.com/sudo-bautista-johansson/Ethical-Hacking-Tooling.git
cd Farei_0x
# Ver comandos disponibles
python3 Farei_0x.py -h
```

---
*Hecho con agresividad competitiva para romper las ligas de CTFs.* 🦇
