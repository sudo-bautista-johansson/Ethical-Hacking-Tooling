# Simulador de Base de Datos para Farei_AI

PowerShell tiene problemas al interpretar las comillas simples y dobles directamente en línea. Para evitar el error de sintaxis (`OperationalError: near ".10": syntax error`), la forma más segura y limpia es crear un pequeño script de Python temporal o correr el comando con el formato correcto de comillas.

## Opción 1: El comando corregido para PowerShell
Copia y pega este bloque entero en tu consola PowerShell. Utiliza comillas triples (`"""`) de Python para envolver el script y evitar conflictos con la terminal de Windows:

```powershell
python -c """
import sqlite3
conn = sqlite3.connect('bauty_state.db')
c = conn.cursor()
c.execute('INSERT OR IGNORE INTO hosts (ip) VALUES (\"10.10.10.15\")')
c.execute('INSERT INTO ports (ip, port, service, state) VALUES (\"10.10.10.15\", 80, \"http Apache 2.4.49\", \"open\")')
c.execute('INSERT INTO ports (ip, port, service, state) VALUES (\"10.10.10.15\", 445, \"smb\", \"open\")')
c.execute('INSERT INTO ad_findings (target, vulnerability, user_account) VALUES (\"DOMINIO.LOCAL\", \"AS-REP Roasting\", \"j.smith\")')
conn.commit()
conn.close()
print('DB Simulada con éxito')
"""
```

---

## Opción 2: Ejecutar el script (Recomendado)
Si el comando de arriba sigue fallando por temas de PowerShell, simplemente crea un archivo llamado `simular.py` en la carpeta de tu framework con este código:

```python
import sqlite3

conn = sqlite3.connect('bauty_state.db')
c = conn.cursor()

# Inyectar Host
c.execute("INSERT OR IGNORE INTO hosts (ip) VALUES ('10.10.10.15')")

# Inyectar Puertos y Servicios
c.execute("INSERT INTO ports (ip, port, service, state) VALUES ('10.10.10.15', 80, 'http Apache 2.4.49', 'open')")
c.execute("INSERT INTO ports (ip, port, service, state) VALUES ('10.10.10.15', 445, 'smb', 'open')")

# Inyectar vulnerabilidad de Active Directory
c.execute("INSERT INTO ad_findings (target, vulnerability, user_account) VALUES ('DOMINIO.LOCAL', 'AS-REP Roasting', 'j.smith')")

conn.commit()
conn.close()
print("DB Simulada con éxito. Ya puedes probar Farei_AI.")
```

Y luego ejecútalo normalmente:
```bash
python simular.py
```

### ¿Qué hacer después?
Entra al asistente de IA con `python Farei_0x.py ai` y pruébalo haciéndole esta pregunta exacta:
> *Revisá nuestra base de datos actual. ¿Cuáles son los dos vectores de ataque más críticos que tenemos y con qué herramientas exactas de mi framework Farei_0x o Kali los exploto?*
