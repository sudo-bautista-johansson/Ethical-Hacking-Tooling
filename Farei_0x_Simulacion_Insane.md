# ⚔️ Simulación Élite: Destrozando una Máquina "Insane" con Farei_0x

**Objetivo (Target):** Máquina `10.10.10.100` (Nombre: *Blackout* - Dificultad: Insane)
**Meta:** Comprometer el Directorio Activo completo y conseguir `user.txt` y `root.txt`.
**Tiempo Estimado con Farei_0x:** ~45 segundos de enumeración y preparación.
**Tiempo Estimado Manual (Jugador Promedio):** ~30 a 50 minutos.

---

## 🕒 Minuto 0:00 - Reconocimiento Relámpago
Acabo de encender mi VPN. No pierdo tiempo escribiendo comandos largos de Nmap.

**Comando:**
```bash
python Farei_0x.py recon 10.10.10.100
```
**Qué obtengo:**
En 3 segundos, la herramienta escanea 65,535 puertos. Me dice que están abiertos el **80 (HTTP)**, el **88 (Kerberos)** y el **445 (SMB)**. Inmediatamente, el framework guarda esta información en la base de datos `bauty_state.db`.

## 🕒 Minuto 0:05 - Evasión Web (Anti-Rabbit-Hole)
Veo un servidor web en el puerto 80. Las máquinas "Insane" siempre tienen trampas (directorios que no existen pero devuelven "200 OK" para romperte la cabeza). Dejo que la herramienta piense por mí. No le paso la IP, porque el framework ya sabe cuál es leyendo la base de datos.

**Comando:**
```bash
python Farei_0x.py fuzz
```
**Qué obtengo:**
La consola me avisa: `[!] CUIDADO: El servidor devuelve 200 OK en páginas falsas (Rabbit Hole). Aislando tamaño: 450 bytes.` 
En 15 segundos, el fuzzer revisa 5,000 rutas ignorando la basura de 450 bytes. Me escupe en verde brillante: `[Status: 200] /api/v1/debug`.
*Tiempo ahorrado: 20 minutos de frustración viendo falsos positivos.*

## 🕒 Minuto 0:20 - Caza del 0-Day
Entro a `/api/v1/debug` en mi navegador y descubro que es un servicio antiguo: `Apache OFBiz 18.12.09`. ¿Voy a Google? No, la API de GitHub es más rápida.

**Comando:**
```bash
python Farei_0x.py cve "Apache OFBiz 18.12.09"
```
**Qué obtengo:**
En 3 segundos, hace una consulta a GitHub y me devuelve el repositorio número 1 con 150 estrellas que es un RCE (Ejecución de Código Remoto). Copio el comando `git clone https://github.com/.../OFBiz-RCE` que me da la herramienta y descargo el exploit.

## 🕒 Minuto 0:25 - Generación del Payload Perfecto
El exploit RCE me pide un comando de consola para ejecutar. Si escribo un `nc -e /bin/bash` normal, el Firewall de la máquina "Insane" lo va a bloquear. Necesito algo ofuscado.

**Comando:**
```bash
python Farei_0x.py payload 10.10.14.5 4444 --base64
```
**Qué obtengo:**
La herramienta imprime instantáneamente 10 Reverse Shells diferentes en Base64. Copio la de `Bash (TCP)` y la pego en mi exploit. Lanzo el ataque y... **¡BOOM! Tengo shell. Entré a la máquina.**

## 🕒 Minuto 0:35 - Dominando el Active Directory
Ya estoy dentro como un usuario de bajos privilegios. Descubro que hay un archivo `.json` de BloodHound olvidado en el servidor por un administrador descuidado. Lo descargo a mi PC. 
Normalmente, tendría que instalar Neo4j, levantar la base de datos gráfica (que toma minutos) y hacer consultas a mano. En vez de eso, uso la magia oscura de Farei_0x.

**Comando:**
```bash
python Farei_0x.py ad 10.10.10.100 corp.local --parse users.json
```
**Qué obtengo:**
En 1 maldito segundo, la herramienta lee miles de líneas de JSON y me escupe un texto rojo brillante: `[!] VULNERABILIDAD CRÍTICA: AS-REP Roasting Posible en el usuario 'svc_admin'`.
El framework acaba de encontrarme el camino directo al Administrador del Dominio sin tener que mirar un solo gráfico.

## 🕒 Minuto 0:40 - Rompiendo Criptografía
Uso la herramienta Impacket (cuyo comando exacto me lo sugirió el módulo `ad` hace un segundo) para extraer el hash de `svc_admin`. Lo guardo en un archivo de texto llamado `hash.txt`.

**Comando:**
```bash
python Farei_0x.py hashes hash.txt
```
**Qué obtengo:**
La herramienta limpia el texto, identifica que es un hash de tipo AS-REP y me dice: `"Sugerencia: hashcat -m 18200 hash.txt rockyou.txt"`. Ejecuto ese comando en Hashcat, rompo la contraseña y me convierto en Domain Admin. **Máquina Pwned.**

## 🕒 Minuto 0:45 - El Reporte Profesional
La máquina cayó. He obtenido la flag de Root. Ahora quiero documentarlo para mi Obsidian.

**Comando:**
```bash
python Farei_0x.py report
```
**Qué obtengo:**
Se genera automáticamente un `Bauty_Report.md`. Cuando lo abro, veo tablas perfectas con la IP `10.10.10.100`, los puertos `80, 88, 445`, la ruta `/api/v1/debug` descubierta, el link exacto de GitHub del exploit de Apache OFBiz que usé, y la vulnerabilidad de "AS-REP Roasting" del usuario `svc_admin`. Todo tabulado.

---

### 🏆 Conclusión de la Simulación
En **menos de 1 minuto** de tiempo de interacción con la terminal, obtuve toda la inteligencia, los exploits y las vulnerabilidades críticas que un jugador normal tardaría casi una hora en descubrir usando herramientas manuales y páginas web de Google. El resto del tiempo simplemente me dediqué a lanzar los ataques. **Esa es la diferencia entre jugar en Plata y jugar en Obsidian.**
