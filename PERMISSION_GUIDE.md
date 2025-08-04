# 2DO File Permission Guide

This guide explains how to ensure the 2DO application has proper file permissions to create and update files.

## Overview

The 2DO application requires write access to create and manage:
- Configuration files (`.2do/config.yaml`)
- Todo databases (`.2do/todos/todos.json`)
- Memory files (`.2do/memory/*.json`)
- Log files (`.2do/logs/*.log`)
- Temporary files for image processing

## Automatic Permission Handling

The 2DO application includes robust automatic permission handling:

### 1. **Smart Directory Selection**
- Tries preferred locations first (local project, home directory)
- Falls back to alternative locations if permissions are insufficient
- Uses temporary directories as a last resort

### 2. **Error Recovery**
- Graceful handling of permission errors
- Automatic backup file creation when primary saves fail
- Clear user feedback about permission issues

### 3. **Security**
- Proper file permissions (644 for files, 755 for directories)
- Secure temporary file handling
- No hardcoded paths that might cause conflicts

## Directory Structure

### Global Configuration (Default)
```
~/.2do/
├── config.yaml          # Main configuration
├── todos/
│   └── todos.json       # Todo database
├── memory/
│   └── *.json          # Analysis memory files
└── logs/
    └── *.log           # Application logs
```

### Local Project Configuration (Git Repositories)
```
project-root/
├── 2DO/
│   ├── config.yaml     # Project-specific config
│   ├── todos/
│   │   └── todos.json  # Project todos
│   └── memory/
│       └── *.json      # Project memory files
└── .git/               # Git repository marker
```

## Permission Requirements

### Minimum Requirements
- **Read/Write access** to home directory (`~`)
- **Read/Write access** to system temp directory (`/tmp` or equivalent)
- **Execute permissions** on Python interpreter

### Recommended Setup
- **755 permissions** on directories (rwxr-xr-x)
- **644 permissions** on files (rw-r--r--)
- **User ownership** of all 2DO files and directories

## Fixing Permission Issues

### Automatic Fix (Recommended)
Run the included permission fix script:

```bash
# From the 2DO project directory
python fix_permissions.py
```

This script will:
1. Check current permission status
2. Create necessary directories
3. Fix permissions recursively
4. Verify the setup
5. Provide diagnostic information

### Manual Fix
If automatic fixing doesn't work:

```bash
# Create directories with proper permissions
mkdir -p ~/.2do/{todos,memory,logs}
chmod 755 ~/.2do ~/.2do/todos ~/.2do/memory ~/.2do/logs

# Fix existing file permissions
find ~/.2do -type d -exec chmod 755 {} \;
find ~/.2do -type f -exec chmod 644 {} \;
```

### Project-Specific Fix
For local project configurations:

```bash
# In your git repository
mkdir -p 2DO/{todos,memory,logs}
chmod 755 2DO 2DO/todos 2DO/memory 2DO/logs
```

## Troubleshooting

### Common Issues

#### 1. **"Permission denied" errors**
**Cause**: Insufficient write permissions
**Solution**: 
- Run `python fix_permissions.py`
- Check directory ownership: `ls -la ~/.2do`
- Ensure you have write access to home directory

#### 2. **"Directory not found" errors**
**Cause**: Missing directories
**Solution**:
- Run `python fix_permissions.py` to create directories
- Manually create: `mkdir -p ~/.2do/{todos,memory,logs}`

#### 3. **"Cannot save configuration" warnings**
**Cause**: Read-only filesystem or permission issues
**Solution**:
- Check filesystem mount options: `mount | grep $(df ~ | tail -1 | awk '{print $1}')`
- Verify disk space: `df -h ~`
- Run permission fix script

#### 4. **Temporary directory fallback**
**Cause**: No write access to preferred locations
**Effect**: Data won't persist between sessions
**Solution**:
- Fix permissions in home directory
- Ensure `~/.2do` is writable

### Advanced Troubleshooting

#### Check Current Permissions
```bash
# Check 2DO directory permissions
ls -la ~/.2do/

# Check file permissions
ls -la ~/.2do/config.yaml ~/.2do/todos/todos.json

# Check directory write access
touch ~/.2do/test_file && rm ~/.2do/test_file && echo "Write access OK"
```

#### System-Level Issues
```bash
# Check if running in restricted environment
id
whoami
pwd

# Check available disk space
df -h ~

# Check filesystem mount options
mount | grep $(df ~ | tail -1 | awk '{print $1}')
```

## Security Considerations

### File Permissions
- **Never use 777 permissions** - this is a security risk
- **Use 755 for directories** - allows read/execute for others
- **Use 644 for files** - allows read for others, write for owner only

### API Keys and Secrets
- Configuration files may contain API keys
- Ensure proper file permissions (644) to prevent unauthorized access
- Consider using environment variables for sensitive data

### Temporary Files
- Image files are stored in system temp directory
- Temporary files are automatically cleaned up
- No sensitive data is stored in temp files

## Platform-Specific Notes

### macOS
- Home directory: `/Users/username`
- Temp directory: `/tmp` or `/var/folders/...`
- May require Gatekeeper permissions for some operations

### Linux
- Home directory: `/home/username`
- Temp directory: `/tmp`
- Standard Unix permissions apply

### Windows (WSL)
- Home directory: `/home/username` (in WSL)
- Temp directory: `/tmp`
- May have additional permission complexities with Windows filesystem

## Integration with Development Tools

### Git Integration
- Local project configurations are stored in `2DO/` directory
- Add `2DO/` to `.gitignore` if you don't want to commit configurations
- API keys in configurations should never be committed

### IDE Integration
- Ensure your IDE has read/write access to 2DO directories
- Some IDEs may require explicit permission grants

### CI/CD Considerations
- In CI environments, ensure write access to temp directories
- Use environment variables for API keys in CI
- Consider read-only mode for CI builds

## Getting Help

If you continue to experience permission issues:

1. **Run diagnostics**: `python -c "from twodo.permission_manager import diagnose_permissions; diagnose_permissions()"`
2. **Check the logs**: Look in `~/.2do/logs/` for detailed error messages
3. **Report issues**: Include diagnostic output when reporting bugs
4. **System administrator**: Contact your system admin for enterprise environments

## Best Practices

1. **Regular maintenance**: Periodically run `python fix_permissions.py`
2. **Backup configurations**: Keep backups of important configurations
3. **Monitor disk space**: Ensure adequate space in home directory
4. **Security updates**: Keep file permissions secure but functional
5. **Environment variables**: Use environment variables for sensitive configuration

---

*This guide covers the comprehensive permission management system built into 2DO. The application is designed to work in various environments with automatic fallbacks and clear error reporting.*
