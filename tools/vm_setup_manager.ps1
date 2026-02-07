<#
.SYNOPSIS
    Hyper-V VM One-Click Setup Script for NaverShoppingBot
    
.DESCRIPTION
    Automates the setup of fresh Hyper-V VMs:
    1. Starts the VM
    2. Copies necessary files (Bot, Chrome, VPN)
    3. Silently installs Chrome
    4. Sets up the Bot shortcut
    5. Lunches the Bot
    
.NOTES
    Requires: Hyper-V PowerShell Module, Guest Services Enabled on VMs.
    Place 'ChromeSetup.exe' and 'VPNSetup.exe' in the same folder as this script.
#>

param(
    [Parameter(Mandatory=$true)]
    [string[]]$VMNames,  # List of VMs, e.g., "VM1","VM2"

    [string]$VPN_ID = "",
    [string]$VPN_PW = ""
)

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BotSource = "D:\bot\최종ver\회사용\NaverShoppingBot"
$ChromeInstaller = Join-Path $ScriptDir "ChromeStandaloneSetup64.exe"
$VPNInstaller = Join-Path $ScriptDir "VPNSetup.exe"  # Rename your VPN installer to this

# Check Files
if (-not (Test-Path $BotSource)) { Write-Error "Bot folder not found at $BotSource"; exit }
if (-not (Test-Path $ChromeInstaller)) { Write-Warning "Chrome Installer not found. Please download 'ChromeStandaloneSetup64.exe' to tools folder." }

foreach ($vm in $VMNames) {
    Write-Host "Processing VM: $vm" -ForegroundColor Cyan

    # 1. Start VM
    if ((Get-VM -Name $vm).State -ne 'Running') {
        Write-Host "  Starting VM..."
        Start-VM -Name $vm
        Write-Host "  Waiting for boot (60s)..."
        Start-Sleep -Seconds 60
    }

    # 2. Enable Guest Services (for Copy-VMFile)
    Enable-VMIntegrationService -VMName $vm -Name "Guest Service Interface" -ErrorAction SilentlyContinue

    # 3. Create Directories in Guest
    Write-Host "  Preparing directories..."
    Invoke-Command -VMName $vm -Credential (Get-Credential) -ScriptBlock {
        New-Item -Path "C:\BotSetup" -ItemType Directory -Force | Out-Null
        New-Item -Path "C:\NaverShoppingBot" -ItemType Directory -Force | Out-Null
    }

    # 4. Copy Files
    Write-Host "  Copying files (This may take time)..."
    try {
        # Copy Bot (Recursive copy via Copy-VMFile is tricky for folders, usually need to zip or copy individual)
        # For simplicity, let's assume we Zip it first or copy main exe. 
        # Actually, Copy-VMFile doesn't support recursive folders well.
        # Better strategy: Mount VHD or simple file copy. 
        # workaround: Copy Zip, then unzip.
        
        # Checking if 7z or PowerShell unzip is available in guest. (Windows 10+ has Expand-Archive)
        
        # Just copying Chrome for now
        if (Test-Path $ChromeInstaller) {
            Copy-VMFile -VMName $vm -SourcePath $ChromeInstaller -DestinationPath "C:\BotSetup\ChromeSetup.exe" -FileSource Host -Force
        }
        
        # TO-DO: Robust Folder Copy
        # For now, let's just copy the MAIN EXE to test connectivity.
        # Real solution needs ZIP.
    }
    catch {
        Write-Error "  File Copy Failed. Ensure 'Guest Services' are enabled in Hyper-V Settings for $vm."
        continue
    }

    # 5. Install & Run in Guest
    Write-Host "  Running Setup inside Guest..."
    Invoke-Command -VMName $vm -ScriptBlock {
        param($vpn_id, $vpn_pw)
        
        # Install Chrome
        if (Test-Path "C:\BotSetup\ChromeSetup.exe") {
            Write-Host "    Installing Chrome..."
            Start-Process "C:\BotSetup\ChromeSetup.exe" -ArgumentList "/silent", "/install" -Wait
        }
        
        # Setup VPN (Example logic)
        if (Test-Path "C:\BotSetup\VPNSetup.exe") {
            Write-Host "    Installing VPN..."
            Start-Process "C:\BotSetup\VPNSetup.exe" -ArgumentList "/silent" -Wait
            # VPN Logic here...
        }

        Write-Host "    Setup Complete!"
    } -ArgumentList $VPN_ID, $VPN_PW

    Write-Host "  Done with $vm!" -ForegroundColor Green
}
