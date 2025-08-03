# 2DO Installation Script for Windows PowerShell
# Usage: iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex

param(
    [string]$InstallDir = "$env:USERPROFILE\.local\bin",
    [string]$VenvDir = "$env:USERPROFILE\.2do"
)

# Configuration
$RepoUrl = "https://github.com/STAFE-GROUP-AB/2do-developer"
$MinPythonVersion = [Version]"3.8.0"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "[$Prefix] " -ForegroundColor $Colors[$Color] -NoNewline
    }
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Status {
    param([string]$Message)
    Write-ColoredOutput -Message $Message -Color "Blue" -Prefix "INFO"
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput -Message $Message -Color "Green" -Prefix "SUCCESS"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput -Message $Message -Color "Yellow" -Prefix "WARNING"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput -Message $Message -Color "Red" -Prefix "ERROR"
}

function Write-Header {
    Write-Host ""
    Write-ColoredOutput -Message "╭─────────────────────────────────────────────────────────╮" -Color "Blue"
    Write-ColoredOutput -Message "│                    2DO INSTALLER                        │" -Color "Blue"
    Write-ColoredOutput -Message "│   Intelligent AI model routing and multitasking CLI    │" -Color "Blue"
    Write-ColoredOutput -Message "╰─────────────────────────────────────────────────────────╯" -Color "Blue"
    Write-Host ""
}

function Test-CommandExists {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-PythonVersion {
    param([string]$PythonCmd)
    
    try {
        $versionOutput = & $PythonCmd --version 2>&1
        if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
            $version = [Version]$matches[1]
            return $version -ge $MinPythonVersion
        }
    }
    catch {
        return $false
    }
    return $false
}

function Find-Python {
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        if (Test-CommandExists $cmd) {
            if (Test-PythonVersion $cmd) {
                return $cmd
            }
        }
    }
    return $null
}

function Install-PythonWindows {
    Write-Status "Python 3.8+ not found. Attempting to install..."
    
    # Check if winget is available
    if (Test-CommandExists "winget") {
        Write-Status "Installing Python using winget..."
        try {
            winget install -e --id Python.Python.3.12
            Write-Success "Python installed via winget"
            return $true
        }
        catch {
            Write-Warning "winget installation failed, trying alternative methods..."
        }
    }
    
    # Check if chocolatey is available
    if (Test-CommandExists "choco") {
        Write-Status "Installing Python using Chocolatey..."
        try {
            choco install python3 -y
            Write-Success "Python installed via Chocolatey"
            return $true
        }
        catch {
            Write-Warning "Chocolatey installation failed..."
        }
    }
    
    # Guide user to manual installation
    Write-Warning "Automatic installation failed. Please install Python manually:"
    Write-Host "1. Visit: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "2. Download Python 3.8 or later" -ForegroundColor Yellow
    Write-Host "3. Run the installer and make sure to check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "4. Restart PowerShell and run this script again" -ForegroundColor Yellow
    return $false
}

function New-InstallDirectory {
    if (-not (Test-Path $InstallDir)) {
        Write-Status "Creating installation directory: $InstallDir"
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
}

function Add-ToPath {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($currentPath -notlike "*$InstallDir*") {
        Write-Status "Adding $InstallDir to user PATH"
        $newPath = if ($currentPath) { "$currentPath;$InstallDir" } else { $InstallDir }
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        $env:PATH = "$env:PATH;$InstallDir"
        Write-Success "Added to PATH. Restart PowerShell to use the new PATH."
    }
}

function Install-2DO {
    param([string]$PythonCmd)
    
    $tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
    
    Write-Status "Creating virtual environment..."
    & $PythonCmd -m venv $VenvDir
    
    if (-not $?) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    
    Write-Status "Activating virtual environment..."
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        & $activateScript
    } else {
        Write-Error "Failed to find activation script"
        exit 1
    }
    
    Write-Status "Upgrading pip..."
    & python -m pip install --upgrade pip
    
    Write-Status "Downloading 2DO source code..."
    $repoDir = Join-Path $tempDir "2do-developer"
    
    if (Test-CommandExists "git") {
        & git clone "$RepoUrl.git" $repoDir
    } else {
        Write-Status "Git not found, downloading as ZIP..."
        $zipPath = Join-Path $tempDir "main.zip"
        Invoke-WebRequest -Uri "$RepoUrl/archive/main.zip" -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $tempDir
        $extractedDir = Join-Path $tempDir "2do-developer-main"
        Move-Item $extractedDir $repoDir
    }
    
    Write-Status "Installing 2DO..."
    Set-Location $repoDir
    
    # Try installing with retries
    $installSuccess = $false
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        Write-Status "Installation attempt $attempt/3..."
        try {
            & pip install . --timeout 60
            if ($?) {
                $installSuccess = $true
                break
            }
        }
        catch {
            Write-Warning "Installation attempt $attempt failed, retrying..."
            Start-Sleep -Seconds 5
        }
    }
    
    if (-not $installSuccess) {
        Write-Error "Failed to install 2DO after 3 attempts. This may be due to network issues."
        Write-Error "Please check your internet connection and try again."
        exit 1
    }
    
    Write-Status "Creating wrapper script..."
    $wrapperScript = @"
@echo off
call "$VenvDir\Scripts\activate.bat"
2do %*
"@
    
    $wrapperPath = Join-Path $InstallDir "2do.bat"
    $wrapperScript | Out-File -FilePath $wrapperPath -Encoding ASCII
    
    # Clean up
    Remove-Item $tempDir -Recurse -Force
    
    Write-Success "2DO installed successfully!"
}

function Start-Setup {
    Write-Status "Running 2DO setup wizard..."
    
    $twodoPath = Join-Path $InstallDir "2do.bat"
    if (Test-Path $twodoPath) {
        & $twodoPath setup
    } else {
        # Fallback to direct execution
        $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
        & $activateScript
        & 2do setup
    }
}

function Main {
    Write-Header
    
    Write-Status "Detected OS: Windows"
    
    # Check for Python
    $pythonCmd = Find-Python
    if (-not $pythonCmd) {
        if (-not (Install-PythonWindows)) {
            exit 1
        }
        
        # Check again after installation
        Start-Sleep -Seconds 2
        $pythonCmd = Find-Python
        if (-not $pythonCmd) {
            Write-Error "Python installation verification failed. Please install Python 3.8+ manually."
            exit 1
        }
    }
    
    Write-Success "Found Python: $pythonCmd"
    
    # Create installation directory
    New-InstallDirectory
    
    # Install 2DO
    Install-2DO $pythonCmd
    
    # Add to PATH
    Add-ToPath
    
    Write-Success "Installation completed!"
    
    # Run setup wizard
    Write-Host ""
    Write-Status "Starting setup wizard..."
    
    try {
        Start-Setup
    }
    catch {
        Write-Status "Please restart PowerShell and run: 2do setup"
    }
    
    Write-Host ""
    Write-Success "2DO is now installed! 🎉"
    Write-Host ""
    Write-ColoredOutput -Message "Next steps:" -Color "Cyan"
    Write-Host "1. Restart PowerShell to use the updated PATH"
    Write-Host "2. Run: 2do setup (if not completed above)"
    Write-Host "3. Start using 2DO: 2do start"
    Write-Host ""
    Write-ColoredOutput -Message "For help:" -Color "Cyan"
    Write-Host "- Run: 2do --help"
    Write-Host "- Visit: $RepoUrl"
    Write-Host ""
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Installation failed: $($_.Exception.Message)"
    exit 1
}