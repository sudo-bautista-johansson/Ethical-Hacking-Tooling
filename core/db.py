import sqlite3
import os

DB_NAME = "bauty_state.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tablas Originales
    c.execute('''CREATE TABLE IF NOT EXISTS hosts (ip TEXT PRIMARY KEY, os_guess TEXT, last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ports (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, port INTEGER, service TEXT, state TEXT, FOREIGN KEY(ip) REFERENCES hosts(ip))''')
    c.execute('''CREATE TABLE IF NOT EXISTS creds (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT, username TEXT, password_or_hash TEXT, type TEXT)''')
    
    # Nuevas Tablas de Inteligencia
    c.execute('''CREATE TABLE IF NOT EXISTS directories (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, path TEXT, size INTEGER, status INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exploits (id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT, url TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ad_findings (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, vulnerability TEXT, user_account TEXT)''')
    
    conn.commit()
    conn.close()

def add_host(ip):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO hosts (ip) VALUES (?)', (ip,))
    conn.commit()
    conn.close()

def add_port(ip, port, service="unknown"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM ports WHERE ip=? AND port=?', (ip, port))
    if not c.fetchone():
        c.execute('INSERT INTO ports (ip, port, service, state) VALUES (?, ?, ?, ?)', (ip, port, service, "open"))
    conn.commit()
    conn.close()

def add_cred(ip, username, password, cred_type):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO creds (ip, username, password_or_hash, type) VALUES (?, ?, ?, ?)', (ip, username, password, cred_type))
    conn.commit()
    conn.close()

# --- Nuevas Funciones de Guardado ---

def add_directory(url, path, size, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM directories WHERE url=? AND path=?', (url, path))
    if not c.fetchone():
        c.execute('INSERT INTO directories (url, path, size, status) VALUES (?, ?, ?, ?)', (url, path, size, status))
    conn.commit()
    conn.close()

def add_exploit(service, url_link, description=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM exploits WHERE url=?', (url_link,))
    if not c.fetchone():
        c.execute('INSERT INTO exploits (service, url, description) VALUES (?, ?, ?)', (service, url_link, description))
    conn.commit()
    conn.close()

def add_ad_finding(target, vuln, user):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM ad_findings WHERE vulnerability=? AND user_account=?', (vuln, user))
    if not c.fetchone():
        c.execute('INSERT INTO ad_findings (target, vulnerability, user_account) VALUES (?, ?, ?)', (target, vuln, user))
    conn.commit()
    conn.close()

def get_all_state():
    """Extrae todo el estado (viejo y nuevo) para el súper-reporte."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT * FROM hosts')
    hosts = c.fetchall()
    c.execute('SELECT * FROM ports')
    ports = c.fetchall()
    c.execute('SELECT * FROM creds')
    creds = c.fetchall()
    
    # Nuevas extracciones
    c.execute('SELECT * FROM directories')
    directories = c.fetchall()
    c.execute('SELECT * FROM exploits')
    exploits = c.fetchall()
    c.execute('SELECT * FROM ad_findings')
    ad_findings = c.fetchall()
    
    conn.close()
    return {
        "hosts": hosts, 
        "ports": ports, 
        "creds": creds,
        "directories": directories,
        "exploits": exploits,
        "ad_findings": ad_findings
    }
