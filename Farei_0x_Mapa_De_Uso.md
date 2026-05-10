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
