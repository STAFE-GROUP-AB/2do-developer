#!/bin/bash
# 2DO Installation Script for Unix/Linux/macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/STAFE-GROUP-AB/2do-developer"
INSTALL_DIR="$HOME/.local/bin"
VENV_DIR="$HOME/.2do"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╭─────────────────────────────────────────────────────────╮"
    echo "│                    2DO INSTALLER                        │"
    echo "│   Intelligent AI model routing and multitasking CLI    │"
    echo "╰─────────────────────────────────────────────────────────╯"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Check Python installation
check_python() {
    local python_cmd=""
    local python_version=""
    
    if command_exists python3; then
        python_cmd="python3"
    elif command_exists python; then
        python_cmd="python"
    else
        return 1
    fi
    
    python_version=$($python_cmd --version 2>&1 | awk '{print $2}')
    local major_version=$(echo $python_version | cut -d. -f1)
    local minor_version=$(echo $python_version | cut -d. -f2)
    
    if [ "$major_version" -eq 3 ] && [ "$minor_version" -ge 8 ]; then
        echo $python_cmd
        return 0
    else
        return 1
    fi
}

# Install Python on macOS using Homebrew
install_python_macos() {
    if command_exists brew; then
        print_status "Installing Python using Homebrew..."
        brew install python3
    else
        print_error "Homebrew not found. Please install Python 3.8+ manually:"
        print_error "1. Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        print_error "2. Install Python: brew install python3"
        exit 1
    fi
}

# Install Python on Linux
install_python_linux() {
    local os_id=""
    if [ -f /etc/os-release ]; then
        os_id=$(grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '"')
    fi
    
    case $os_id in
        ubuntu|debian)
            print_status "Installing Python using apt..."
            sudo apt update && sudo apt install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|fedora)
            if command_exists dnf; then
                print_status "Installing Python using dnf..."
                sudo dnf install -y python3 python3-pip
            elif command_exists yum; then
                print_status "Installing Python using yum..."
                sudo yum install -y python3 python3-pip
            fi
            ;;
        arch)
            print_status "Installing Python using pacman..."
            sudo pacman -S python python-pip
            ;;
        *)
            print_error "Unsupported Linux distribution. Please install Python 3.8+ manually."
            exit 1
            ;;
    esac
}

# Create installation directory
create_install_dir() {
    if [ ! -d "$INSTALL_DIR" ]; then
        print_status "Creating installation directory: $INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
    fi
}

# Add to PATH if not already there
add_to_path() {
    local shell_rc=""
    
    if [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.profile"
    fi
    
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        print_status "Adding $INSTALL_DIR to PATH in $shell_rc"
        echo "" >> "$shell_rc"
        echo "# Added by 2DO installer" >> "$shell_rc"
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$shell_rc"
        export PATH="$INSTALL_DIR:$PATH"
        print_success "Added to PATH. Restart your terminal or run: source $shell_rc"
    fi
}

# Install 2DO
install_2do() {
    local python_cmd="$1"
    local temp_dir=$(mktemp -d)
    
    print_status "Creating virtual environment..."
    $python_cmd -m venv "$VENV_DIR"
    
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    print_status "Downloading 2DO source code..."
    if command_exists git; then
        git clone "$REPO_URL.git" "$temp_dir/2do-developer"
    else
        print_status "Git not found, downloading as ZIP..."
        if command_exists curl; then
            curl -L "${REPO_URL}/archive/main.zip" -o "$temp_dir/main.zip"
            cd "$temp_dir"
            unzip main.zip
            mv 2do-developer-main 2do-developer
        elif command_exists wget; then
            wget "${REPO_URL}/archive/main.zip" -O "$temp_dir/main.zip"
            cd "$temp_dir"
            unzip main.zip
            mv 2do-developer-main 2do-developer
        else
            print_error "Neither git, curl, nor wget found. Cannot download 2DO."
            exit 1
        fi
    fi
    
    print_status "Installing 2DO..."
    cd "$temp_dir/2do-developer"
    
    # Try installing with retries
    local install_success=false
    for attempt in 1 2 3; do
        print_status "Installation attempt $attempt/3..."
        if pip install . --timeout 60; then
            install_success=true
            break
        else
            print_warning "Installation attempt $attempt failed, retrying..."
            sleep 5
        fi
    done
    
    if [ "$install_success" = false ]; then
        print_error "Failed to install 2DO after 3 attempts. This may be due to network issues."
        print_error "Please check your internet connection and try again."
        exit 1
    fi
    
    print_status "Creating wrapper script..."
    cat > "$INSTALL_DIR/2do" << EOF
#!/bin/bash
source "$VENV_DIR/bin/activate"
exec 2do "\$@"
EOF
    
    chmod +x "$INSTALL_DIR/2do"
    
    # Clean up
    rm -rf "$temp_dir"
    
    print_success "2DO installed successfully!"
}

# Run setup wizard
run_setup() {
    print_status "Running 2DO setup wizard..."
    if command_exists "$INSTALL_DIR/2do"; then
        "$INSTALL_DIR/2do" setup
    else
        source "$VENV_DIR/bin/activate"
        2do setup
    fi
}

# Main installation function
main() {
    print_header
    
    local os_type=$(detect_os)
    print_status "Detected OS: $os_type"
    
    # Check for Python
    local python_cmd=$(check_python)
    if [ $? -ne 0 ]; then
        print_warning "Python 3.8+ not found. Installing Python..."
        case $os_type in
            macos)
                install_python_macos
                ;;
            linux)
                install_python_linux
                ;;
            *)
                print_error "Please install Python 3.8+ manually and run this script again."
                exit 1
                ;;
        esac
        
        # Check again after installation
        python_cmd=$(check_python)
        if [ $? -ne 0 ]; then
            print_error "Python installation failed. Please install Python 3.8+ manually."
            exit 1
        fi
    fi
    
    print_success "Found Python: $python_cmd"
    
    # Create installation directory
    create_install_dir
    
    # Install 2DO
    install_2do "$python_cmd"
    
    # Add to PATH
    add_to_path
    
    print_success "Installation completed!"
    
    # Run setup wizard
    echo ""
    print_status "Starting setup wizard..."
    if command_exists "$INSTALL_DIR/2do" && [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        "$INSTALL_DIR/2do" setup
    else
        print_status "Please restart your terminal and run: 2do setup"
    fi
    
    echo ""
    print_success "2DO is now installed! 🎉"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo "1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Run: 2do setup (if not completed above)"
    echo "3. Start using 2DO: 2do start"
    echo ""
    echo -e "${BOLD}For help:${NC}"
    echo "- Run: 2do --help"
    echo "- Visit: $REPO_URL"
    echo ""
}

# Run main function only if script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi