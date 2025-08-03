# 2DO

🤖 **2DO** is an intelligent command line tool that automatically selects the best AI model for your prompts and enables powerful multitasking capabilities for developers.

## Features

### 🎯 Intelligent AI Model Routing
- Automatically analyzes your prompts to determine the most suitable AI model
- Supports multiple AI providers (OpenAI, Anthropic, and more)
- Optimizes for speed, cost, and task complexity

### 📋 Advanced Todo Management
- Create and manage todos for codebases and projects
- Support for text, code, image, and general task types
- Priority-based organization (low, medium, high, critical)
- Automatic todo generation from repository analysis
- Import tasks from markdown files
- Export todos as GitHub issues

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
- Built-in support for MCP (Model Context Protocol) servers
- Extensible architecture for adding custom integrations
- Enhanced context and capabilities for AI models

## Installation

```bash
# Clone the repository
git clone https://github.com/STAFE-GROUP-AB/AI-Redirector.git
cd AI-Redirector

# Install dependencies
pip install -r requirements.txt

# Install the package
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
- **parse-markdown**: Extract tasks from markdown files and convert to todos
- **github-issues**: Work with GitHub issues (list, work on, create todos from issues)
- **create-github-issue**: Create new GitHub issues directly
- **export-todos-to-github**: Export your todos as GitHub issues
- **chat**: Interactive chat with intelligent AI model routing (supports images)
- **quit**: Exit the session

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