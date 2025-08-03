# 🚀 2DO Curl Installation Demo

This demonstrates the curl-based installation system implemented for 2DO.

## Quick Installation Commands

### Unix/Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex
```

## What Happens During Installation

1. **🔍 OS Detection**: Automatically identifies Windows, macOS, or Linux
2. **🐍 Python Check**: Verifies Python 3.8+ is available
3. **📦 Auto-Install**: Offers to install Python if missing (via system package managers)
4. **🏠 Virtual Environment**: Creates isolated environment at `~/.2do`
5. **⬇️ Download**: Clones or downloads the latest 2DO source code
6. **🔧 Installation**: Installs 2DO and all dependencies
7. **🛠️ CLI Setup**: Creates `2do` command and adds to PATH
8. **⚙️ Configuration**: Runs the setup wizard automatically

## Installation Features

### Cross-Platform Support
- **Linux**: Supports Ubuntu/Debian (apt), CentOS/RHEL/Fedora (dnf/yum), Arch (pacman)
- **macOS**: Uses Homebrew for Python installation
- **Windows**: Uses winget or Chocolatey for Python installation

### Error Handling
- Network timeout handling with retry logic
- Python version validation
- Fallback installation methods
- Clear error messages and troubleshooting guidance

### Smart Detection
- Detects existing Python installations
- Chooses appropriate package managers
- Configures PATH automatically for different shells (bash, zsh, PowerShell)

## File Structure

```
2do-developer/
├── install.sh              # Unix/Linux/macOS installer
├── install.ps1             # Windows PowerShell installer
├── pyproject.toml           # Modern Python packaging configuration
├── test_installation.py    # Installation system tests
├── test_functionality.sh   # Functionality tests
└── README.md               # Updated with installation instructions
```

## Testing

Run the test suite to verify installation system:

```bash
python3 test_installation.py
```

## Manual Installation (Fallback)

If the curl installation fails, users can still install manually:

```bash
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer
pip install .
```

## Verification

After installation, users can verify with:

```bash
2do --version
2do --help
```

## Next Steps

After installation, users should:

1. Restart their terminal (for PATH updates)
2. Run `2do setup` to configure API keys
3. Start using 2DO with `2do start`

This implementation satisfies the requirement to "install and use 2do with one single line of code" and includes a comprehensive setup wizard for user guidance.