#!/usr/bin/env python3
import argparse
import sys
import os

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(num, desc, command=None):
    print(f"\n{Colors.WARNING}Paso {num}:{Colors.ENDC} {desc}")
    if command:
        print(f"{Colors.OKGREEN}{command}{Colors.ENDC}")

def main():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("=================================================")
    print("  TTY SHELL STABILIZER (Magia Negra para CTFs)   ")
    print("=================================================")
    print(f"{Colors.ENDC}")
    
    print("Acabas de recibir una Reverse Shell ciega (sh o bash tonta).")
    print("Sigue estos pasos EXACTOS en tu terminal para estabilizarla:\n")
    
    print_step(1, "Spawnea una consola PTY interactiva usando Python. Escribe esto en la shell de la víctima:",
               "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'")
               
    print_step(2, "Pon la shell en segundo plano pulsando:",
               "CTRL + Z")
               
    print_step(3, "Configura tu propia terminal (atacante) para pasar las pulsaciones crudas a la víctima:",
               "stty raw -echo; fg")
               
    print_step(4, "Una vez que vuelva a aparecer la shell, resetea la terminal:",
               "reset")
               
    print_step(5, "Configura las variables de entorno para que funcionen atajos como CTRL+L o nano/vim:",
               "export TERM=xterm-256color")
               
    # Opcional: ajustar filas y columnas
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        print_step(6, f"(Opcional) Ajusta el tamaño de la terminal a tu pantalla actual ({rows}x{columns}):",
                   f"stty rows {rows} columns {columns}")
    except:
        pass
        
    print(f"\n{Colors.OKCYAN}[+] ¡Listo! Ahora tienes una shell 100% interactiva donde funciona el autocompletado y CTRL+C no te tirará la conexión.{Colors.ENDC}")

if __name__ == "__main__":
    main()
