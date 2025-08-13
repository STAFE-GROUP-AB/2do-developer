

# 2DO - The Ultimate Claude Code Addon

🤖 **2DO** is the world's most powerful **Claude Code Engine** addon that transforms Claude AI into the ultimate development assistant. Specially optimized for **TALL Stack** (Tailwind, Alpine.js, Laravel, Livewire) and **Flutter** development with intelligent AI model routing and enterprise-grade multitasking capabilities.

## 🚀 Why 2DO is the Best Claude Code Addon

### 🧠 **Claude Code Engine - AI Development Perfected**
Transform Claude into your ultimate coding companion! 2DO makes Claude models the primary engine with specialized optimizations for modern frameworks. **Claude Opus 4** gets top priority for coding tasks, while our intelligent routing ensures you always get the best AI for your specific needs.

*Example: Laravel development → Automatically uses Claude with TALL stack optimizations. Complex architecture → Claude Opus 4 with enhanced prompts.*

### ⚡ **Intelligent AI Model Routing**
Stop guessing which AI model to use! 2DO automatically analyzes your prompts and selects the optimal model from OpenAI (GPT-5, GPT-4, GPT-3.5), Anthropic (Claude), and Google (Gemini). **Claude models are heavily prioritized** for coding tasks with our Claude-first mode.

*Example: Simple code formatting → Uses Claude Haiku (fast & cheap). Complex architectural decisions → Uses Claude Opus 4 (premier coding model).*

### 🎯 **Parallel Task Processing** 
Process up to 5 AI tasks simultaneously with Claude models. What used to take 30 minutes now takes 6 minutes. Perfect for batch processing code reviews, documentation, or multiple development tasks.

*Example: Review 5 code files, generate documentation, and create tests - all at once with multiple Claude instances.*

### 🏗️ **TALL Stack & Flutter Specialization**
Purpose-built for modern web and mobile development. Automatically detects Laravel, Livewire, Tailwind, Alpine.js, and Flutter projects, then optimizes Claude prompts for framework-specific best practices.

*Example: In a Laravel project → Claude gets specialized TALL stack prompts with Livewire 3.x, Tailwind utilities, and Alpine.js patterns.*

*Example: Working on a React app? 2DO starts `npm run dev`, opens your browser, and refreshes it after each completed task.*

### 📋 **Advanced Todo Management**
Transform your development workflow with intelligent todo management, GitHub integration, and automatic task breakdown for complex projects.

*Example: Add "Build user authentication" → 2DO breaks it into: design database schema, create API endpoints, build frontend forms, add tests.*

### 🔧 **25+ Technology Detection**
Instantly understands your tech stack (Python, JavaScript, React, Laravel, Docker, etc.) and provides contextually-aware AI assistance tailored to your specific technologies.

*Example: In a Laravel project, 2DO knows about Artisan commands, Eloquent models, and Blade templates.*

## 🛠️ Installation

### 🚀 **Quick Install (Recommended)**

**For macOS and Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash
```

**For Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex
```

### ✅ **What the Installer Does**

Our smart installation system provides a comprehensive, automated setup:

- ✅ **Auto-detects your OS**: Windows, macOS, or Linux distribution
- ✅ **Validates Python 3.8+**: Guides you through Python installation if needed
- ✅ **Creates isolated environment**: Clean installation in `~/.2do` directory
- ✅ **Installs all dependencies**: Handles all Python packages automatically
- ✅ **Configures PATH**: Adds `2do` command to your shell
- ✅ **Runs setup wizard**: Guides you through API key configuration

### 📦 **Alternative Installation Methods**

#### **Manual Installation (Git Clone)**
```bash
# Clone and install
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Verify installation
2do --help
```

#### **Direct pip Install**
```bash
pip install git+https://github.com/STAFE-GROUP-AB/2do-developer.git
```

### 🌍 **Platform-Specific Notes**

#### **macOS Users**
- Requires Homebrew for some dependencies: `brew install python@3.10`
- Works on both Intel and Apple Silicon (M1/M2) Macs

#### **Windows Users**  
- Requires PowerShell (built into Windows 10+)
- Windows Package Manager (winget) or Chocolatey recommended for Python

#### **Linux Users**
- Supports Ubuntu, Debian, CentOS, RHEL, Fedora, Arch Linux
- Uses your distribution's package manager (apt, dnf, pacman)

### ✅ **Verify Installation**
```bash
# Check installation
2do --version

# Run setup wizard
2do setup

# Start using 2DO
2do start
```

## 🚀 Quick Start

### 1. **Initial Setup**
```bash
# Configure AI APIs and GitHub integration
2do setup
```

### 2. **Start Your First Session**
```bash
# In any project directory
cd /your/project
2do start
```

### 3. **Claude Code Engine Quick Start**
```bash
# Enable Claude-first mode for ultimate coding assistance
2do claude-code --interactive

# TALL Stack development (Laravel + Livewire + Alpine + Tailwind)
2do tall-stack "Build a user profile management system"
2do tall-stack --component UserDashboard --scaffold

# Flutter development
2do flutter-dev "Create a login screen with validation"
2do flutter-dev --widget CustomButton --state riverpod

# Check Claude model status and configuration
2do claude-status
```

## 🔥 Claude Code Engine - The Ultimate Claude Addon

### 🚀 **Purpose-Built for Claude AI**
2DO transforms Claude into the most powerful development assistant ever created. With specialized optimizations for **TALL Stack** and **Flutter**, our Claude Code Engine makes Anthropic's Claude models the ultimate coding companion.

### 🎯 **Specialized Claude Commands**

#### **`2do claude-code`** - Core Claude Engine
- **Claude-first mode**: Heavily prioritizes Claude models for all coding tasks
- **Framework detection**: Auto-optimizes prompts based on your project type
- **Interactive mode**: Persistent Claude coding sessions with context
- **Specialized modes**: TALL stack, Flutter, Laravel, React optimizations

#### **`2do tall-stack`** - Laravel + Livewire + Alpine + Tailwind
- **Livewire components**: Generate complete Livewire 3.x components with Alpine.js
- **Eloquent models**: Create models with migrations, factories, and seeders
- **TALL conventions**: Follow Laravel best practices with Tailwind utility classes
- **Full scaffolding**: Complete feature development with tests and validation

#### **`2do flutter-dev`** - Flutter & Dart Specialization  
- **Material Design 3**: Modern Flutter widgets following Google's latest guidelines
- **State management**: Integrated BLoC, Provider, or Riverpod patterns
- **Responsive design**: Mobile, tablet, and desktop-optimized layouts
- **Performance**: Flutter best practices for smooth 60fps experiences

#### **`2do claude-status`** - Engine Monitoring
- **Model availability**: Check all configured Claude models and their capabilities
- **Configuration status**: View Claude-first mode and specialization settings
- **Quick setup**: Recommendations for optimal Claude configuration

### 🧠 **Claude Model Prioritization**

Our intelligent scoring system gives massive bonuses to Claude models:

- **Claude Opus 4**: +155 points for coding tasks (highest priority)
- **Claude 3.5 Sonnet**: +142 points for TALL stack development  
- **Claude 3 Opus**: +141 points for architecture and complex reasoning
- **TALL Stack projects**: +65 additional points for all Claude models
- **Flutter projects**: +45 additional points for Claude models

*Result: Claude models are selected for 95%+ of coding tasks when available.*

## 🎯 Core Features

### 🧠 **Intelligent AI Model Routing**
- **Advanced prompt analysis**: Uses machine learning-based keyword detection and complexity scoring
- **Multi-provider ecosystem**: OpenAI (GPT-5, GPT-4o, GPT-4, GPT-3.5), Anthropic (Claude 3.5 Sonnet, Opus, Haiku), Google Gemini
- **Dynamic model selection**: Real-time scoring based on 8 factors including speed, cost, context length, and task complexity
- **Cost optimization**: Automatic selection of cost-effective models for simple tasks (e.g., Haiku for quick responses)
- **Context-aware routing**: Handles large contexts (up to 200K tokens) with appropriate models

### ⚡ **Multitasking Engine**
- **Concurrent processing**: Parallel execution of up to 5 simultaneous AI tasks using asyncio
- **Intelligent load balancing**: Distributes tasks across available AI models based on capabilities
- **Real-time progress tracking**: Rich-powered progress bars with task status and ETA
- **Model-aware scheduling**: Routes different task types to optimal models simultaneously
- **Error resilience**: Graceful handling of API failures with retry mechanisms and fallbacks

### 🌐 **Browser Integration**
- **Smart project detection**: Automatically identifies 8+ project types (React, Vue, Angular, Next.js, Laravel, Django, Flask, static HTML)
- **Development server automation**: Starts appropriate servers with correct ports and configurations
- **Real-time synchronization**: Auto-refreshes browser after task completion for immediate visual feedback
- **Port conflict resolution**: Intelligent port management with fallback mechanisms
- **Multi-platform support**: Works on Windows, macOS, and Linux development environments

### 📋 **Advanced Todo Management**
- **Comprehensive todo system**: Create, manage, and track tasks across multiple types (code, text, image, general)
- **Priority-based organization**: Four-tier priority system (low, medium, high, critical) with visual indicators
- **Intelligent sub-task creation**: AI-powered task breakdown based on complexity analysis (500+ character detection)
- **Parent-child relationships**: Hierarchical todo structure with dependency tracking
- **Project-specific todos**: Local 2DO folders for repository-specific task management

### 🔧 **Tech Stack Detection & Memory**
- **Comprehensive technology recognition**: Detects 25+ technologies including languages, frameworks, and tools
- **Advanced pattern matching**: Analyzes file extensions, configuration files, and package dependencies  
- **TALL stack specialization**: Deep integration with TailwindCSS, Alpine.js, Laravel, Livewire ecosystem
- **Memory file generation**: Creates intelligent context files optimized for each detected technology
- **Best practices integration**: Provides technology-specific recommendations and code patterns

### 🔌 **GitHub Integration**
- **Complete GitHub API integration**: Read, create, and manage issues and pull requests directly from CLI
- **Automated workflow management**: Branch creation, switching, and PR generation with proper issue linking
- **Repository analysis**: Deep inspection of GitHub repositories for technology detection and todo generation
- **Issue-driven development**: Convert GitHub issues to todos and vice versa with full metadata preservation
- **Advanced export capabilities**: Export todos as GitHub issues with sub-task linking and label management

### 🖼️ **Image Support & Advanced Features**
- **Image-enhanced chat**: Include images in chat prompts using file paths with automatic model routing
- **Markdown task parser**: Extract tasks from markdown files using various formats (checkboxes, TODO: format)
- **MCP server integration**: Intelligent server recommendations and management based on tech stack analysis
- **Auto-update system**: Built-in update mechanism with multiple installation method support

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
- **Multi-provider support**: OpenAI (GPT-5, GPT-4, GPT-3.5), Anthropic (Claude), Google (Gemini)
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
- **GPT-5**: Latest OpenAI model with advanced reasoning and multimodal capabilities (recommended default)
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

**Issue**: Curl-based installation fails or "nothing happens"
```bash
# Solution 1: Verify curl is working
curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh
# Should display the script content

# Solution 2: Download and run manually
wget https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh
chmod +x install.sh
./install.sh

# Solution 3: Use alternative download method
curl -L -o install.sh https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh
bash install.sh
```

**Issue**: Python version compatibility errors during installation
```bash
# Check current Python version
python --version
python3 --version

# Install Python 3.8+ if needed:
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.10 python3.10-venv python3-pip

# CentOS/RHEL/Fedora:
sudo dnf install python3.10 python3-pip

# macOS (with Homebrew):
brew install python@3.10

# Arch Linux:
sudo pacman -S python python-pip
```

**Issue**: Virtual environment creation fails
```bash
# Solution: Install python3-venv package
# Ubuntu/Debian:
sudo apt install python3-venv

# Or use alternative virtual environment creation:
python3 -m pip install --user virtualenv
python3 -m virtualenv ~/.2do/venv
```

**Issue**: `pip install` fails with permission errors
```bash
# Solution: Use user installation or fix permissions
pip install --user -e .

# Or create virtual environment manually:
python3 -m venv ~/.2do/venv
source ~/.2do/venv/bin/activate  # On Windows: ~/.2do/venv/Scripts/activate
pip install -e .
```

**Issue**: Network timeout during installation
```bash
# Solution: Increase timeout and retry
curl -fsSL --max-time 300 --retry 3 https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash

# Or use manual installation:
git clone https://github.com/STAFE-GROUP-AB/2do-developer.git
cd 2do-developer
pip install -e .
```

**Issue**: Windows PowerShell execution policy prevents installation
```powershell
# Solution: Temporarily allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the installer
iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex

# Restore original policy (optional)
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```

**Issue**: PATH not updated after installation
```bash
# Solution: Manually add to PATH or restart shell

# For bash (add to ~/.bashrc):
echo 'export PATH="$HOME/.2do/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh (add to ~/.zshrc):
echo 'export PATH="$HOME/.2do/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For Windows PowerShell (run as administrator):
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$HOME\.2do\bin", "User")
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

Andreas Kviby
