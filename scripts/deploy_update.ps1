<#
.SYNOPSIS
    Скрипт розгортання (Deployment) та оновлення Cisco Router Wizard на Windows Terminal Server.
.DESCRIPTION
    Цей скрипт автоматизує:
    1. Створення резервної копії попереднього білда
    2. Зупинку всіх активних процесів старого додатку
    3. Копіювання нового білда на Production
    4. Опціональний запуск
#>

$serviceName = "CiscoRouterWizard"
$installDir = "C:\Program Files\CiscoRouterWizard"
$backupDir = "C:\Backups\CiscoRouterWizard"
$exeName = "CiscoRouterWizard.exe"
$sourceExe = ".\dist\$exeName"

Write-Host "[INFO] Starting Automated Deployment for $serviceName..." -ForegroundColor Cyan

# 1. Перевірка наявності нового білда
if (!(Test-Path $sourceExe)) {
    Write-Host "[ERROR] New build not found at $sourceExe. Please run PyInstaller (or CI/CD action) first." -ForegroundColor Red
    exit 1
}

# 2. Backup existing (Резервне копіювання)
if (Test-Path "$installDir\$exeName") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    if (!(Test-Path $backupDir)) { New-Item -ItemType Directory -Force -Path $backupDir | Out-Null }
    
    $backupPath = "$backupDir\${exeName}_$timestamp.bak"
    Copy-Item "$installDir\$exeName" $backupPath -Force
    Write-Host "[INFO] Successful Backup: Created $backupPath" -ForegroundColor Green
}

# 3. Stop running instances (Вбивство активних процесів інженерів)
Write-Host "[INFO] Stopping existing $serviceName processes across all sessions..."
Get-Process -Name $serviceName -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2 # Зачекати на звільнення файлу дескрипторами

# 4. Deploy new code (Копіювання нового коду)
if (!(Test-Path $installDir)) { New-Item -ItemType Directory -Force -Path $installDir | Out-Null }
Copy-Item $sourceExe "$installDir\$exeName" -Force
Write-Host "[INFO] Deployed new executable to $installDir successfully." -ForegroundColor Green

Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Cyan
