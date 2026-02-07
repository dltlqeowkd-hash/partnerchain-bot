<#
.SYNOPSIS
    Hyper-V One-Click Setup (Host Side)
    
.DESCRIPTION
    1. Checks for Master.vhdx, Chrome, VPN installers.
    2. Creates 5 VMs (Bot_VM_1 to 5) using Differencing Disks.
    3. Mounts each disk and injects the Bot software.
    4. Sets up auto-start on first boot.
    
.NOTES
    Run as Administrator.
#>

$ErrorActionPreference = "Stop"
[console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 1. Admin Check
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "관리자 권한이 필요합니다. 관리자 권한으로 재실행합니다..."
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# 2. Configuration & Paths
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Definition # D:\bot\tools
$BotSourceDir = "D:\bot\최종ver\회사용\NaverShoppingBot"
$MasterVHD = Join-Path $BaseDir "Master.vhdx"
$ChromeInst = Join-Path $BaseDir "ChromeStandaloneSetup64.exe"
$VPNInst = Join-Path $BaseDir "VPNSetup.exe"

$NetSwitchName = "Default Switch" # Or change to your switch
$VMCount = 5
$VM_Prefix = "Bot_VM"

Write-Host "=== One-Click Hyper-V Setup ===" -ForegroundColor Cyan

# 3. Validation
$Missing = @()
if (-not (Test-Path $MasterVHD)) { $Missing += "Master.vhdx (가상윈도우 원본)" }
if (-not (Test-Path $ChromeInst)) { $Missing += "ChromeStandaloneSetup64.exe (크롬 설치파일)" }
if (-not (Test-Path $VPNInst)) { $Missing += "VPNSetup.exe (VPN 설치파일)" }
if (-not (Test-Path $BotSourceDir)) { $Missing += "NaverShoppingBot (봇 프로그램 폴더)" }

if ($Missing.Count -gt 0) {
    Write-Error "다음 파일들이 'tools' 폴더에 없습니다!"
    $Missing | ForEach-Object { Write-Error " - $_" }
    Write-Host "`nD:\bot\tools 폴더에 해당 파일들을 넣어주세요." -ForegroundColor Yellow
    Pause
    exit
}

# 4. Create VMs
for ($i = 1; $i -le $VMCount; $i++) {
    $VMName = "${VM_Prefix}_${i}"
    $DiffDisk = Join-Path $BaseDir "${VMName}.vhdx"
    
    Write-Host "`n[$i/$VMCount] $VMName 작업 중..." -ForegroundColor Green

    # Setup 4-1: Clean previous VM
    if (Get-VM -Name $VMName -ErrorAction SilentlyContinue) {
        Write-Host "  - 기존 VM 삭제 중..."
        Stop-VM -Name $VMName -Force -ErrorAction SilentlyContinue
        Remove-VM -Name $VMName -Force
    }
    if (Test-Path $DiffDisk) { Remove-Item $DiffDisk -Force }

    # Setup 4-2: Create Diff Disk (Fast Clone)
    Write-Host "  - 디스크 생성 중..."
    New-VHD -Path $DiffDisk -ParentPath $MasterVHD -Differencing | Out-Null

    # Setup 4-3: Offline Injection (Mount VHD)
    Write-Host "  - 파일 주입 중 (Mount)..."
    try {
        $Mount = Mount-VHD -Path $DiffDisk -Passthru
        $DriveLetter = ($Mount | Get-Disk | Get-Partition | Where-Object { $_.DriveLetter -ne $null } | Select-Object -First 1).DriveLetter
        
        if (-not $DriveLetter) { throw "드라이브 문자 할당 실패" }
        $DriveRoot = "${DriveLetter}:"

        # Copy Files to C:\BotSetup inside VM
        $Dest = "$DriveRoot\BotSetup"
        New-Item -Path $Dest -ItemType Directory -Force | Out-Null
        
        Copy-Item $ChromeInst "$Dest\ChromeSetup.exe"
        Copy-Item $VPNInst "$Dest\VPNSetup.exe"
        Copy-Item $BotSourceDir "$Dest\NaverShoppingBot" -Recurse

        # Create Guest Setup Script (Runs inside VM)
        $GuestScriptContent = @"
Start-Transcript -Path "C:\BotSetup_Log.txt"
Write-Host "Installing Chrome..."
Start-Process "C:\BotSetup\ChromeSetup.exe" -ArgumentList "/silent", "/install" -Wait

Write-Host "Installing VPN..."
Start-Process "C:\BotSetup\VPNSetup.exe" -ArgumentList "/silent" -Wait
# TODO: Add VPN Login automation logic here if possible

Write-Host "Setting up Bot..."
# Copy to Desktop
`$Desktop = [Environment]::GetFolderPath("Desktop")
Copy-Item "C:\BotSetup\NaverShoppingBot" "`$Desktop\NaverShoppingBot" -Recurse -Force

# Create Shortcut on Desktop
`$WshShell = New-Object -comObject WScript.Shell
`$Shortcut = `$WshShell.CreateShortcut("`$Desktop\NaverShoppingBot.lnk")
`$Shortcut.TargetPath = "`$Desktop\NaverShoppingBot\NaverShoppingBot_Company.exe"
`$Shortcut.Save()

Write-Host "Launching Bot..."
Start-Process "`$Desktop\NaverShoppingBot\NaverShoppingBot_Company.exe"

# Cleanup Self (RunOnce)
Remove-Item "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\BotSetup.bat" -Force
Stop-Transcript
"@
        $GuestScriptContent | Out-File "$Dest\Guest_Install.ps1" -Encoding UTF8

        # Create Startup Trigger
        $BatContent = "powershell -ExecutionPolicy Bypass -File C:\BotSetup\Guest_Install.ps1"
        $StartupPath = "$DriveRoot\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\BotSetup.bat"
        $BatContent | Out-File $StartupPath -Encoding ASCII

    }
    catch {
        Write-Error "  - 파일 주입 실패: $_"
        Dismount-VHD -Path $DiffDisk -ErrorAction SilentlyContinue
        continue
    }
    finally {
        Dismount-VHD -Path $DiffDisk -ErrorAction SilentlyContinue
    }

    # Setup 4-4: Create & Start VM
    Write-Host "  - VM 등록 및 시작..."
    New-VM -Name $VMName -MemoryStartupBytes 2GB -VHDPath $DiffDisk -SwitchName $NetSwitchName | Out-Null
    Set-VMProcessor -VMName $VMName -Count 2 # 2 vCPU
    Start-VM -Name $VMName

    Write-Host "  - 완료!"
}

Write-Host "`n=== 모든 작업 완료! VM들이 부팅되면 자동으로 설치를 시작합니다. ===" -ForegroundColor Cyan
Pause
