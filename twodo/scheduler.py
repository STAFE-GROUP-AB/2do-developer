"""
2DO Scheduler - Schedule and automate 2DO tasks
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import croniter
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import ConfigManager
from .todo_manager import TodoManager
from .github_integration import GitHubIntegration
from .multitasker import Multitasker
from .ai_router import AIRouter

console = Console()

class ScheduleConfig:
    """Configuration for a scheduled task"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.name = config_dict.get('name', '')
        self.description = config_dict.get('description', '')
        self.schedule = config_dict.get('schedule', '')  # Cron expression or interval
        self.enabled = config_dict.get('enabled', True)
        self.tasks = config_dict.get('tasks', [])
        self.next_run = None
        self.last_run = None
        self.run_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'schedule': self.schedule,
            'enabled': self.enabled,
            'tasks': self.tasks,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count
        }
    
    def validate(self) -> List[str]:
        """Validate the schedule configuration"""
        errors = []
        
        if not self.name:
            errors.append("Schedule name is required")
            
        if not self.schedule:
            errors.append("Schedule expression is required")
        else:
            # Validate cron expression
            try:
                croniter.croniter(self.schedule)
            except (ValueError, croniter.CroniterBadCronError):
                errors.append(f"Invalid schedule expression: {self.schedule}")
                
        if not self.tasks:
            errors.append("At least one task is required")
            
        # Validate task types
        valid_task_types = [
            'github_sync', 'multitask', 'add_todo', 'create_branch', 
            'github_pr', 'custom_command', 'ai_prompt'
        ]
        
        for i, task in enumerate(self.tasks):
            if not isinstance(task, dict):
                errors.append(f"Task {i+1} must be a dictionary")
                continue
                
            task_type = task.get('type')
            if not task_type:
                errors.append(f"Task {i+1} is missing 'type' field")
            elif task_type not in valid_task_types:
                errors.append(f"Task {i+1} has invalid type '{task_type}'. Valid types: {', '.join(valid_task_types)}")
                
        return errors


class TaskExecutor:
    """Executes individual scheduled tasks"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.todo_manager = TodoManager(config_manager.config_dir)
        
        # Initialize GitHub integration only if API key is available
        github_token = None
        try:
            if config_manager.has_api_keys():
                github_token = config_manager.get_api_key("github")
        except Exception:
            pass  # API keys not configured
            
        self.github = GitHubIntegration(github_token) if github_token else None
        self.ai_router = AIRouter(config_manager)
        
    async def execute_task(self, task: Dict[str, Any], schedule_name: str) -> Dict[str, Any]:
        """Execute a single task and return result"""
        task_type = task.get('type')
        task_config = task.get('config', {})
        result = {'type': task_type, 'status': 'success', 'message': '', 'data': {}}
        
        try:
            console.print(f"🔄 Executing {task_type} task for schedule '{schedule_name}'")
            
            if task_type == 'github_sync':
                result.update(await self._execute_github_sync(task_config))
            elif task_type == 'multitask':
                result.update(await self._execute_multitask(task_config))
            elif task_type == 'add_todo':
                result.update(await self._execute_add_todo(task_config))
            elif task_type == 'create_branch':
                result.update(await self._execute_create_branch(task_config))
            elif task_type == 'github_pr':
                result.update(await self._execute_github_pr(task_config))
            elif task_type == 'custom_command':
                result.update(await self._execute_custom_command(task_config))
            elif task_type == 'ai_prompt':
                result.update(await self._execute_ai_prompt(task_config))
            else:
                result.update({
                    'status': 'error',
                    'message': f'Unknown task type: {task_type}'
                })
                
        except Exception as e:
            result.update({
                'status': 'error',
                'message': f'Task execution failed: {str(e)}'
            })
            
        return result
    
    async def _execute_github_sync(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sync GitHub issues and optionally create todos"""
        if not self.github:
            return {
                'status': 'error',
                'message': 'GitHub integration not configured. Please run "2do setup" to configure GitHub API key.'
            }
            
        action = config.get('action', 'sync_issues')
        create_todos = config.get('create_todos', True)
        
        if action == 'sync_issues':
            try:
                # Get GitHub issues
                issues = await asyncio.get_event_loop().run_in_executor(
                    None, self.github.list_issues
                )
                
                synced_count = 0
                if create_todos and issues:
                    for issue in issues:
                        # Create todo from issue
                        title = f"GitHub Issue #{issue['number']}: {issue['title']}"
                        description = issue['body'] or ''
                        todo_id = self.todo_manager.add_todo(
                            title=title,
                            description=description,
                            todo_type='code',
                            priority='medium',
                            content=f"{title}\n\n{description}"
                        )
                        synced_count += 1
                        
                return {
                    'status': 'success',
                    'message': f'Synced {len(issues or [])} issues, created {synced_count} todos',
                    'data': {'issues_count': len(issues or []), 'todos_created': synced_count}
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'GitHub sync failed: {str(e)}'
                }
            
        return {'status': 'error', 'message': f'Unknown sync action: {action}'}
    
    async def _execute_multitask(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multitasking on todos"""
        todo_filter = config.get('filter', '')
        max_parallel = config.get('max_parallel', 3)
        
        # Get todos based on filter
        todos = self.todo_manager.get_todos()
        
        # Apply filters
        if 'priority:high' in todo_filter:
            todos = [t for t in todos if t.priority == 'high']
        elif 'priority:medium' in todo_filter:
            todos = [t for t in todos if t.priority == 'medium']
        elif 'priority:low' in todo_filter:
            todos = [t for t in todos if t.priority == 'low']
            
        # Filter for pending todos
        pending_todos = [t for t in todos if t.status == 'pending']
        
        if not pending_todos:
            return {
                'status': 'success',
                'message': 'No pending todos to process',
                'data': {'processed_count': 0}
            }
        
        # Execute multitasking
        multitasker = Multitasker(self.config_manager, max_workers=max_parallel)
        results = await multitasker.process_todos_async(pending_todos[:max_parallel])
        
        return {
            'status': 'success',
            'message': f'Processed {len(results)} todos',
            'data': {'processed_count': len(results), 'results': results}
        }
    
    async def _execute_add_todo(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new todo"""
        content = config.get('content', '')
        todo_type = config.get('type', 'general')
        priority = config.get('priority', 'medium')
        title = config.get('title', content[:50] + '...' if len(content) > 50 else content)
        description = config.get('description', content)
        
        if not content:
            return {'status': 'error', 'message': 'Todo content is required'}
            
        try:
            todo_id = self.todo_manager.add_todo(
                title=title,
                description=description,
                todo_type=todo_type,
                priority=priority,
                content=content
            )
            
            return {
                'status': 'success',
                'message': f'Added todo: {todo_id}',
                'data': {'todo_id': todo_id}
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to add todo: {str(e)}'}
    
    async def _execute_create_branch(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a git branch for issue work"""
        if not self.github:
            return {
                'status': 'error',
                'message': 'GitHub integration not configured. Please run "2do setup" to configure GitHub API key.'
            }
            
        issue_number = config.get('issue_number')
        branch_prefix = config.get('branch_prefix', 'issue')
        
        if issue_number:
            try:
                # Create branch for specific issue
                branch_name = f"{branch_prefix}-{issue_number}"
                success = await asyncio.get_event_loop().run_in_executor(
                    None, self.github.create_branch_for_issue, issue_number
                )
                if success:
                    return {
                        'status': 'success',
                        'message': f'Created branch: {branch_name}',
                        'data': {'branch_name': branch_name}
                    }
                else:
                    return {'status': 'error', 'message': f'Failed to create branch for issue {issue_number}'}
            except Exception as e:
                return {'status': 'error', 'message': f'Branch creation failed: {str(e)}'}
        
        return {'status': 'error', 'message': 'Issue number is required'}
    
    async def _execute_github_pr(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a GitHub pull request"""
        if not self.github:
            return {
                'status': 'error',
                'message': 'GitHub integration not configured. Please run "2do setup" to configure GitHub API key.'
            }
            
        title = config.get('title', '')
        body = config.get('body', '')
        branch = config.get('branch', '')
        
        if not all([title, branch]):
            return {'status': 'error', 'message': 'Title and branch are required for PR creation'}
            
        try:
            pr_url = await asyncio.get_event_loop().run_in_executor(
                None, self.github.create_pull_request, title, body, branch
            )
            
            if pr_url:
                return {
                    'status': 'success',
                    'message': f'Created pull request: {pr_url}',
                    'data': {'pr_url': pr_url}
                }
            else:
                return {'status': 'error', 'message': 'Failed to create pull request'}
        except Exception as e:
            return {'status': 'error', 'message': f'PR creation failed: {str(e)}'}
    
    async def _execute_custom_command(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a custom shell command"""
        command = config.get('command', '')
        working_dir = config.get('working_dir', os.getcwd())
        
        if not command:
            return {'status': 'error', 'message': 'Command is required'}
            
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'status': 'success' if result.returncode == 0 else 'error',
                'message': f'Command exit code: {result.returncode}',
                'data': {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Command execution failed: {str(e)}'}
    
    async def _execute_ai_prompt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI prompt"""
        prompt = config.get('prompt', '')
        model = config.get('model', 'auto')
        
        if not prompt:
            return {'status': 'error', 'message': 'Prompt is required'}
            
        try:
            # Route the prompt to the best AI model
            response = await self.ai_router.route_and_process(prompt)
            
            return {
                'status': 'success',
                'message': 'AI prompt executed successfully',
                'data': {'response': response, 'model_used': model}
            }
        except Exception as e:
            return {'status': 'error', 'message': f'AI prompt failed: {str(e)}'}


class Scheduler:
    """Main scheduler class for managing scheduled tasks"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.task_executor = TaskExecutor(config_manager)
        self.scheduler = BackgroundScheduler()
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.schedules_dir = self._get_schedules_directory()
        self.running = False
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _get_schedules_directory(self) -> Path:
        """Get the schedules directory path"""
        if self.config_manager.is_local_project:
            schedules_dir = self.config_manager.config_dir / "schedules"
        else:
            schedules_dir = self.config_manager.config_dir / "schedules"
        
        schedules_dir.mkdir(parents=True, exist_ok=True)
        return schedules_dir
    
    def load_schedules(self) -> None:
        """Load all schedule configurations from JSON files"""
        console.print("📁 Loading schedules...")
        
        schedule_files = list(self.schedules_dir.glob("*.json"))
        if not schedule_files:
            console.print("📄 No schedule files found")
            return
            
        for schedule_file in schedule_files:
            try:
                with open(schedule_file, 'r') as f:
                    config_data = json.load(f)
                    
                schedule_config = ScheduleConfig(config_data)
                errors = schedule_config.validate()
                
                if errors:
                    console.print(f"❌ Invalid schedule in {schedule_file.name}: {', '.join(errors)}")
                    continue
                    
                self.schedules[schedule_config.name] = schedule_config
                console.print(f"✅ Loaded schedule: {schedule_config.name}")
                
            except Exception as e:
                console.print(f"❌ Error loading {schedule_file.name}: {str(e)}")
    
    def save_schedule(self, schedule_config: ScheduleConfig) -> bool:
        """Save a schedule configuration to a JSON file"""
        try:
            filename = f"{schedule_config.name.replace(' ', '_').lower()}.json"
            filepath = self.schedules_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(schedule_config.to_dict(), f, indent=2)
                
            console.print(f"💾 Saved schedule: {schedule_config.name}")
            return True
            
        except Exception as e:
            console.print(f"❌ Error saving schedule: {str(e)}")
            return False
    
    def add_schedule(self, config_data: Dict[str, Any]) -> bool:
        """Add a new schedule"""
        schedule_config = ScheduleConfig(config_data)
        errors = schedule_config.validate()
        
        if errors:
            console.print(f"❌ Invalid schedule configuration: {', '.join(errors)}")
            return False
            
        self.schedules[schedule_config.name] = schedule_config
        
        if self.save_schedule(schedule_config):
            if self.running:
                self._schedule_job(schedule_config)
            return True
            
        return False
    
    def remove_schedule(self, name: str) -> bool:
        """Remove a schedule"""
        if name not in self.schedules:
            console.print(f"❌ Schedule '{name}' not found")
            return False
            
        # Remove from scheduler if running
        if self.running:
            try:
                self.scheduler.remove_job(name)
            except Exception:
                pass  # Job might not exist
                
        # Remove from memory
        del self.schedules[name]
        
        # Remove file
        try:
            filename = f"{name.replace(' ', '_').lower()}.json"
            filepath = self.schedules_dir / filename
            if filepath.exists():
                filepath.unlink()
                
            console.print(f"🗑️ Removed schedule: {name}")
            return True
            
        except Exception as e:
            console.print(f"❌ Error removing schedule file: {str(e)}")
            return False
    
    def list_schedules(self) -> None:
        """Display all schedules in a table"""
        if not self.schedules:
            console.print("📋 No schedules configured")
            return
            
        table = Table(title="📅 Scheduled Tasks")
        table.add_column("Name", style="cyan")
        table.add_column("Schedule", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Next Run", style="blue")
        table.add_column("Last Run", style="magenta")
        table.add_column("Tasks", style="white")
        
        for schedule in self.schedules.values():
            status = "✅ Enabled" if schedule.enabled else "❌ Disabled"
            next_run = schedule.next_run.strftime("%Y-%m-%d %H:%M") if schedule.next_run else "Not scheduled"
            last_run = schedule.last_run.strftime("%Y-%m-%d %H:%M") if schedule.last_run else "Never"
            task_count = len(schedule.tasks)
            
            table.add_row(
                schedule.name,
                schedule.schedule,
                status,
                next_run,
                last_run,
                f"{task_count} task{'s' if task_count != 1 else ''}"
            )
            
        console.print(table)
    
    def _schedule_job(self, schedule_config: ScheduleConfig) -> None:
        """Schedule a job with the APScheduler"""
        if not schedule_config.enabled:
            return
            
        try:
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(schedule_config.name)
            except Exception:
                pass
                
            # Create cron trigger
            trigger = CronTrigger.from_crontab(schedule_config.schedule)
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_schedule,
                trigger=trigger,
                id=schedule_config.name,
                args=[schedule_config.name],
                max_instances=1,
                replace_existing=True
            )
            
            # Update next run time
            job = self.scheduler.get_job(schedule_config.name)
            if job and hasattr(job, 'next_run_time'):
                schedule_config.next_run = job.next_run_time
                
        except Exception as e:
            console.print(f"❌ Error scheduling job '{schedule_config.name}': {str(e)}")
    
    def _execute_schedule(self, schedule_name: str) -> None:
        """Execute a scheduled task (called by APScheduler)"""
        if schedule_name not in self.schedules:
            return
            
        schedule_config = self.schedules[schedule_name]
        console.print(f"\n🚀 Executing scheduled task: {schedule_name}")
        console.print(Panel(f"📋 {schedule_config.description}", title="Schedule Description"))
        
        # Update run statistics
        schedule_config.last_run = datetime.now()
        schedule_config.run_count += 1
        
        # Execute tasks asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(self._execute_schedule_async(schedule_config))
            
            # Display results
            self._display_execution_results(schedule_name, results)
            
            # Update next run time
            job = self.scheduler.get_job(schedule_name)
            if job and hasattr(job, 'next_run_time'):
                schedule_config.next_run = job.next_run_time
                
        except Exception as e:
            console.print(f"❌ Error executing schedule '{schedule_name}': {str(e)}")
        finally:
            loop.close()
    
    async def _execute_schedule_async(self, schedule_config: ScheduleConfig) -> List[Dict[str, Any]]:
        """Execute all tasks in a schedule asynchronously"""
        results = []
        
        for i, task in enumerate(schedule_config.tasks):
            console.print(f"⏳ Executing task {i+1}/{len(schedule_config.tasks)}: {task.get('type', 'unknown')}")
            
            result = await self.task_executor.execute_task(task, schedule_config.name)
            results.append(result)
            
            # Display task result
            if result['status'] == 'success':
                console.print(f"✅ Task {i+1} completed: {result['message']}")
            else:
                console.print(f"❌ Task {i+1} failed: {result['message']}")
                
        return results
    
    def _display_execution_results(self, schedule_name: str, results: List[Dict[str, Any]]) -> None:
        """Display execution results in a formatted way"""
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        if failed == 0:
            status_message = f"✅ All {len(results)} tasks completed successfully"
            status_style = "green"
        else:
            status_message = f"⚠️ {successful} succeeded, {failed} failed"
            status_style = "yellow"
            
        console.print(Panel(
            f"📊 Schedule: {schedule_name}\n"
            f"🎯 Status: {status_message}\n"
            f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="Execution Summary",
            border_style=status_style
        ))
    
    def start(self) -> None:
        """Start the scheduler"""
        if self.running:
            console.print("⚠️ Scheduler is already running")
            return
            
        console.print("🚀 Starting scheduler...")
        
        # Load schedules
        self.load_schedules()
        
        # Schedule all enabled jobs
        for schedule_config in self.schedules.values():
            self._schedule_job(schedule_config)
            
        # Start the scheduler
        self.scheduler.start()
        self.running = True
        
        console.print(f"✅ Scheduler started with {len(self.schedules)} schedule(s)")
        
        # Display next executions
        if self.schedules:
            console.print("\n📅 Next scheduled executions:")
            for schedule in self.schedules.values():
                if schedule.enabled and schedule.next_run:
                    console.print(f"  • {schedule.name}: {schedule.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if not self.running:
            console.print("⚠️ Scheduler is not running")
            return
            
        console.print("🛑 Stopping scheduler...")
        self.scheduler.shutdown(wait=False)
        self.running = False
        console.print("✅ Scheduler stopped")
    
    def trigger_schedule(self, name: str) -> bool:
        """Manually trigger a schedule"""
        if name not in self.schedules:
            console.print(f"❌ Schedule '{name}' not found")
            return False
            
        console.print(f"🔧 Manually triggering schedule: {name}")
        self._execute_schedule(name)
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status information"""
        return {
            'running': self.running,
            'schedule_count': len(self.schedules),
            'enabled_schedules': sum(1 for s in self.schedules.values() if s.enabled),
            'next_executions': [
                {
                    'name': s.name,
                    'next_run': s.next_run.isoformat() if s.next_run else None
                }
                for s in self.schedules.values() 
                if s.enabled and s.next_run
            ]
        }