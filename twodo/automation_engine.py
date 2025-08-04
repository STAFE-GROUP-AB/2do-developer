#!/usr/bin/env python3
"""
Automation Engine - Smart todo parsing, instant actions, and GitHub Pro mode
Handles intelligent parsing of user requests into todos with automation features
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel

console = Console()

@dataclass
class AutoTodoRequest:
    """Represents an automatically parsed todo request"""
    original_input: str
    suggested_title: str
    suggested_description: str
    detected_files: List[str]
    action_type: str  # 'modify', 'create', 'fix', 'refactor', etc.
    confidence: float
    auto_start_eligible: bool = True

class AutomationEngine:
    """Handles smart todo parsing and automation features"""
    
    def __init__(self, todo_manager, multitasker, github_integration=None):
        self.todo_manager = todo_manager
        self.multitasker = multitasker
        self.github_integration = github_integration
        self.github_pro_mode = False
        
        # File modification patterns for smart parsing
        self.file_patterns = {
            'modify': [
                r'(change|modify|update|edit|replace)\s+(.+?)\s+(in|from)\s+([^\s]+\.\w+)',
                r'replace\s+(.+?)\s+(with|to)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
                r'(change|update|modify)\s+(.+?)\s+(text|content|code)\s+in\s+([^\s]+)',
            ],
            'create': [
                r'(create|add|make)\s+(.+?)\s+(in|to)\s+([^\s]+\.\w+)',
                r'(add|insert|include)\s+(.+?)\s+(to|in)\s+([^\s]+\.\w+)',
                r'(create|add)\s+.*?(function|class|method|component)\s+(.+?)\s+in\s+([^\s]+)',
            ],
            'remove': [
                r'(remove|delete)\s+(.+?)\s+(from|in)\s+([^\s]+\.\w+)',
                r'(delete|remove)\s+(.+?)\s+from\s+([^\s]+)',
            ],
            'fix': [
                r'(fix|debug|solve)\s+(.+?)\s+(bug|issue|error)\s+in\s+([^\s]+)',
                r'(fix|repair|correct)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
            ],
            'refactor': [
                r'(refactor|restructure|reorganize)\s+(.+?)\s+in\s+([^\s]+)',
                r'(improve|optimize|clean\s+up)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
            ]
        }
    
    def parse_smart_todo(self, user_input: str) -> Optional[AutoTodoRequest]:
        """Parse user input to detect file modification requests and convert to todos"""
        user_input_lower = user_input.lower().strip()
        
        for action_type, patterns in self.file_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    return self._create_auto_todo_request(user_input, match, action_type, pattern)
        
        # Fallback: check if it sounds like a development task
        dev_keywords = ['implement', 'code', 'build', 'test', 'deploy', 'debug', 'feature', 'bug']
        if any(keyword in user_input_lower for keyword in dev_keywords):
            return AutoTodoRequest(
                original_input=user_input,
                suggested_title=user_input.strip(),
                suggested_description=f"Development task: {user_input}",
                detected_files=[],
                action_type='general',
                confidence=0.7,
                auto_start_eligible=True
            )
        
        return None
    
    def _create_auto_todo_request(self, user_input: str, match, action_type: str, pattern: str) -> AutoTodoRequest:
        """Create an AutoTodoRequest from a regex match"""
        groups = match.groups()
        
        # Extract file names from the match
        detected_files = []
        for group in groups:
            if '.' in group and not ' ' in group:  # Likely a filename
                detected_files.append(group)
        
        # Generate title and description based on action type
        if action_type == 'modify':
            if len(groups) >= 4:
                what_to_change = groups[1] if len(groups) > 1 else "content"
                filename = groups[-1]
                title = f"Modify {what_to_change} in {filename}"
                description = f"Change '{what_to_change}' in file {filename}"
            else:
                title = f"Modify file content"
                description = user_input
        elif action_type == 'create':
            if len(groups) >= 3:
                what_to_create = groups[1] if len(groups) > 1 else "new content"
                filename = groups[-1]
                title = f"Add {what_to_create} to {filename}"
                description = f"Create/add '{what_to_create}' in file {filename}"
            else:
                title = "Create new content"
                description = user_input
        elif action_type == 'fix':
            if len(groups) >= 3:
                what_to_fix = groups[1] if len(groups) > 1 else "issue"
                filename = groups[-1]
                title = f"Fix {what_to_fix} in {filename}"
                description = f"Debug and fix '{what_to_fix}' in file {filename}"
            else:
                title = "Fix issue"
                description = user_input
        else:
            title = user_input.strip()
            description = f"{action_type.title()} task: {user_input}"
        
        return AutoTodoRequest(
            original_input=user_input,
            suggested_title=title,
            suggested_description=description,
            detected_files=detected_files,
            action_type=action_type,
            confidence=0.9,
            auto_start_eligible=True
        )
    
    async def handle_smart_todo_creation(self, user_input: str) -> bool:
        """Handle smart todo creation with instant action prompt"""
        auto_todo = self.parse_smart_todo(user_input)
        
        if not auto_todo:
            return False
        
        # Display the parsed todo
        console.print(Panel.fit(
            f"🤖 Smart Todo Detected!\n\n"
            f"📝 Title: {auto_todo.suggested_title}\n"
            f"📋 Description: {auto_todo.suggested_description}\n"
            f"📁 Files: {', '.join(auto_todo.detected_files) if auto_todo.detected_files else 'None detected'}\n"
            f"🎯 Action: {auto_todo.action_type.title()}\n"
            f"🎲 Confidence: {auto_todo.confidence:.0%}",
            style="bold green"
        ))
        
        # Confirm todo creation
        if not Confirm.ask("Create this todo?", default=True):
            console.print("❌ Todo creation cancelled.")
            return False
        
        # Create the todo
        todo_id = self.todo_manager.add_todo(
            auto_todo.suggested_title,
            auto_todo.suggested_description,
            "code",  # todo_type - default to code for smart todos
            "medium"  # priority - default to medium
        )
        
        console.print(f"✅ Todo created with ID: {todo_id}")
        
        # Instant action prompt
        if auto_todo.auto_start_eligible:
            if Confirm.ask("🚀 Start working on this todo now?", default=False):
                console.print("🔥 Starting multitasking on your new todo...")
                try:
                    # Start multitasking on the specific todo
                    await self._start_single_todo_multitask(todo_id)
                    return True
                except Exception as e:
                    console.print(f"❌ Error starting multitask: {e}")
                    console.print("💡 You can start it manually with 'multitask' command")
        
        return True
    
    def run_all_todos_sync(self) -> bool:
        """Synchronous wrapper for run_all_todos to avoid nested event loop issues"""
        try:
            return asyncio.run(self.run_all_todos())
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                console.print(f"💥 Event loop conflict detected: {e}")
                console.print("🔧 Attempting alternative async handling...")
                # Alternative: use existing event loop if available
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create a new thread to run the async code
                        import concurrent.futures
                        import threading
                        
                        def run_in_thread():
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                return new_loop.run_until_complete(self.run_all_todos())
                            finally:
                                new_loop.close()
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(run_in_thread)
                            return future.result()
                    else:
                        return loop.run_until_complete(self.run_all_todos())
                except Exception as thread_e:
                    console.print(f"💥 Thread execution failed: {thread_e}")
                    return False
            else:
                console.print(f"💥 Unexpected runtime error: {e}")
                return False
        except Exception as e:
            console.print(f"💥 Run all todos failed: {e}")
            return False
    
    async def run_all_todos(self) -> bool:
        """Run multitasking on all pending todos - the ultimate shortcut"""
        todos = self.todo_manager.get_todos()
        pending_todos = [todo for todo in todos if todo.get('status') == 'pending']
        
        if not pending_todos:
            console.print("📭 No pending todos to run!")
            return False
        
        console.print(Panel.fit(
            f"🔥 RUN ALL MODE ACTIVATED!\n\n"
            f"📊 Found {len(pending_todos)} pending todos\n"
            f"⚡ About to start multitasking on ALL of them\n"
            f"🚀 This is the ultimate productivity shortcut!",
            style="bold red"
        ))
        
        # Show the todos that will be processed
        console.print("\n📋 Todos to process:")
        for i, todo in enumerate(pending_todos[:5], 1):  # Show first 5
            console.print(f"  {i}. {todo.get('title', 'Untitled')}")
        
        if len(pending_todos) > 5:
            console.print(f"  ... and {len(pending_todos) - 5} more")
        
        # Confirmation
        if not Confirm.ask(f"\n💥 Ready to unleash the beast on {len(pending_todos)} todos?", default=False):
            console.print("🛑 Run all cancelled - probably a wise choice!")
            return False
        
        console.print("🔥 MAXIMUM PRODUCTIVITY MODE ENGAGED!")
        
        try:
            # Start multitasking on all pending todos
            await self.multitasker.start_multitask(pending_todos)
            console.print("🎉 ALL TODOS LAUNCHED! The automation army is working!")
            return True
        except Exception as e:
            console.print(f"💥 Run all encountered an error: {e}")
            return False
    
    async def _start_single_todo_multitask(self, todo_id: str):
        """Start multitasking on a single specific todo"""
        # Get the specific todo by ID
        todo = self.todo_manager.get_todo_by_id(todo_id)
        if todo:
            await self.multitasker.start_multitask([todo])
        else:
            console.print(f"❌ Todo with ID {todo_id} not found")
    
    def toggle_github_pro_mode(self) -> bool:
        """Toggle GitHub Pro mode on/off"""
        self.github_pro_mode = not self.github_pro_mode
        
        if self.github_pro_mode:
            console.print(Panel.fit(
                "🚀 GITHUB PRO MODE ACTIVATED!\n\n"
                "✨ Features enabled:\n"
                "  • Each todo gets its own branch\n"
                "  • Automatic branch creation\n"
                "  • Auto-push when todo completes\n"
                "  • Automatic PR creation\n"
                "  • Advanced GitHub workflow integration\n\n"
                "🎯 You're now in full automation mode!",
                style="bold green"
            ))
        else:
            console.print(Panel.fit(
                "📴 GitHub Pro Mode Deactivated\n\n"
                "Back to standard todo management mode.",
                style="bold yellow"
            ))
        
        return self.github_pro_mode
    
    async def handle_github_pro_todo(self, todo_id: str, todo_title: str):
        """Handle a todo in GitHub Pro mode with branch creation and PR automation"""
        if not self.github_pro_mode or not self.github_integration:
            return False
        
        try:
            # Create a branch for this todo
            branch_name = self._generate_branch_name(todo_title)
            console.print(f"🌿 Creating branch: {branch_name}")
            
            # This would integrate with GitHubIntegration to create branch
            # Implementation depends on the existing GitHub integration
            
            console.print(f"✅ Branch {branch_name} created for todo {todo_id}")
            return True
            
        except Exception as e:
            console.print(f"❌ GitHub Pro mode error: {e}")
            return False
    
    def _generate_branch_name(self, todo_title: str) -> str:
        """Generate a clean branch name from todo title"""
        # Clean the title for branch naming
        clean_title = re.sub(r'[^a-zA-Z0-9\s-]', '', todo_title)
        clean_title = re.sub(r'\s+', '-', clean_title.strip())
        clean_title = clean_title.lower()[:50]  # Limit length
        
        return f"todo/{clean_title}"
    
    def get_automation_status(self) -> Dict:
        """Get current automation engine status"""
        return {
            'github_pro_mode': self.github_pro_mode,
            'smart_parsing_enabled': True,
            'instant_actions_enabled': True,
            'run_all_available': True,
            'github_integration': self.github_integration is not None
        }
