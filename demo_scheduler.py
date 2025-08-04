#!/usr/bin/env python3
"""
2DO Scheduler Demo Script

This script demonstrates the core scheduler functionality:
1. Creating schedules programmatically
2. Listing schedules
3. Triggering schedules manually
4. Showing scheduler status
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from twodo.scheduler import Scheduler, ScheduleConfig
from twodo.config import ConfigManager
from rich.console import Console

console = Console()

def demo_scheduler():
    """Demonstrate scheduler functionality"""
    console.print("🚀 2DO Scheduler Demo", style="bold blue")
    console.print()
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"📁 Using temporary directory: {temp_dir}")
        
        # Create config manager
        config_manager = ConfigManager(project_dir=temp_dir, suppress_prompts=True)
        scheduler = Scheduler(config_manager)
        
        console.print("✅ Scheduler initialized")
        console.print()
        
        # Demo 1: Create a simple schedule
        console.print("📋 Demo 1: Creating a simple schedule", style="bold cyan")
        
        simple_schedule = {
            'name': 'demo-simple-todo',
            'description': 'Demo schedule that creates a todo every minute',
            'schedule': '*/1 * * * *',  # Every minute
            'enabled': True,
            'tasks': [
                {
                    'type': 'add_todo',
                    'config': {
                        'content': 'Demo todo created by scheduler',
                        'type': 'general',
                        'priority': 'low'
                    }
                }
            ]
        }
        
        success = scheduler.add_schedule(simple_schedule)
        console.print(f"Schedule creation: {'✅ Success' if success else '❌ Failed'}")
        console.print()
        
        # Demo 2: Create a complex schedule with multiple tasks
        console.print("📋 Demo 2: Creating a complex schedule", style="bold cyan")
        
        complex_schedule = {
            'name': 'demo-complex-workflow',
            'description': 'Demo schedule with multiple task types',
            'schedule': '0 */2 * * *',  # Every 2 hours
            'enabled': True,
            'tasks': [
                {
                    'type': 'custom_command',
                    'config': {
                        'command': 'echo "Starting workflow..." && date',
                        'working_dir': temp_dir
                    }
                },
                {
                    'type': 'add_todo',
                    'config': {
                        'content': 'Complex workflow todo - analyze project status',
                        'type': 'general',
                        'priority': 'medium'
                    }
                },
                {
                    'type': 'ai_prompt',
                    'config': {
                        'prompt': 'This is a demo AI prompt for the scheduler. Please provide a brief response about project automation.',
                        'model': 'auto'
                    }
                }
            ]
        }
        
        success = scheduler.add_schedule(complex_schedule)
        console.print(f"Complex schedule creation: {'✅ Success' if success else '❌ Failed'}")
        console.print()
        
        # Demo 3: List all schedules
        console.print("📋 Demo 3: Listing all schedules", style="bold cyan")
        scheduler.list_schedules()
        console.print()
        
        # Demo 4: Get scheduler status
        console.print("📋 Demo 4: Scheduler status", style="bold cyan")
        status = scheduler.get_status()
        console.print(f"Running: {status['running']}")
        console.print(f"Total schedules: {status['schedule_count']}")
        console.print(f"Enabled schedules: {status['enabled_schedules']}")
        console.print()
        
        # Demo 5: Manually trigger a schedule
        console.print("📋 Demo 5: Manually triggering simple schedule", style="bold cyan")
        success = scheduler.trigger_schedule('demo-simple-todo')
        console.print(f"Manual trigger: {'✅ Success' if success else '❌ Failed'}")
        console.print()
        
        # Demo 6: Test schedule validation
        console.print("📋 Demo 6: Testing schedule validation", style="bold cyan")
        
        invalid_schedule = {
            'name': '',  # Invalid: empty name
            'description': 'Invalid schedule for testing',
            'schedule': 'invalid-cron',  # Invalid: bad cron expression
            'enabled': True,
            'tasks': []  # Invalid: no tasks
        }
        
        schedule_config = ScheduleConfig(invalid_schedule)
        errors = schedule_config.validate()
        
        console.print(f"Validation errors found: {len(errors)}")
        for error in errors:
            console.print(f"  ❌ {error}")
        console.print()
        
        # Demo 7: Test daemon functionality (briefly)
        console.print("📋 Demo 7: Testing daemon start/stop", style="bold cyan")
        
        try:
            console.print("Starting scheduler daemon...")
            scheduler.start()
            console.print("✅ Daemon started successfully")
            
            # Check status while running
            status = scheduler.get_status()
            console.print(f"Daemon running: {status['running']}")
            
            console.print("Stopping scheduler daemon...")
            scheduler.stop()
            console.print("✅ Daemon stopped successfully")
            
        except Exception as e:
            console.print(f"❌ Daemon test failed: {e}")
        
        console.print()
        console.print("🎉 Demo completed successfully!", style="bold green")
        console.print()
        console.print("📖 Next steps:")
        console.print("  • Run '2do schedule list' to see your schedules")
        console.print("  • Run '2do schedule add' to create new schedules")
        console.print("  • Run '2do scheduler --daemon' to start the scheduler")
        console.print("  • Check the SCHEDULER_GUIDE.md for detailed documentation")

if __name__ == '__main__':
    demo_scheduler()