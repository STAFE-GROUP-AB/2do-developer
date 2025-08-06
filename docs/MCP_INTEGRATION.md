# 🚀 Advanced MCP Server Integration

## Overview

2do now supports advanced MCP (Model Context Protocol) servers inspired by the Laravel Claude Code CLI, providing AI with powerful capabilities for web research, persistent memory, database operations, and design system integration.

## 🌟 Available MCP Servers

### 1. **Filesystem MCP** (Official)
- **Status**: ✅ Always enabled
- **Capabilities**: File operations, directory management, content reading/writing
- **Tools**: `read_text_file`, `write_file`, `create_directory`, `list_directory`, etc.

### 2. **Web Fetch MCP** (Community)
- **Package**: `@zcaceres/fetch-mcp`
- **Capabilities**: Web scraping, API calls, documentation research
- **Tools**: 
  - `web_fetch` - Fetch content from URLs
  - `web_search` - Search the web for information

### 3. **Memory MCP** (Official)
- **Package**: `@modelcontextprotocol/server-memory`
- **Capabilities**: Persistent context storage across sessions
- **Tools**:
  - `memory_store` - Store information with keys and tags
  - `memory_retrieve` - Retrieve stored information
  - `memory_list` - List all stored memory keys

### 4. **Database MCP** (Community)
- **Capabilities**: Direct database operations and schema analysis
- **Auto-detection**: Automatically detects SQLite, MySQL, PostgreSQL
- **Tools**:
  - `db_query` - Execute SQL queries
  - `db_schema` - Get database schema
  - `db_tables` - List all tables

### 5. **Figma MCP** (Community)
- **Package**: `figma-developer-mcp`
- **Capabilities**: Design system integration, component access
- **Requirements**: Figma Personal Access Token
- **Tools**:
  - `figma_file` - Get file information and components
  - `figma_components` - Access design system components
  - `figma_styles` - Get design tokens and styles

### 6. **GitHub MCP** (Official)
- **Package**: `@modelcontextprotocol/server-github`
- **Capabilities**: Enhanced repository operations with authentication
- **Requirements**: GitHub Personal Access Token
- **Tools**: Repository management, issue tracking, PR operations

## 🛠️ Configuration

### Interactive Setup
```bash
2do mcp --interactive
```

This launches an interactive configuration wizard that:
- Detects existing database configurations
- Guides you through token setup for Figma and GitHub
- Automatically configures compatible servers
- Provides setup instructions for external services

### List Configured Servers
```bash
2do mcp --list
```

Shows a table of all configured MCP servers with their status and descriptions.

## 🔐 Token Management

### Environment Variables (Recommended)
```bash
export GITHUB_TOKEN="your_github_token_here"
export FIGMA_ACCESS_TOKEN="your_figma_token_here"
```

### Configuration File Storage
Tokens can also be stored in the 2do configuration file with automatic encryption.

### Token Priority
1. Environment variables (highest priority)
2. Configuration file storage
3. Interactive prompts during setup

## 🎯 Usage Examples

### Web Research
```bash
2do "Research the latest React 19 features and update our component library"
```
AI can now fetch documentation, blog posts, and API references directly.

### Persistent Memory
```bash
2do "Remember that we use TypeScript strict mode and prefer functional components"
```
Context is stored and retrieved across sessions automatically.

### Database Operations
```bash
2do "Analyze our user table schema and suggest performance optimizations"
```
AI can directly query and analyze your database structure.

### Design System Integration
```bash
2do "Get our button component variants from Figma and generate React components"
```
AI can access your Figma design system and generate corresponding code.

## 🔧 Advanced Configuration

### Manual Server Configuration
Edit `~/.config/2do/config.json`:

```json
{
  "mcp_servers": [
    {
      "name": "web-fetch",
      "command": "npx",
      "args": ["-y", "@zcaceres/fetch-mcp"],
      "type": "community",
      "enabled": true,
      "description": "Web scraping and API calls"
    }
  ],
  "mcp_tokens": {
    "github": "your_token_here",
    "figma": "your_token_here"
  }
}
```

### Database Auto-Detection
The system automatically detects:
- `.env` files with `DATABASE_URL` or `DB_CONNECTION`
- SQLite files (`database.sqlite`, `db.sqlite3`, `data.db`)
- Common database configuration patterns

### Custom Server Integration
Add custom MCP servers by extending the configuration:

```json
{
  "name": "custom-server",
  "command": "your-command",
  "args": ["--arg1", "--arg2"],
  "type": "custom",
  "enabled": true,
  "description": "Your custom MCP server"
}
```

## 🚨 Troubleshooting

### Server Initialization Failures
- Check if required packages are installed (`npx` for Node.js packages)
- Verify tokens are correctly configured
- Ensure network connectivity for web-based servers

### Token Issues
- Verify token permissions and scopes
- Check environment variable names match exactly
- Use `2do mcp --list` to verify server status

### Database Connection Issues
- Ensure database files exist and are readable
- Check database server is running (for MySQL/PostgreSQL)
- Verify connection strings in `.env` files

## 🎉 Benefits

### For Developers
- **Faster Research**: AI can fetch documentation and examples directly
- **Better Context**: Persistent memory across development sessions
- **Database Insights**: Direct analysis of database schemas and data
- **Design Consistency**: Integration with Figma design systems

### For Teams
- **Shared Knowledge**: Memory MCP stores team conventions and decisions
- **Automated Documentation**: AI can research and document best practices
- **Design-Code Sync**: Figma integration ensures design system consistency

## 🔮 Future Enhancements

- **Slack/Discord MCP**: Team communication integration
- **Jira/Linear MCP**: Project management integration
- **AWS/GCP MCP**: Cloud infrastructure management
- **Docker MCP**: Container and deployment management

---

*This integration is inspired by the Laravel Claude Code CLI and represents the cutting edge of AI-assisted development workflows.*
