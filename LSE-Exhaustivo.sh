#!/bin/bash
# LSE Exhaustivo - Analizador de Privilegios Linux Ligero
# Creado para CTFs - No requiere dependencias.

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  LSE Exhaustivo (Linux Smart Enumeration v2)   ${NC}"
echo -e "${CYAN}================================================${NC}"

# 1. Info Básica
echo -e "\n${YELLOW}[+] Sistema Operativo y Kernel:${NC}"
uname -a
cat /etc/issue 2>/dev/null | head -n 1
cat /etc/os-release 2>/dev/null | grep PRETTY_NAME

# 2. Usuarios y Grupos
echo -e "\n${YELLOW}[+] Quién soy y mis grupos:${NC}"
id

echo -e "\n${YELLOW}[+] Usuarios con consola interactiva (sh/bash):${NC}"
cat /etc/passwd | grep "sh$"

# 3. Permisos de Sudo
echo -e "\n${YELLOW}[+] Reglas de Sudo (sudo -l):${NC}"
sudo -l 2>/dev/null || echo -e "${RED}No se requiere o no se puede hacer sudo -l sin contraseña.${NC}"

# 4. Tareas Cron
echo -e "\n${YELLOW}[+] Tareas Cron en el sistema:${NC}"
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.* 2>/dev/null

# 5. Binarios SUID (Muy importante en CTFs)
echo -e "\n${YELLOW}[+] Binarios SUID (buscando vectores GTFOBins):${NC}"
# Excluimos los muy comunes que no suelen ser vulnerables (mount, su, passwd, ping) para reducir ruido
find / -perm -4000 -type f 2>/dev/null | grep -v "snap" | grep -v "mount" | grep -v "ping" | grep -v "su" | grep -v "passwd"

# 6. Capabilities (Alternativa a SUID)
echo -e "\n${YELLOW}[+] Linux Capabilities:${NC}"
getcap -r / 2>/dev/null

# 7. Archivos interesantes (Historiales, Keys)
echo -e "\n${YELLOW}[+] Archivos de Historial (.bash_history, .mysql_history, etc):${NC}"
find /home /root -name ".*history" -readable 2>/dev/null

echo -e "\n${YELLOW}[+] Archivos de Configuración o Backups (.bak, .conf):${NC}"
find /opt /var/www -name "*.conf" -o -name "*.bak" 2>/dev/null | head -n 20

echo -e "\n${YELLOW}[+] Llaves SSH Privadas legibles:${NC}"
find / -name "id_rsa" -o -name "id_ed25519" -readable 2>/dev/null

# 8. Servicios corriendo internamente (Puertos locales)
echo -e "\n${YELLOW}[+] Puertos a la escucha localmente (Posible Pivoting):${NC}"
ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null

# 9. Archivos World-Writeable (modificables por cualquiera)
echo -e "\n${YELLOW}[+] Archivos con permisos de escritura para todos (World-Writeable) en /etc y /opt:${NC}"
find /etc /opt -type f -perm -o+w 2>/dev/null

echo -e "\n${CYAN}================================================${NC}"
echo -e "${GREEN}Enumeración finalizada. Revisa los resultados cuidadosamente.${NC}"
