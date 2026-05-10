<#
.SYNOPSIS
    WinPrivEsc - Escáner de Escalada de Privilegios básico para Windows (CTFs).
.DESCRIPTION
    Busca vulnerabilidades comunes en entornos Windows como Unquoted Service Paths,
    AlwaysInstallElevated, y archivos interesantes de contraseñas.
#>

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     WinPrivEsc - Windows Smart Enumeration     " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Información Básica del Sistema
Write-Host "[+] Información del Sistema:" -ForegroundColor Yellow
systeminfo | Select-String "OS Name|OS Version|System Type" | Write-Host
Write-Host ""

# 2. Usuarios y Grupos Locales
Write-Host "[+] Mi Usuario y Privilegios:" -ForegroundColor Yellow
whoami /priv | Select-String "SeImpersonatePrivilege|SeAssignPrimaryTokenPrivilege|SeBackupPrivilege|SeRestorePrivilege|SeTakeOwnershipPrivilege|SeLoadDriverPrivilege|SeDebugPrivilege"
If ($?) { Write-Host "  -> ¡Posible vector de Potato (Juicy/Rogue) detectado!" -ForegroundColor Red }
Write-Host ""

# 3. AlwaysInstallElevated (Registro)
Write-Host "[+] Verificando AlwaysInstallElevated (Permite instalar .msi como SYSTEM):" -ForegroundColor Yellow
$reg1 = reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>$null
$reg2 = reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>$null

if ($reg1 -match "0x1" -and $reg2 -match "0x1") {
    Write-Host "  -> ¡VULNERABLE! Ambos registros están en 1. Puedes crear un MSI malicioso con msfvenom." -ForegroundColor Red
} else {
    Write-Host "  -> No vulnerable a AlwaysInstallElevated." -ForegroundColor Green
}
Write-Host ""

# 4. Unquoted Service Paths
Write-Host "[+] Buscando Unquoted Service Paths (Servicios sin comillas con espacios en la ruta):" -ForegroundColor Yellow
Get-CimInstance Win32_Service | 
    Where-Object {$_.PathName -notmatch '^"' -and $_.PathName -match ' ' -and $_.PathName -notmatch 'C:\\Windows\\'} | 
    Select-Object Name, PathName, StartMode | Format-List
Write-Host ""

# 5. Búsqueda de contraseñas en archivos (Autologin)
Write-Host "[+] Buscando contraseñas en el Registro (AutoAdminLogon):" -ForegroundColor Yellow
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" 2>$null | Select-String "DefaultUserName|DefaultPassword"
Write-Host ""

# 6. Historial de PowerShell
Write-Host "[+] Revisando Historial de PowerShell (PSReadLine):" -ForegroundColor Yellow
$historyPath = (Get-PSReadLineOption).HistorySavePath
if (Test-Path $historyPath) {
    Write-Host "  -> Archivo de historial encontrado en: $historyPath" -ForegroundColor Cyan
    Write-Host "  -> Mostrando últimas 5 líneas:"
    Get-Content $historyPath -Tail 5 | Write-Host -ForegroundColor Gray
} else {
    Write-Host "  -> No se encontró historial." -ForegroundColor Green
}
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Enumeración finalizada." -ForegroundColor Green
