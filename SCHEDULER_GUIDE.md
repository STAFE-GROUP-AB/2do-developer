# 2DO Scheduler Documentation

The 2DO Scheduler adds powerful automation capabilities to the 2DO tool, allowing you to schedule and automate tasks like GitHub synchronization, code reviews, and todo management.

## Features

### Core Capabilities
- **Cron-based Scheduling**: Use standard cron expressions for flexible timing
- **Multiple Task Types**: Support for GitHub sync, multitasking, custom commands, AI prompts, and more
- **JSON Configuration**: Simple JSON files for easy schedule management
- **Daemon Mode**: Run scheduler continuously in the background
- **Manual Triggers**: Test schedules manually before scheduling them
- **Rich CLI Interface**: Beautiful command-line interface with progress tracking

### Supported Task Types

1. **github_sync** - Sync GitHub issues and create todos
2. **multitask** - Run multitasking on pending todos  
3. **add_todo** - Add new todos programmatically
4. **create_branch** - Create git branches for issue work
5. **github_pr** - Create GitHub pull requests
6. **custom_command** - Execute shell commands
7. **ai_prompt** - Execute AI prompts and save results

## Quick Start

### 1. List Current Schedules
```bash
2do schedule list
```

### 2. Add a New Schedule
```bash
2do schedule add
```
Follow the interactive prompts to create your schedule.

### 3. Manually Trigger a Schedule (Testing)
```bash
2do schedule trigger schedule-name
```

### 4. Start Scheduler in Daemon Mode
```bash
2do scheduler --daemon
```

### 5. View Scheduler Status
```bash
2do scheduler
```

## Schedule Configuration

Schedules are stored as JSON files in the `2do/schedules/` folder (or `~/.2do/schedules/` for global schedules).

### Example Schedule File

```json
{
  "name": "daily-github-sync",
  "description": "Sync GitHub issues daily at 7 AM on weekdays",
  "schedule": "0 7 * * 1-5",
  "enabled": true,
  "tasks": [
    {
      "type": "github_sync",
      "config": {
        "action": "sync_issues",
        "create_todos": true
      }
    },
    {
      "type": "multitask",
      "config": {
        "filter": "priority:high",
        "max_parallel": 3
      }
    }
  ]
}
```

### Schedule Fields

- **name**: Unique identifier for the schedule
- **description**: Human-readable description of what the schedule does
- **schedule**: Cron expression (e.g., "0 7 * * 1-5" for 7 AM weekdays)
- **enabled**: Boolean flag to enable/disable the schedule
- **tasks**: Array of tasks to execute when the schedule triggers

### Cron Expression Examples

- `0 7 * * 1-5` - 7:00 AM, Monday through Friday
- `0 */1 * * *` - Every hour
- `0 9-17 * * 1-5` - Every hour from 9 AM to 5 PM, weekdays only
- `0 17 * * 5` - 5:00 PM every Friday
- `*/30 * * * *` - Every 30 minutes

## Task Configuration

### github_sync
```json
{
  "type": "github_sync",
  "config": {
    "action": "sync_issues",
    "create_todos": true
  }
}
```

### multitask
```json
{
  "type": "multitask",
  "config": {
    "filter": "priority:high",
    "max_parallel": 3
  }
}
```

### add_todo
```json
{
  "type": "add_todo",
  "config": {
    "content": "Review weekly progress and plan next steps",
    "type": "general",
    "priority": "medium"
  }
}
```

### custom_command
```json
{
  "type": "custom_command",
  "config": {
    "command": "git status && git log --oneline -5",
    "working_dir": "."
  }
}
```

### ai_prompt
```json
{
  "type": "ai_prompt",
  "config": {
    "prompt": "Analyze recent commits and suggest improvements",
    "model": "auto"
  }
}
```

### create_branch
```json
{
  "type": "create_branch",
  "config": {
    "issue_number": 123,
    "branch_prefix": "feature"
  }
}
```

### github_pr
```json
{
  "type": "github_pr",
  "config": {
    "title": "Automated PR from scheduler",
    "body": "This PR was created automatically by the 2DO scheduler",
    "branch": "feature-branch"
  }
}
```

## Use Cases

### 1. Daily Development Workflow
```json
{
  "name": "daily-dev-start",
  "description": "Start daily development routine",
  "schedule": "0 9 * * 1-5",
  "enabled": true,
  "tasks": [
    {
      "type": "github_sync",
      "config": {
        "action": "sync_issues",
        "create_todos": true
      }
    },
    {
      "type": "multitask",
      "config": {
        "filter": "priority:high",
        "max_parallel": 2
      }
    }
  ]
}
```

### 2. End-of-Day Cleanup
```json
{
  "name": "daily-cleanup",
  "description": "End of day project cleanup",
  "schedule": "0 18 * * 1-5",
  "enabled": true,
  "tasks": [
    {
      "type": "custom_command",
      "config": {
        "command": "git add . && git commit -m 'End of day checkpoint' || echo 'Nothing to commit'",
        "working_dir": "."
      }
    },
    {
      "type": "add_todo",
      "config": {
        "content": "Review today's progress and plan tomorrow's tasks",
        "type": "general",
        "priority": "low"
      }
    }
  ]
}
```

### 3. Weekly Project Review
```json
{
  "name": "weekly-review",
  "description": "Comprehensive weekly project review",
  "schedule": "0 10 * * 1",
  "enabled": true,
  "tasks": [
    {
      "type": "ai_prompt",
      "config": {
        "prompt": "Review the past week's commits, issues, and progress. Provide insights and suggestions for the upcoming week.",
        "model": "auto"
      }
    },
    {
      "type": "custom_command",
      "config": {
        "command": "git log --since='1 week ago' --oneline",
        "working_dir": "."
      }
    }
  ]
}
```

## Command Reference

### Scheduler Commands

#### `2do scheduler`
Show scheduler status and current schedules
- `--daemon` - Run in daemon mode
- `--stop` - Stop running daemon

#### `2do schedule list`
List all configured schedules

#### `2do schedule add`
Add a new schedule interactively
- `--name` - Schedule name
- `--schedule` - Cron expression
- `--description` - Schedule description

#### `2do schedule remove <name>`
Remove a schedule by name

#### `2do schedule trigger <name>`
Manually trigger a schedule for testing

## Best Practices

### 1. Start with Manual Triggers
Always test your schedules manually before enabling them:
```bash
2do schedule trigger my-schedule
```

### 2. Use Descriptive Names
Choose clear, descriptive names for your schedules:
- ✅ `daily-github-sync`
- ✅ `weekly-code-review`
- ❌ `schedule1`

### 3. Handle Failures Gracefully
Design schedules that can handle partial failures. The scheduler will continue executing remaining tasks even if one fails.

### 4. Monitor Execution
Check scheduler logs and execution summaries regularly to ensure schedules are working as expected.

### 5. Use Appropriate Timing
- Don't schedule too frequently (respect API rate limits)
- Consider time zones for your scheduling
- Use business hours for development-related tasks

## Troubleshooting

### Schedule Not Running
1. Check if scheduler daemon is running: `2do scheduler`
2. Verify cron expression: Use online cron validators
3. Check schedule is enabled in JSON file
4. Review logs for error messages

### Task Failures
1. Test individual tasks manually: `2do schedule trigger schedule-name`
2. Check API key configuration: `2do setup`
3. Verify working directory and file permissions
4. Review task configuration syntax

### Performance Issues
1. Limit concurrent tasks in multitask operations
2. Use appropriate scheduling intervals
3. Monitor system resources during execution

## Integration with Existing 2DO Features

The scheduler seamlessly integrates with all existing 2DO features:
- **AI Routing**: Automatic model selection for AI tasks
- **GitHub Integration**: Full GitHub API support
- **Todo Management**: Creates and manages todos
- **Multitasking**: Parallel processing capabilities
- **Configuration**: Uses existing config system

This makes the scheduler a powerful automation layer on top of 2DO's existing intelligent development workflow.