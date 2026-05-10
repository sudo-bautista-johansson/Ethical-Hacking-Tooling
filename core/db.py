import sqlite3
import os

DB_NAME = "bauty_state.db"

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabla para Hosts (IPs y su estado)
    c.execute('''
        CREATE TABLE IF NOT EXISTS hosts (
            ip TEXT PRIMARY KEY,
            os_guess TEXT,
            last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla para Puertos Abiertos
    c.execute('''
        CREATE TABLE IF NOT EXISTS ports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            port INTEGER,
            service TEXT,
            state TEXT,
            FOREIGN KEY(ip) REFERENCES hosts(ip)
        )
    ''')
    
    # Tabla para Credenciales/Hashes encontrados
    c.execute('''
        CREATE TABLE IF NOT EXISTS creds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            username TEXT,
            password_or_hash TEXT,
            type TEXT,
            FOREIGN KEY(ip) REFERENCES hosts(ip)
        )
    ''')
    
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
    # Evitar duplicados
    c.execute('SELECT id FROM ports WHERE ip=? AND port=?', (ip, port))
    if not c.fetchone():
        c.execute('INSERT INTO ports (ip, port, service, state) VALUES (?, ?, ?, ?)', (ip, port, service, "open"))
    conn.commit()
    conn.close()

def get_open_ports(ip):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT port, service FROM ports WHERE ip=?', (ip,))
    results = c.fetchall()
    conn.close()
    return results

def add_cred(ip, username, password, cred_type):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO creds (ip, username, password_or_hash, type) VALUES (?, ?, ?, ?)', 
              (ip, username, password, cred_type))
    conn.commit()
    conn.close()

def get_all_state():
    """Extrae todo el estado para generar reportes."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('SELECT * FROM hosts')
    hosts = c.fetchall()
    
    c.execute('SELECT * FROM ports')
    ports = c.fetchall()
    
    c.execute('SELECT * FROM creds')
    creds = c.fetchall()
    
    conn.close()
    return {"hosts": hosts, "ports": ports, "creds": creds}
