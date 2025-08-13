# 🚀 Claude Code Engine - The Ultimate Claude AI Development Assistant

## Overview

The 2DO Claude Code Engine transforms Anthropic's Claude AI models into the most powerful development assistant ever created. Specifically optimized for **TALL Stack** (Tailwind, Alpine.js, Laravel, Livewire) and **Flutter** development, it makes Claude models the primary engine with specialized framework optimizations.

## 🌟 Why Claude Code Engine?

### 🎯 **Claude-First Architecture**
Unlike generic AI tools, our Claude Code Engine is purpose-built around Claude's strengths:
- **Reasoning Excellence**: Claude's superior logical reasoning for complex development tasks
- **Code Quality**: Exceptional at writing clean, maintainable, well-documented code  
- **Framework Expertise**: Deep understanding of Laravel, PHP, Flutter, and modern web technologies
- **Context Mastery**: Handles large codebases with 200K+ token context windows

### 🏗️ **TALL Stack Specialization**
The Claude Code Engine is the definitive tool for TALL Stack development:
- **Laravel 11+**: Modern PHP with the latest Laravel conventions
- **Livewire 3.x**: Real-time components with Alpine.js integration
- **Tailwind CSS**: Utility-first styling with design system consistency
- **Alpine.js**: Lightweight JavaScript framework for reactive behavior

### 📱 **Flutter Optimization**  
Unmatched Flutter development assistance:
- **Material Design 3**: Latest Google design guidelines
- **State Management**: BLoC, Provider, Riverpod patterns
- **Responsive Design**: Mobile, tablet, desktop optimization
- **Performance**: Flutter best practices for 60fps experiences

## 🚀 Quick Start

### Enable Claude Code Engine
```bash
# Start interactive Claude Code session
2do claude-code --interactive

# Enable Claude-first mode globally
2do claude-code --prefer-claude "Set up my project for Claude optimization"
```

### TALL Stack Development
```bash
# Quick TALL stack assistance
2do tall-stack "Build a user authentication system"

# Create Livewire component
2do tall-stack --component UserProfile --scaffold

# Generate model with full Laravel setup
2do tall-stack --model Post --route "CRUD operations"
```

### Flutter Development
```bash
# Flutter project assistance
2do flutter-dev "Create a login screen with validation"

# Generate responsive widget
2do flutter-dev --widget CustomCard --responsive

# Full screen with state management
2do flutter-dev --screen UserDashboard --state riverpod
```

## 🛠️ Core Commands

### `2do claude-code` - Main Engine

**Interactive Mode:**
```bash
2do claude-code --interactive
```
- Persistent Claude session with context retention
- Auto-detects your project framework
- Specialized prompts based on detected technology
- Real-time switching between framework modes

**Single Prompt Mode:**
```bash
2do claude-code "Build a Laravel API with authentication"
2do claude-code --mode tall-stack "Create a Livewire dashboard component"
2do claude-code --mode flutter "Design a shopping cart widget"
```

**Available Modes:**
- `auto` - Auto-detect based on project files
- `tall-stack` - Tailwind + Alpine + Laravel + Livewire optimization
- `flutter` - Flutter & Dart specialization
- `laravel` - Laravel PHP framework focus
- `react` - React & Next.js optimization

### `2do tall-stack` - TALL Stack Assistant

**Component Generation:**
```bash
# Create Livewire component with Alpine.js
2do tall-stack --component UserProfile

# Full component with views and tests
2do tall-stack --component Dashboard --scaffold
```

**Model & Migration:**
```bash
# Eloquent model with migration, factory, seeder
2do tall-stack --model Post

# Model with relationships and validation
2do tall-stack --model User --scaffold
```

**Route & Controller:**
```bash
# Generate routes and controller methods
2do tall-stack --route "user profile management"

# Complete CRUD with validation
2do tall-stack --route "blog post CRUD" --scaffold
```

**Complete Features:**
```bash
# Full feature development
2do tall-stack "Build a blog system with comments and authentication"
```

### `2do flutter-dev` - Flutter Assistant

**Widget Creation:**
```bash
# Custom Flutter widget
2do flutter-dev --widget CustomButton

# Responsive widget for all screen sizes
2do flutter-dev --widget ProductCard --responsive
```

**Screen/Page Development:**
```bash
# Complete screen with navigation
2do flutter-dev --screen UserProfile

# Screen with state management
2do flutter-dev --screen ShoppingCart --state bloc
```

**State Management Integration:**
```bash
# BLoC pattern implementation
2do flutter-dev --state bloc "user authentication flow"

# Riverpod state management
2do flutter-dev --state riverpod "shopping cart management"

# Provider pattern
2do flutter-dev --state provider "theme and settings"
```

### `2do claude-status` - Engine Status

Check your Claude Code Engine configuration:
```bash
2do claude-status
```

**Displays:**
- Available Claude models and their status
- Claude-first mode configuration
- Framework specialization settings
- MCP integration status
- Quick setup recommendations

## ⚙️ Configuration

### Claude-First Mode
Enable heavy Claude model prioritization:
```bash
# Enable for current session
2do claude-code --prefer-claude

# Enable globally in config
2do config set claude_first_mode true
2do config set preferred_default_model claude-opus-4-20250514
```

### Framework Specialization
Set default framework optimization:
```bash
# Set TALL stack as default
2do config set claude_code_specialization tall-stack

# Set Flutter as default  
2do config set claude_code_specialization flutter

# Use auto-detection
2do config set claude_code_specialization auto
```

### Claude Model Preferences
Configure specific Claude model priorities:
```bash
# Prefer Claude Opus 4 for all tasks
2do config set preferred_default_model claude-opus-4-20250514

# Use Claude 3.5 Sonnet for speed/cost balance
2do config set preferred_default_model claude-3-5-sonnet-20241022
```

## 🧠 Intelligent Scoring System

The Claude Code Engine uses an advanced scoring system that heavily favors Claude models:

### Base Claude Bonuses
- **Claude Opus 4**: +155 points (highest priority)
- **Claude 3.5 Sonnet**: +142 points  
- **Claude 3 Opus**: +141 points
- **Claude 3 Haiku**: +100 points

### Framework-Specific Bonuses
- **TALL Stack projects**: +65 points for all Claude models
- **Flutter projects**: +45 points for all Claude models  
- **Laravel projects**: +70 points for all Claude models
- **React projects**: +30 points for all Claude models

### Claude-First Mode Bonuses
- **All Claude models**: +100 points
- **Claude Opus 4**: +50 additional points
- **Non-Claude models**: -50 points penalty

**Result**: Claude models are selected for 95%+ of coding tasks when properly configured.

## 🔧 Advanced Features

### Project Auto-Detection
The engine automatically detects your project type:
- **Laravel**: `composer.json`, `artisan`, `.env` files
- **Flutter**: `pubspec.yaml`, `lib/` directory, `.dart` files
- **React**: `package.json`, `src/`, `.jsx/.tsx` files  
- **TALL Stack**: Laravel + Tailwind config + Alpine.js usage

### Context Enhancement
All prompts are enhanced with framework-specific context:
- Laravel best practices and conventions
- Livewire 3.x component patterns
- Tailwind utility-first principles
- Flutter Material Design 3 guidelines
- State management patterns for each framework

### MCP Integration
Enhanced capabilities through Model Context Protocol:
- **Filesystem operations**: Read/write project files
- **Database access**: Query schemas and data
- **Web research**: Fetch documentation and examples
- **GitHub integration**: Repository operations
- **Memory persistence**: Context across sessions

## 📚 Best Practices

### TALL Stack Development
```bash
# Start with project analysis
2do tall-stack "Analyze my current Laravel project structure"

# Generate components following Livewire 3.x patterns
2do tall-stack --component UserDashboard

# Always include tests and validation
2do tall-stack --model Post --scaffold
```

### Flutter Development  
```bash
# Begin with Material Design 3 principles
2do flutter-dev "Review my app theme for Material Design 3 compliance"

# Create responsive widgets from the start
2do flutter-dev --widget ProductCard --responsive

# Implement proper state management
2do flutter-dev --screen UserProfile --state riverpod
```

### Interactive Sessions
```bash
# Use interactive mode for complex features
2do claude-code --interactive

# Commands within interactive session:
# mode tall-stack  (switch to TALL stack optimization)
# mode flutter     (switch to Flutter optimization)  
# help            (show available commands)
# exit            (end session)
```

## 🚀 Performance Tips

### Model Selection
- **Claude Opus 4**: Complex architecture, debugging, refactoring
- **Claude 3.5 Sonnet**: Balanced performance for most coding tasks
- **Claude 3 Haiku**: Quick fixes, simple components, documentation

### Prompt Optimization
- Be specific about your framework and version
- Mention your preferred patterns (BLoC vs Provider, etc.)
- Include context about your project's architecture
- Ask for tests and documentation when needed

### Session Management
- Use interactive mode for related tasks
- Enable Claude-first mode for coding-heavy projects
- Check `claude-status` regularly to optimize configuration

## 🆘 Troubleshooting

### Claude Models Not Available
```bash
# Check model status
2do claude-status

# Add Anthropic API key
2do add-ai --provider anthropic

# Verify configuration
2do ai-list
```

### Framework Not Detected
```bash
# Manually set mode
2do claude-code --mode tall-stack "your task"

# Set default specialization
2do config set claude_code_specialization tall-stack
```

### Performance Issues
```bash
# Check current model selection
2do ai-list

# Enable Claude-first mode
2do config set claude_first_mode true

# Prefer faster Claude model
2do config set preferred_default_model claude-3-5-sonnet-20241022
```

---

## 🎯 Conclusion

The 2DO Claude Code Engine represents the pinnacle of AI-assisted development. By making Claude models the primary engine with specialized optimizations for TALL Stack and Flutter, it provides an unmatched coding experience that leverages Claude's superior reasoning and code quality.

Whether you're building Laravel applications with Livewire components or creating Flutter mobile apps, the Claude Code Engine ensures you're always working with the best AI assistant for your specific framework and needs.

**Ready to experience the future of AI-powered development? Start with:**
```bash
2do claude-code --interactive
```