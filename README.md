# AI Redirector

🤖 **AI Redirector** is an intelligent command line tool that automatically selects the best AI model for your prompts and enables powerful multitasking capabilities for developers.

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

### ⚡ Multitasking Engine
- Process multiple todos in parallel using optimal AI models
- Intelligent task distribution based on AI model capabilities
- Real-time progress tracking and result aggregation

### 🔧 Tech Stack Detection & Memory
- Automatically detects technology stack from repositories
- Creates intelligent memory files for better context
- Supports 20+ technologies (Python, JavaScript, React, Docker, etc.)
- Provides tech-specific best practices and recommendations

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
# Configure your AI model API keys
airedirector setup
```

### 2. Start Interactive Session
```bash
# Start with a specific repository
airedirector start --repo /path/to/your/project

# Or start without a repository
airedirector start
```

### 3. Available Commands

#### Setup AI Models
The setup command guides you through configuring API keys for various AI providers:
- OpenAI (GPT-4, GPT-3.5, GPT-4 Turbo)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)

#### Interactive Session Features
- **add-todo**: Create new todo items with different types and priorities
- **list-todos**: View all todos in a formatted table
- **start-multitask**: Process all pending todos in parallel
- **chat**: Interactive chat with intelligent AI model routing
- **quit**: Exit the session

## Usage Examples

### Repository Analysis and Todo Generation
```bash
# Analyze a GitHub repository and create todos
airedirector start --repo https://github.com/user/project

# The tool will:
# 1. Detect the tech stack (Python, React, Docker, etc.)
# 2. Create memory files for optimal AI context
# 3. Generate relevant todos (code review, documentation, tests)
# 4. Allow you to add custom todos
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
When you start multitasking, the AI Redirector:
1. Analyzes each todo to determine the best AI model
2. Creates optimized prompts based on todo type and content
3. Processes todos in parallel (up to 5 concurrent tasks)
4. Provides real-time progress tracking
5. Aggregates and displays results

## AI Model Selection Logic

The AI Redirector uses sophisticated analysis to route prompts:

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
- **Frameworks**: React, Vue, Angular, Express, Django, Flask
- **Tools**: Docker, Kubernetes, Terraform
- **Databases**: SQL files, SQLite
- **Build Systems**: Gradle, Maven, CMake, Cargo

## Configuration

Configuration files are stored in `~/.ai_redirector/`:
- `config.yaml`: Main configuration and API keys
- `todos/todos.json`: Todo items storage
- `memory/`: Tech stack memory files

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