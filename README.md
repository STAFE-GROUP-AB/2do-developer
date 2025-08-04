# 2DO

🤖 **2DO** is an intelligent command line tool that automatically selects the best AI model for your prompts and enables powerful multitasking capabilities for developers.

## 🏗️ Repository Architecture

### Technical Overview
- **Total codebase**: ~10,000 lines of Python code across 17 core modules
- **Main package**: `twodo/` containing the core application logic
- **Testing suite**: Comprehensive test coverage with 11 test modules
- **Distribution**: Standard Python package with pyproject.toml configuration

### Core Architecture Components

```
2do-developer/
├── twodo/                    # Main application package (4,900+ LOC)
│   ├── ai_router.py         # Intelligent AI model routing (488 LOC)
│   ├── cli.py               # Command-line interface (1,361 LOC) 
│   ├── todo_manager.py      # Todo management system (398 LOC)
│   ├── multitasker.py       # Parallel task processing (247 LOC)
│   ├── github_integration.py # GitHub API operations (402 LOC)
│   ├── browser_integration.py # Development server automation (281 LOC)
│   ├── mcp_manager.py       # MCP server management (349 LOC)
│   ├── tech_stack.py        # Technology detection (355 LOC)
│   ├── config.py            # Configuration management (288 LOC)
│   ├── setup_guide.py       # Interactive setup wizard (373 LOC)
│   ├── updater.py           # Auto-update system (453 LOC)
│   ├── intent_router.py     # Prompt analysis (373 LOC)
│   ├── image_handler.py     # Image processing (298 LOC)
│   ├── markdown_parser.py   # Markdown task extraction (164 LOC)
│   └── mcp_client.py        # MCP protocol client (222 LOC)
├── tests/                   # Test suite (2,500+ LOC)
├── install.sh              # Unix installation script 
├── install.ps1             # Windows PowerShell installer
└── pyproject.toml          # Modern Python packaging
```

### Key Technical Capabilities

#### 🧠 Intelligent AI Model Routing
The `ai_router.py` module implements sophisticated prompt analysis and model selection:
- **Multi-provider support**: OpenAI (GPT-4, GPT-3.5), Anthropic (Claude), Google (Gemini)
- **Dynamic model scoring**: Analyzes prompt complexity, length, and content type
- **Cost optimization**: Balances performance with API costs
- **Context management**: Handles large context windows up to 200K tokens

#### ⚡ Concurrent Task Processing  
The `multitasker.py` module enables parallel AI operations:
- **Async processing**: Up to 5 concurrent tasks using asyncio
- **Load balancing**: Distributes tasks across available AI models
- **Progress tracking**: Real-time status updates with Rich progress bars
- **Error handling**: Graceful degradation and retry mechanisms

#### 🔧 Technology Stack Detection
The `tech_stack.py` module provides comprehensive project analysis:
- **25+ framework detection**: Python, JavaScript, React, Laravel, Docker, etc.
- **TALL stack recognition**: TailwindCSS, Alpine.js, Laravel, Livewire integration
- **Memory generation**: Creates context files for optimal AI understanding
- **Dependency analysis**: Parses package.json, requirements.txt, composer.json

#### 🌐 Development Workflow Integration
The `browser_integration.py` module automates development servers:
- **Auto-detection**: Identifies React, Vue, Angular, Laravel, Django, Flask projects
- **Server management**: Starts appropriate development servers automatically  
- **Browser automation**: Opens and refreshes browsers after task completion
- **Port management**: Handles port conflicts and fallback options

## Features

### 🎯 Intelligent AI Model Routing
- **Advanced prompt analysis**: Uses machine learning-based keyword detection and complexity scoring
- **Multi-provider ecosystem**: OpenAI (GPT-4o, GPT-4, GPT-3.5), Anthropic (Claude 3.5 Sonnet, Opus, Haiku), Google Gemini
- **Dynamic model selection**: Real-time scoring based on 8 factors including speed, cost, context length, and task complexity
- **Cost optimization**: Automatic selection of cost-effective models for simple tasks (e.g., Haiku for quick responses)
- **Context-aware routing**: Handles large contexts (up to 200K tokens) with appropriate models
- **Performance tracking**: Monitors model performance and adjusts recommendations over time

### 🌐 Browser Integration
- **Smart project detection**: Automatically identifies 8+ project types (React, Vue, Angular, Next.js, Laravel, Django, Flask, static HTML)
- **Development server automation**: Starts appropriate servers with correct ports and configurations
- **Real-time synchronization**: Auto-refreshes browser after task completion for immediate visual feedback
- **Port conflict resolution**: Intelligent port management with fallback mechanisms
- **Process lifecycle management**: Clean startup, monitoring, and shutdown of development servers
- **Multi-platform support**: Works on Windows, macOS, and Linux development environments

### 📋 Advanced Todo Management
- **Comprehensive todo system**: Create, manage, and track tasks across multiple types (code, text, image, general)
- **Priority-based organization**: Four-tier priority system (low, medium, high, critical) with visual indicators
- **Intelligent sub-task creation**: AI-powered task breakdown based on complexity analysis (500+ character detection)
- **Parent-child relationships**: Hierarchical todo structure with dependency tracking
- **Status lifecycle management**: Full workflow from pending → in_progress → completed/failed
- **Persistent storage**: JSON-based storage with atomic file operations and backup mechanisms
- **Project-specific todos**: Local 2DO folders for repository-specific task management
- **Automatic todo generation**: Creates relevant todos from repository analysis and tech stack detection

### ⚡ Multitasking Engine
- **Concurrent processing**: Parallel execution of up to 5 simultaneous AI tasks using asyncio
- **Intelligent load balancing**: Distributes tasks across available AI models based on capabilities
- **Real-time progress tracking**: Rich-powered progress bars with task status and ETA
- **Model-aware scheduling**: Routes different task types to optimal models simultaneously
- **Error resilience**: Graceful handling of API failures with retry mechanisms and fallbacks
- **Result aggregation**: Combines and presents results from multiple parallel operations
- **Resource optimization**: Memory and API quota management for efficient processing

### 🔧 Tech Stack Detection & Memory
- **Comprehensive technology recognition**: Detects 25+ technologies including languages, frameworks, and tools
- **Advanced pattern matching**: Analyzes file extensions, configuration files, and package dependencies  
- **TALL stack specialization**: Deep integration with TailwindCSS, Alpine.js, Laravel, Livewire ecosystem
- **Memory file generation**: Creates intelligent context files optimized for each detected technology
- **Dependency analysis**: Parses package.json, requirements.txt, composer.json, pom.xml, and more
- **Project profiling**: Generates comprehensive project profiles for optimal AI model context
- **Best practices integration**: Provides technology-specific recommendations and code patterns

### 📁 Local Project Management
- Detects git repositories and creates local 2DO folders for project-specific settings
- Stores project memory and configuration locally when working in git repositories
- Seamless switching between global and project-specific configurations

### 🔌 GitHub Integration
- **Complete GitHub API integration**: Read, create, and manage issues and pull requests directly from CLI
- **Automated workflow management**: Branch creation, switching, and PR generation with proper issue linking
- **Repository analysis**: Deep inspection of GitHub repositories for technology detection and todo generation
- **Issue-driven development**: Convert GitHub issues to todos and vice versa with full metadata preservation
- **Advanced export capabilities**: Export todos as GitHub issues with sub-task linking and label management
- **Authentication handling**: Secure token management with permission validation and testing
- **Git workflow automation**: Automated commits, pushes, and branch management for issue-based development

### 🖼️ Image Support
- Include images in chat prompts using file paths
- Enhanced AI model routing for image-based tasks

### 📄 Markdown Task Parser
- Extract tasks from markdown files using various formats
- Support for standard checkbox formats (- [ ], * [ ], + [ ])
- TODO: format recognition
- Automatic todo creation from parsed tasks

### 🔌 MCP Server Integration
- **Intelligent server recommendations**: Analyzes your codebase and automatically recommends relevant MCP servers
- **Technology-aware selection**: Suggests servers based on detected tech stack (Python, JavaScript, Docker, Git, etc.)
- **Essential server management**: Always includes Context7 (Upstash) and filesystem servers for core functionality
- **Interactive configuration**: Guided setup and management through `2do mcp` command with validation
- **Comprehensive server catalog**: Support for 15+ popular MCP servers including Git, GitHub, databases, cloud providers
- **Persistent configuration**: Saves and manages MCP server configurations across sessions
- **Advanced integration**: Seamless communication with MCP servers for enhanced AI model capabilities

## Technical Documentation

### System Requirements
- **Python**: 3.8+ (recommended: 3.10+)
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Memory**: Minimum 512MB RAM for basic operations, 2GB+ recommended for multitasking
- **Storage**: 100MB for installation, additional space for project-specific data
- **Network**: Internet connection required for AI model APIs and GitHub integration

### Dependencies & Architecture
The project utilizes modern Python packaging with `pyproject.toml` and includes:

#### Core Dependencies
- **CLI Framework**: `click>=8.0.0` for command-line interface
- **AI Providers**: `openai>=1.0.0`, `anthropic>=0.20.0`, `google-generativeai>=0.8.0`
- **Async Processing**: `aiohttp>=3.8.0` for concurrent API operations
- **Rich Terminal**: `rich>=13.0.0` for enhanced console output and progress bars
- **Data Validation**: `pydantic>=2.0.0` for configuration and data model validation

#### Integration Dependencies  
- **GitHub**: `PyGithub>=2.0.0` for GitHub API operations
- **Git**: `GitPython>=3.1.0` for local repository management
- **Browser**: `playwright>=1.40.0` for web automation
- **Image Processing**: `pillow>=10.0.0` for image handling and analysis
- **System**: `psutil>=5.9.0` for process management and system monitoring

### Configuration Management
The `config.py` module implements a sophisticated configuration system:

```python
# Configuration hierarchy (priority order):
1. Project-specific: ./2DO/config.yaml
2. User global: ~/.2do/config.yaml  
3. Environment variables: 2DO_*
4. Default values: Built-in fallbacks
```

#### Configuration Features
- **Secure API key storage**: Encrypted credential management
- **Project isolation**: Separate configurations per Git repository
- **Environment variable support**: 12-factor app compliance
- **Migration handling**: Automatic config format upgrades
- **Validation**: Pydantic-based configuration validation

### AI Model Routing Algorithm
The intelligent routing system in `ai_router.py` uses a multi-factor scoring algorithm:

#### Scoring Factors (weighted)
1. **Task complexity** (30%): Keyword analysis and content length
2. **Speed requirements** (25%): Quick vs. thorough processing needs
3. **Cost optimization** (20%): Balance between performance and API costs
4. **Context length** (15%): Required context window size
5. **Model strengths** (10%): Specialized capabilities (code, reasoning, creative)

#### Model Selection Logic
```python
def calculate_model_score(prompt, model_capability):
    complexity_score = analyze_complexity(prompt)
    speed_score = determine_speed_need(prompt) 
    cost_score = calculate_cost_efficiency(model_capability)
    context_score = estimate_context_need(prompt)
    strength_score = match_model_strengths(prompt, model_capability)
    
    return weighted_average([
        complexity_score * 0.30,
        speed_score * 0.25, 
        cost_score * 0.20,
        context_score * 0.15,
        strength_score * 0.10
    ])
```

### Multitasking Architecture
The `multitasker.py` module implements an advanced concurrent processing system:

#### Async Processing Pipeline
1. **Task Analysis**: Evaluate todo complexity and requirements
2. **Model Assignment**: Route each task to optimal AI model
3. **Concurrent Execution**: Process up to 5 tasks simultaneously using asyncio
4. **Progress Tracking**: Real-time status updates with Rich progress bars
5. **Result Aggregation**: Combine outputs and update todo status
6. **Error Handling**: Graceful degradation with retry mechanisms

#### Resource Management
- **Rate Limiting**: Respects AI provider API limits
- **Memory Management**: Efficient handling of large responses
- **Connection Pooling**: Reuse HTTP connections for performance
- **Timeout Handling**: Configurable timeouts for different task types

### Technology Detection System
The `tech_stack.py` module provides comprehensive project analysis:

#### Detection Methods
1. **File Extension Analysis**: Pattern matching against 50+ file types
2. **Configuration File Parsing**: Deep analysis of package.json, requirements.txt, etc.
3. **Dependency Resolution**: Framework detection through dependency analysis
4. **Content Analysis**: Keyword scanning in configuration files
5. **Directory Structure**: Project layout pattern recognition

#### Supported Technologies
- **Languages**: Python, JavaScript, TypeScript, Java, C#, C++, Rust, Go, PHP, Ruby
- **Frontend**: React, Vue, Angular, Svelte, Alpine.js
- **Backend**: Express, Django, Flask, Laravel, Spring Boot
- **CSS**: TailwindCSS, Sass, Less, PostCSS
- **Tools**: Docker, Kubernetes, Terraform, Git
- **Databases**: SQL, MongoDB, Redis detection

### Browser Integration System
The `browser_integration.py` module automates development workflows:

#### Project Detection Algorithm
1. **Package.json Analysis**: Identify JavaScript/Node.js projects
2. **Framework Detection**: Recognize React, Vue, Angular, Next.js patterns
3. **Backend Detection**: Identify PHP (Laravel), Python (Django/Flask) projects  
4. **Static Site Detection**: HTML/CSS projects fallback
5. **Configuration Parsing**: Extract server commands and ports

#### Server Management
- **Process Spawning**: Cross-platform subprocess management
- **Port Allocation**: Dynamic port selection with conflict resolution
- **Health Monitoring**: Server startup validation and monitoring
- **Cleanup Handling**: Graceful shutdown and resource cleanup

### Data Persistence & Storage
The application uses a hybrid storage approach:

#### Todo Storage (`todo_manager.py`)
- **Format**: JSON with atomic write operations
- **Location**: `~/.2do/todos/` (global) or `./2DO/todos/` (project-specific)
- **Backup**: Automatic backup before modifications
- **Validation**: Pydantic model validation for data integrity

#### Memory Files (`tech_stack.py`)
- **Tech-specific context**: Generated per detected technology
- **Best practices**: Framework-specific guidelines and patterns
- **Project profiling**: Comprehensive project analysis summaries
- **Performance**: Cached analysis to avoid repeated computation

### Testing & Quality Assurance
The project includes a comprehensive test suite with 11 test modules covering:

#### Test Coverage Areas
- **CLI Integration**: Complete command-line interface testing (`test_cli_integration.py`)
- **Configuration Management**: Fallback and validation testing (`test_config_fallback.py`)
- **Setup Verification**: Installation and setup process validation (`test_setup_verification.py`)
- **Interactive Features**: User guidance and help system testing (`test_interactive_guidance.py`)
- **Sub-task Management**: Hierarchical todo system testing (`test_subtasks.py`)
- **Dependency Validation**: External dependency testing (`test_dependencies.py`)
- **Performance Testing**: Enhanced progress tracking (`test_enhanced_progress.py`)
- **Basic Functionality**: Core feature testing (`test_basic.py`)
- **Chat System**: Help and interaction testing (`test_chat_help.py`)
- **Comprehensive Integration**: End-to-end workflow testing (`test_comprehensive.py`)

#### Testing Infrastructure
- **Test Framework**: Built-in Python unittest with custom test runner
- **Mock Systems**: Comprehensive mocking for AI APIs and external services  
- **Integration Testing**: Real-world scenario simulation
- **Performance Testing**: Multitasking and concurrent operation validation
- **Configuration Testing**: Multiple environment and setup configurations

#### Quality Metrics
- **Code Coverage**: 2,500+ lines of test code
- **Module Coverage**: All core modules have dedicated test coverage
- **Integration Testing**: Cross-module functionality validation
- **Error Handling**: Comprehensive error condition testing

### Performance & Metrics

#### Code Statistics
- **Total Lines of Code**: ~10,000 lines across Python modules
- **Core Application**: 4,900+ lines in the `twodo/` package
- **Test Coverage**: 2,500+ lines of test code (25% of total codebase)
- **Module Count**: 17 core modules with clear separation of concerns
- **Configuration Files**: Modern `pyproject.toml` with 18 production dependencies

#### Performance Characteristics
- **Startup Time**: < 0.5 seconds for basic commands
- **Memory Usage**: ~50-100MB base memory footprint
- **Concurrent Tasks**: Up to 5 simultaneous AI model requests
- **API Efficiency**: Connection pooling and rate limiting for optimal throughput
- **File Operations**: Atomic writes with backup mechanisms for data safety

#### Scalability Features
- **Async Processing**: Non-blocking concurrent task execution
- **Resource Management**: Intelligent memory and connection management
- **Caching**: Technology detection results cached for performance
- **Batch Operations**: Efficient handling of multiple todos simultaneously
- **Cross-platform**: Consistent performance across Windows, macOS, and Linux

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

### Development Setup
To contribute to 2DO, follow these steps:

```bash
# Clone the repository
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dependencies
pip install -e .

# Install additional development dependencies (if any)
pip install pytest pytest-cov black flake8

# Verify installation
2do --help
```

### Development Workflow
1. **Fork and Clone**: Fork the repository and clone your fork
2. **Branch Creation**: Create a feature branch: `git checkout -b feature/your-feature-name`
3. **Development**: Make your changes following the coding standards
4. **Testing**: Run the test suite to ensure your changes don't break existing functionality
5. **Documentation**: Update documentation if your changes affect user-facing features
6. **Commit**: Make clear, descriptive commits following conventional commit format
7. **Pull Request**: Submit a pull request with a detailed description

### Running Tests
```bash
# Run all tests
python test_runner.py

# Run specific test files
python -m unittest tests.test_basic
python -m unittest tests.test_cli_integration

# Run with verbose output
python test_runner.py -v
```

### Code Standards
- **Python Style**: Follow PEP 8 with 88-character line limit
- **Type Hints**: Use type hints for all function parameters and return values
- **Documentation**: Add docstrings for all public functions and classes
- **Error Handling**: Implement comprehensive error handling with meaningful messages
- **Testing**: Add tests for new features and bug fixes

### Architecture Guidelines
When contributing, please follow these architectural principles:

#### Module Responsibilities
- **`cli.py`**: Command-line interface and user interaction only
- **`ai_router.py`**: AI model selection and routing logic
- **`todo_manager.py`**: Todo CRUD operations and persistence
- **`config.py`**: Configuration management and validation
- **Integration modules**: Specific external service integration (GitHub, browser, etc.)

#### Design Patterns
- **Dependency Injection**: Pass dependencies rather than creating them within classes
- **Single Responsibility**: Each module should have one clear purpose
- **Error Propagation**: Use exceptions for error handling, not return codes
- **Configuration-driven**: Make behavior configurable rather than hard-coded

### Testing Guidelines
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test cross-module functionality
- **Mock External Services**: Use mocks for AI APIs, GitHub API, etc.
- **Test Configuration**: Test different configuration scenarios
- **Error Testing**: Test error conditions and edge cases

### Documentation Standards
- **README Updates**: Update README.md for user-facing changes
- **Code Comments**: Add comments for complex logic
- **Type Documentation**: Document complex types and data structures
- **Example Updates**: Update examples if APIs change

### Release Process
1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update CHANGELOG.md with new features and fixes
3. **Testing**: Ensure all tests pass on multiple Python versions
4. **Documentation**: Verify all documentation is up to date
5. **Tag Release**: Create a git tag with the version number
6. **GitHub Release**: Create a GitHub release with release notes

## Troubleshooting

### Common Issues

#### Installation Problems
**Issue**: `pip install` fails with permission errors
```bash
# Solution: Use user installation
pip install --user -e .
```

**Issue**: Python version compatibility errors
```bash
# Solution: Check Python version and upgrade if needed
python --version  # Should be 3.8+
# On Ubuntu/Debian: sudo apt update && sudo apt install python3.10
# On macOS: brew install python@3.10  
# On Windows: Download from python.org
```

#### Configuration Issues
**Issue**: API keys not being recognized
```bash
# Solution: Verify configuration
2do setup  # Re-run setup wizard
# Or check config file directly
cat ~/.2do/config.yaml
```

**Issue**: GitHub integration not working
```bash
# Solution: Verify token permissions
# Token needs: repo, issues, pull_requests permissions
# Create new token at: https://github.com/settings/tokens
```

#### Runtime Problems
**Issue**: Browser integration fails to start
- **Cause**: Port already in use or server command not found
- **Solution**: Check if development server is already running, install missing dependencies

**Issue**: AI model routing errors
- **Cause**: Invalid API keys or network connectivity
- **Solution**: Verify API keys and internet connection, check provider status pages

**Issue**: Todo persistence problems  
- **Cause**: File permission issues or disk space
- **Solution**: Check directory permissions for `~/.2do/` or project `2DO/` folder

### Performance Optimization

#### Memory Usage
If experiencing high memory usage:
```bash
# Reduce concurrent tasks
# Edit ~/.2do/config.yaml and set:
multitasking:
  max_workers: 3  # Default is 5
```

#### API Rate Limits
To avoid rate limiting:
- Use smaller batch sizes for multitasking
- Configure appropriate delays between requests
- Monitor your API usage on provider dashboards

### Getting Help

1. **Documentation**: Review this README and inline help (`2do --help`)
2. **Issues**: Search existing [GitHub Issues](https://github.com/STAFE-GROUP-AB/2do-developer/issues)
3. **Community**: Start a [GitHub Discussion](https://github.com/STAFE-GROUP-AB/2do-developer/discussions)
4. **Bug Reports**: Create detailed issue reports with reproduction steps

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please visit the [GitHub Issues](https://github.com/STAFE-GROUP-AB/2do-developer/issues) page.

### Additional Resources
- **Repository**: [STAFE-GROUP-AB/2do-developer](https://github.com/STAFE-GROUP-AB/2do-developer)  
- **Discussions**: [Community discussions and Q&A](https://github.com/STAFE-GROUP-AB/2do-developer/discussions)
- **Documentation**: Comprehensive documentation in this README
- **Examples**: See demo files and test cases in the repository
