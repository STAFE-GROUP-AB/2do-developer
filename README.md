# 2DO

🤖 **2DO** is an intelligent command line tool that automatically selects the best AI model for your prompts and enables powerful multitasking capabilities for developers.

## Features

### 🎯 Intelligent AI Model Routing
- Automatically analyzes your prompts to determine the most suitable AI model
- Supports multiple AI providers (OpenAI, Anthropic, and more)
- Optimizes for speed, cost, and task complexity

### 🌐 Browser Integration
- Start browser interactive mode alongside the terminal
- Automatically detects project type and starts appropriate development server
- Opens browser with your project running in real-time
- Auto-refreshes browser after task completion for immediate visual feedback
- Supports React, Vue, Angular, Laravel, Django, Flask, and static HTML projects

### 📋 Advanced Todo Management
- Create and manage todos for codebases and projects
- Support for text, code, image, and general task types
- Priority-based organization (low, medium, high, critical)
- **🆕 Automatic sub-task creation for large/complex todos**
- **🆕 AI-powered task breakdown with intelligent analysis**
- **🆕 Parent-child todo relationships and hierarchy display**
- Automatic todo generation from repository analysis
- Import tasks from markdown files
- Export todos as GitHub issues (with sub-task support)

### ⚡ Multitasking Engine
- Process multiple todos in parallel using optimal AI models
- Intelligent task distribution based on AI model capabilities
- Real-time progress tracking and result aggregation

### 🔧 Tech Stack Detection & Memory
- Automatically detects technology stack from repositories
- Creates intelligent memory files for better context
- Supports 25+ technologies including TALL Stack (TailwindCSS, Alpine.js, Laravel, Livewire)
- Provides tech-specific best practices and recommendations

### 📁 Local Project Management
- Detects git repositories and creates local 2DO folders for project-specific settings
- Stores project memory and configuration locally when working in git repositories
- Seamless switching between global and project-specific configurations

### 🔌 GitHub Integration
- Read and work on GitHub issues directly from the CLI
- Automatic branch creation for issue work
- Pull request creation with proper linking to issues
- Export todos as GitHub issues with labels and descriptions
- Branch management and workflow automation

### 🖼️ Image Support
- Include images in chat prompts using file paths
- Enhanced AI model routing for image-based tasks

### 📄 Markdown Task Parser
- Extract tasks from markdown files using various formats
- Support for standard checkbox formats (- [ ], * [ ], + [ ])
- TODO: format recognition
- Automatic todo creation from parsed tasks

### 🔌 MCP Server Integration
- **🎯 Smart MCP Server Recommendations**: Automatically analyzes your codebase and recommends the most relevant MCP servers
- **📋 Tech Stack-Based Selection**: Suggests MCP servers based on detected technologies (Python, JavaScript, Docker, etc.)
- **⭐ Always-Included Essentials**: Ensures [Context7 (Upstash)](https://github.com/upstash/context7) and filesystem servers are always available
- **🔧 Easy Configuration**: Interactive setup and management of MCP servers through `2do mcp` command
- **🛠️ Popular Server Support**: Includes Git, GitHub, Python, Node.js, Browser, Docker, AWS, and database MCP servers
- **💾 Persistent Configuration**: Saves MCP server configurations for reuse across sessions

## Installation

### 🚀 Quick Install (Recommended)

Install 2DO with a single command:

#### Unix/Linux/macOS:
```bash
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash
```

#### Windows (PowerShell):
```powershell
iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex
```

The installer will:
- ✅ Detect your operating system
- ✅ Check for Python 3.8+ (install if needed)
- ✅ Download and install 2DO
- ✅ Set up the command in your PATH
- ✅ Run the setup wizard automatically

### 📦 Manual Installation

If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Updates

### 🔄 Automatic Updates

2DO includes a built-in update system that supports multiple installation methods:

```bash
# Check for updates
2do update --check-only

# Update to latest version
2do update

# Force update from main branch (useful for development versions)
2do update --force
```

**Update Features:**
- ✅ **Automatic version detection** - Compares your version with latest releases
- ✅ **Multiple update methods** - Supports installer script, pip, and source installations
- ✅ **Backup and rollback** - Creates backups before updating (installer method)
- ✅ **Smart detection** - Automatically detects how 2DO was installed
- ✅ **Progress tracking** - Shows clear progress during updates
- ✅ **Error handling** - Graceful fallbacks if update fails

**Supported Update Methods:**
- **Installer Script**: Re-runs the original installation script (most stable)
- **Pip Update**: Updates via `pip install --upgrade` from GitHub
- **Source Update**: Pulls latest changes via `git pull` (for development)

### 🛠️ Manual Update Methods

If automatic updates don't work, you can update manually:

#### For Installer Script Installations:
```bash
# Re-run the installer
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash
```

#### For Pip Installations:
```bash
pip install --upgrade git+https://github.com/STAFE-GROUP-AB/2do-developer.git
```

#### For Source Installations:
```bash
cd /path/to/2do-developer
git pull origin main
pip install -e .
```

## Quick Start

### 1. Initial Setup
```bash
# Configure your AI model API keys and GitHub integration
2do setup
```

This will guide you through configuring:
- **OpenAI API key** for GPT models
- **Anthropic API key** for Claude models  
- **GitHub Personal Access Token** for repository integration

### 2. Start Interactive Session
```bash
# Start in a git repository (automatically creates local 2DO folder)
cd /path/to/your/git/project
2do start

# Start with a specific repository
2do start --repo /path/to/your/project

# Start without a repository (uses global configuration)
2do start
```

### 3. Available Commands

#### Interactive Session Features
- **add-todo**: Create new todo items with different types and priorities
- **list-todos**: View all todos in a formatted table
- **start-multitask**: Process all pending todos in parallel
- **start-browser**: Start browser integration mode with auto-detection
- **refresh-browser**: Manually refresh the browser (when browser mode is active)
- **stop-browser**: Stop browser integration and development server
- **🆕 create-subtasks**: Break down large todos into manageable sub-tasks
- **parse-markdown**: Extract tasks from markdown files and convert to todos
- **github-issues**: Work with GitHub issues (list, work on, create todos from issues)
- **create-github-issue**: Create new GitHub issues directly
- **export-todos-to-github**: Export your todos as GitHub issues (with sub-task linking)
- **chat**: Interactive chat with intelligent AI model routing (supports images)
- **quit**: Exit the session

#### Command Line Features
- **2do setup**: Configure AI model API keys and GitHub integration
- **2do start**: Start the interactive session
- **2do verify**: Verify setup and guide through missing components
- **2do mcp**: Manage MCP (Model Context Protocol) servers
- **🆕 2do update**: Check for and install updates automatically
- **2do --help**: Show help and available commands

## Usage Examples

### Local 2DO Folder Setup
```bash
# Navigate to any git repository
cd /path/to/your/git/project

# Start 2DO - automatically creates 2DO folder
2do start

# The tool will:
# 1. Detect it's a git repository
# 2. Create a local "2DO" folder for project-specific settings
# 3. Store todos, memory files, and configuration locally
# 4. Detect GitHub repository information if available
```

### Browser Integration Mode
```bash
# Start 2DO in a project directory
cd /path/to/your/web/project
2do start

# In the interactive session:
# 1. Choose "start-browser" to:
#    - Auto-detect your project type (React, Laravel, Django, etc.)
#    - Start the appropriate development server
#    - Open your browser automatically
#    - Enable auto-refresh after task completion

# 2. Work on your todos and see changes in real-time
# 3. After multitasking, the browser refreshes automatically
# 4. Use "refresh-browser" for manual refresh
# 5. Use "stop-browser" to clean up
```

### Repository Analysis and Todo Generation
```bash
# Analyze a GitHub repository and create todos
2do start --repo https://github.com/user/project

# The tool will:
# 1. Detect the tech stack (Python, React, Laravel, TailwindCSS, etc.)
# 2. Create memory files for optimal AI context
# 3. Generate relevant todos (code review, documentation, tests)
# 4. Allow you to add custom todos
```

### Working with GitHub Issues
```bash
# After starting in a git repository with GitHub remote:
# 1. Select "github-issues" from the menu
# 2. Choose "list" to see all open issues
# 3. Choose "work-on" and enter issue number
#    - Automatically creates a new branch: "issue-123-fix-login-bug"
#    - Switches to that branch for development
# 4. Make your changes and commits
# 5. Choose "finish-work" to create a pull request
```

### MCP Server Management
```bash
# Get recommendations based on your project
2do mcp --recommend

# Set up MCP servers interactively (analyzes codebase and recommends servers)
2do mcp

# List currently configured MCP servers
2do mcp --list

# Example output for a Python project:
# 🔍 Analyzing project: /path/to/project
# 📋 Detected technologies: python, git
# 
# Recommended MCP Servers:
# ✅ Context7 (Upstash) - Always included for advanced context management
# ✅ Filesystem MCP Server - Essential for file operations
# ✅ Git MCP Server - Git repository operations (detected: git)
# ✅ Python MCP Server - Python code execution (detected: python)
#
# Interactive selection allows you to choose which servers to configure
```

### Markdown Task Processing
```bash
# Extract tasks from markdown files
# Supports formats like:
# - [ ] Pending task
# - [x] Completed task  
# - TODO: Something to do
# * [ ] Another task format
# + [ ] Yet another format

# In 2DO:
# 1. Select "parse-markdown"
# 2. Choose to parse current directory, specific file, or directory
# 3. Review found tasks and create todos from them
```

### Image-Enhanced Chat
```bash
# In chat mode, include images:
# 1. Type: image:/path/to/screenshot.png
# 2. Enter your question about the image
# 3. 2DO will choose the best model for image analysis
```

### TALL Stack Development
```bash
# When working in a Laravel project with TailwindCSS, Alpine.js, and Livewire:
# 1. 2DO detects all TALL stack components
# 2. Creates specialized memory files with best practices
# 3. Provides contextual advice for the full stack
```

### Adding Different Types of Todos
```bash
# Code-related todo
Todo type: code
Priority: high
Content: Paste your code or reference files

# Text-based todo  
Todo type: text
Priority: medium
Content: Documentation or written content

# Image processing todo
Todo type: image
Priority: low
Content: Path to image file
```

### 🆕 Sub-task Management
2DO automatically detects large or complex todos and can break them down into manageable sub-tasks:

```bash
# When adding a large todo, 2DO will prompt:
# "🔍 This todo appears to be quite large and complex."
# "Would you like to automatically break it down into sub-tasks?"

# Manual sub-task creation
# 1. Select "create-subtasks" from the menu
# 2. Choose a todo from the list
# 3. AI will analyze and create 3-5 sub-tasks

# Sub-tasks are displayed hierarchically:
# 📁 Build web application (with 4 sub-tasks)
#   ├─ Plan & Design - Planning phase
#   ├─ Core Implementation - Main development  
#   ├─ Testing - Testing and validation
#   └─ Documentation - Documentation and guides
```

#### Sub-task Detection Criteria
2DO identifies large/complex todos based on:
- **Content length**: Over 500 characters
- **Complexity keywords**: "comprehensive", "complete", "system", "platform", etc.
- **Multiple actions**: Presence of connecting words indicating multiple steps

#### GitHub Integration with Sub-tasks
When exporting todos to GitHub, you can choose:
- **parent-only**: Export only the main todo
- **with-subtasks**: Include sub-tasks in the description
- **subtasks-as-issues**: Create separate linked GitHub issues for each sub-task

### Multitasking Processing
When you start multitasking, the 2DO:
1. Analyzes each todo to determine the best AI model
2. Creates optimized prompts based on todo type and content
3. Processes todos in parallel (up to 5 concurrent tasks)
4. Provides real-time progress tracking
5. Aggregates and displays results

## AI Model Selection Logic

The 2DO uses sophisticated analysis to route prompts:

### Prompt Analysis Factors
- **Code keywords**: Functions, classes, debugging, algorithms
- **Reasoning keywords**: Analysis, explanation, comparison
- **Creative keywords**: Writing, generation, design
- **Speed requirements**: Quick, simple, brief tasks
- **Complexity indicators**: Detailed, comprehensive tasks
- **Context length**: Long prompts requiring large context windows

### Model Capabilities
- **GPT-4**: Complex reasoning, code analysis, general tasks
- **GPT-3.5 Turbo**: Speed-optimized for simple tasks
- **GPT-4 Turbo**: Large context, code-heavy tasks
- **Claude 3 Opus**: Advanced reasoning, creative tasks
- **Claude 3 Sonnet**: Balanced performance and speed
- **Claude 3 Haiku**: Ultra-fast simple tasks

## Tech Stack Detection

Supports automatic detection of:
- **Languages**: Python, JavaScript, TypeScript, Java, C#, C++, Rust, Go, PHP, Ruby
- **Frontend Frameworks**: React, Vue, Angular
- **Backend Frameworks**: Express, Django, Flask, Laravel
- **TALL Stack**: TailwindCSS, Alpine.js, Laravel, Livewire
- **CSS Frameworks**: TailwindCSS, Sass, Less
- **Tools**: Docker, Kubernetes, Terraform
- **Databases**: SQL files, SQLite
- **Build Systems**: Gradle, Maven, CMake, Cargo

### TALL Stack Integration
When all four TALL stack components are detected:
- **TailwindCSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight JavaScript framework
- **Laravel**: PHP web application framework  
- **Livewire**: Laravel library for building dynamic interfaces

2DO provides specialized context and best practices for this modern PHP stack.

### Browser Integration Project Support
2DO automatically detects and supports:
- **React**: Uses `npm start` or `npm run dev` (port 3000)
- **Vue.js**: Uses `npm run serve` or `npm run dev` (port 8080)
- **Angular**: Uses `npm start` or `npm run serve` (port 4200)
- **Next.js**: Uses `npm run dev` (port 3000)
- **Vite**: Uses `npm run dev` (port 5173)
- **Laravel**: Uses `php artisan serve` (port 8000)
- **Django**: Uses `python manage.py runserver` (port 8000)
- **Flask**: Auto-detects Flask apps and runs with Python (port 5000)
- **Static HTML**: Uses Python's built-in HTTP server (port 8080)

The browser integration automatically:
1. Detects your project type based on files and dependencies
2. Starts the appropriate development server
3. Opens your default browser to the running application
4. Refreshes the browser after completing todos or multitasking

## Configuration

### Global Configuration
Configuration files are stored in `~/.2do/`:
- `config.yaml`: Main configuration and API keys
- `todos/todos.json`: Global todo items storage
- `memory/`: Global tech stack memory files

### Local Project Configuration (2DO Folders)
When working in a git repository, 2DO creates a local `2DO/` folder:
- `2DO/config.yaml`: Project-specific configuration
- `2DO/todos/todos.json`: Project-specific todo items
- `2DO/memory/`: Project-specific tech stack memory files

This allows you to:
- Keep project todos separate from global todos
- Have different AI model preferences per project
- Maintain project-specific memory and context

### GitHub Integration Setup
1. Create a GitHub Personal Access Token with permissions:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories)
   - `issues` (for issue management)
   - `pull_requests` (for PR creation)

2. Configure during setup:
   ```bash
   2do setup
   # Enter your token when prompted for GitHub configuration
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please visit the [GitHub Issues](https://github.com/STAFE-GROUP-AB/AI-Redirector/issues) page.