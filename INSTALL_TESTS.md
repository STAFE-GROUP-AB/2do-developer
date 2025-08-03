# 2DO Installation Tests

This directory contains tests to verify the curl-based installation system works correctly.

## Test Files

- `test_functionality.sh` - Tests installation script syntax and functionality
- `test_install.sh` - Basic syntax and structure tests
- Manual installation verification

## Running Tests

```bash
# Test installation script functionality
./test_functionality.sh

# Test basic syntax
./test_install.sh
```

## Installation Commands

### Unix/Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex
```

## What the Installer Does

1. **OS Detection**: Automatically detects Windows, macOS, or Linux
2. **Python Check**: Verifies Python 3.8+ is installed, offers to install if missing
3. **Virtual Environment**: Creates isolated Python environment at `~/.2do`
4. **Package Installation**: Downloads and installs 2DO from the repository
5. **CLI Setup**: Creates `2do` command and adds to PATH
6. **Setup Wizard**: Automatically runs the configuration wizard

## Installation Locations

- **Virtual Environment**: `~/.2do/` (Linux/macOS) or `%USERPROFILE%\.2do` (Windows)
- **CLI Command**: `~/.local/bin/2do` (Linux/macOS) or `%USERPROFILE%\.local\bin\2do.bat` (Windows)
- **Configuration**: `~/.2do/` or via global config if specified

## Troubleshooting

### Network Issues
If installation fails due to network timeouts:
```bash
# Retry with manual clone
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer
pip install .
```

### Python Issues
Ensure Python 3.8+ is installed:
```bash
python3 --version
# or
python --version
```

### PATH Issues
If `2do` command not found after installation:
```bash
# Linux/macOS
export PATH="$HOME/.local/bin:$PATH"

# Windows
$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
```