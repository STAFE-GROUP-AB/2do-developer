"""
Todo Manager - Manages todo lists for codebases and projects
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from .permission_manager import PermissionManager

@dataclass
class Todo:
    """Represents a single todo item"""
    id: str
    title: str
    description: str
    todo_type: str  # code, text, image, general
    priority: str   # low, medium, high, critical
    status: str     # pending, in_progress, completed, failed
    content: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    assigned_model: Optional[str] = None
    result: Optional[str] = None
    parent_id: Optional[str] = None  # For sub-tasks
    sub_task_ids: Optional[List[str]] = None   # For parent tasks

    def __post_init__(self):
        if self.sub_task_ids is None:
            self.sub_task_ids = []

class TodoManager:
    """Manages todo items and persistence"""
    
    def __init__(self, config_dir=None):
        if config_dir:
            self.todo_dir = Path(config_dir) / "todos"
        else:
            self.todo_dir = Path.home() / ".2do" / "todos"
        self.todo_file = self.todo_dir / "todos.json"
        
        # Create directory with enhanced permission handling
        preferred_paths = [self.todo_dir]
        if config_dir:
            # Add additional fallback paths for local projects
            preferred_paths.extend([
                Path(config_dir).parent / ".2do_fallback" / "todos",
                Path.home() / ".2do" / "todos"
            ])
        else:
            preferred_paths.extend([
                Path.home() / ".2do_fallback" / "todos"
            ])
        
        # Use PermissionManager to get a secure directory
        secure_dir = PermissionManager.get_secure_directory(preferred_paths, "2do_todos")
        
        # Update paths if we had to use a fallback
        if secure_dir != self.todo_dir:
            self.todo_dir = secure_dir
            self.todo_file = self.todo_dir / "todos.json"
        
        # Ensure proper permissions
        PermissionManager.ensure_directory_permissions(self.todo_dir)
        
        self.todos = self._load_todos()
    
    def _load_todos(self) -> List[Dict]:
        """Load todos from file"""
        if self.todo_file.exists():
            with open(self.todo_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_todos(self):
        """Save todos to file with enhanced permission handling"""
        try:
            # Ensure directory and file permissions
            PermissionManager.ensure_directory_permissions(self.todo_file.parent)
            
            with open(self.todo_file, 'w') as f:
                json.dump(self.todos, f, indent=2, default=str)
            
            # Set secure file permissions
            PermissionManager.ensure_file_permissions(self.todo_file)
            
        except (OSError, PermissionError) as e:
            console = Console()
            console.print(f"❌ Cannot save todos to {self.todo_file}: {e}")
            
            # Try to save to a backup location
            backup_file = self.todo_file.parent / f"todos_backup_{int(datetime.now().timestamp())}.json"
            try:
                # Ensure backup directory permissions
                PermissionManager.ensure_directory_permissions(backup_file.parent)
                
                with open(backup_file, 'w') as f:
                    json.dump(self.todos, f, indent=2, default=str)
                
                PermissionManager.ensure_file_permissions(backup_file)
                console.print(f"💾 Saved todos to backup file: {backup_file}")
                
            except Exception as backup_error:
                console.print(f"❌ Cannot save backup either: {backup_error}")
                console.print("⚠️ Todo changes are not persisted - they will be lost when the session ends")
                raise Exception(f"Cannot save todos: {e}") from e
    
    def add_todo(self, title: str, description: str, todo_type: str, priority: str, content: Optional[str] = None) -> str:
        """Add a new todo item"""
        todo_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        todo = {
            "id": todo_id,
            "title": title,
            "description": description,
            "todo_type": todo_type,
            "priority": priority,
            "status": "pending",
            "content": content,
            "created_at": now,
            "updated_at": now,
            "assigned_model": None,
            "result": None,
            "parent_id": None,
            "sub_task_ids": []
        }
        
        self.todos.append(todo)
        self._save_todos()
        return todo_id
    
    def get_todos(self) -> List[Dict]:
        """Get all todos"""
        return self.todos
    
    def get_pending_todos(self) -> List[Dict]:
        """Get only pending todos"""
        return [todo for todo in self.todos if todo["status"] == "pending"]
    
    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """Get a specific todo by ID"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                return todo
        return None
    
    def update_todo_status(self, todo_id: str, status: str, result: Optional[str] = None, assigned_model: Optional[str] = None):
        """Update todo status and result"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["status"] = status
                todo["updated_at"] = datetime.now().isoformat()
                if result is not None:
                    todo["result"] = result
                if assigned_model is not None:
                    todo["assigned_model"] = assigned_model
                break
        self._save_todos()
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo by ID"""
        original_length = len(self.todos)
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        
        if len(self.todos) < original_length:
            self._save_todos()
            return True
        return False
    
    def get_todos_by_type(self, todo_type: str) -> List[Dict]:
        """Get todos by type"""
        return [todo for todo in self.todos if todo["todo_type"] == todo_type]
    
    def get_todos_by_priority(self, priority: str) -> List[Dict]:
        """Get todos by priority"""
        return [todo for todo in self.todos if todo["priority"] == priority]
    
    def get_completion_stats(self) -> Dict[str, int]:
        """Get completion statistics"""
        stats = {
            "total": len(self.todos),
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for todo in self.todos:
            status = todo["status"]
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def create_todo_from_codebase(self, repo_path: str) -> List[str]:
        """Create todos from codebase analysis"""
        # This would analyze a codebase and create relevant todos
        # For now, return some example todos
        repo_path = Path(repo_path)
        todo_ids = []
        
        if repo_path.exists():
            # Add todo for README update
            todo_ids.append(self.add_todo(
                "Update README.md",
                f"Review and update README for {repo_path.name}",
                "text",
                "medium",
                f"Repository path: {repo_path}"
            ))
            
            # Add todo for code review
            todo_ids.append(self.add_todo(
                "Code Review",
                f"Perform comprehensive code review of {repo_path.name}",
                "code",
                "high",
                f"Repository path: {repo_path}"
            ))
            
            # Add todo for test coverage
            todo_ids.append(self.add_todo(
                "Test Coverage Analysis",
                f"Analyze and improve test coverage for {repo_path.name}",
                "code",
                "medium",
                f"Repository path: {repo_path}"
            ))
        
        return todo_ids
    
    def is_todo_too_large(self, todo: Dict) -> bool:
        """Analyze if a todo is too large and should be broken down into sub-tasks"""
        
        # Calculate total content length
        total_content_length = len(todo.get("title", "") + todo.get("description", "") + (todo.get("content") or ""))
        
        # Check for complexity indicators
        content_text = (todo.get("title", "") + " " + todo.get("description", "") + " " + (todo.get("content") or "")).lower()
        
        complexity_keywords = [
            "comprehensive", "complete", "full", "entire", "all", "multiple", "various",
            "implement", "create", "build", "develop", "design", "architect",
            "refactor", "migrate", "upgrade", "overhaul", "rewrite",
            "system", "application", "platform", "framework", "infrastructure"
        ]
        
        complexity_score = sum(1 for keyword in complexity_keywords if keyword in content_text)
        
        # Large todo criteria:
        # 1. Content length > 500 characters
        # 2. High complexity score (3+ complexity keywords)
        # 3. Multiple distinct actions indicated
        multiple_actions = len([word for word in content_text.split() if word in ["and", "also", "then", "plus", "additionally", "furthermore"]])
        
        is_large = (
            total_content_length > 500 or
            complexity_score >= 3 or
            multiple_actions >= 2
        )
        
        return is_large
    
    def create_sub_tasks_from_todo(self, parent_todo_id: str, ai_router=None) -> List[str]:
        """Create sub-tasks from a large todo using AI analysis"""
        parent_todo = self.get_todo_by_id(parent_todo_id)
        if not parent_todo:
            return []
        
        if not self.is_todo_too_large(parent_todo):
            return []
        
        sub_task_ids = []
        
        if ai_router:
            # Use AI to generate sub-tasks
            sub_task_ids = self._generate_subtasks_with_ai(parent_todo, ai_router)
        else:
            # Fallback to simple rule-based splitting
            sub_task_ids = self._generate_subtasks_simple(parent_todo)
        
        # Update parent todo with sub-task IDs
        parent_todo["sub_task_ids"] = sub_task_ids
        parent_todo["updated_at"] = datetime.now().isoformat()
        self._save_todos()
        
        return sub_task_ids
    
    def _generate_subtasks_with_ai(self, parent_todo: Dict, ai_router) -> List[str]:
        """Generate sub-tasks using AI analysis with human colleague approach"""
        
        prompt = f"""
        As a helpful development colleague, analyze this task and break it down into 3-5 smaller, actionable sub-tasks.
        Think like a senior developer helping a teammate organize their work.
        
        Main Task: {parent_todo['title']}
        Description: {parent_todo['description']}
        Type: {parent_todo['todo_type']}
        Priority: {parent_todo['priority']}
        Additional Context: {parent_todo.get('content', 'No additional context')}
        
        Please create sub-tasks that:
        1. Are specific and actionable (someone could start working immediately)
        2. Follow a logical order (planning → implementation → testing → documentation)
        3. Are sized appropriately (can be completed in 1-4 hours each)
        4. Cover all aspects of the main task
        5. Use encouraging, colleague-like language
        
        Return ONLY a JSON array of sub-tasks in this exact format:
        [
            {{"title": "Plan and design the architecture", "description": "Start by sketching out the overall approach"}},
            {{"title": "Implement core functionality", "description": "Build the main features step by step"}},
            {{"title": "Add comprehensive testing", "description": "Ensure everything works reliably"}},
            {{"title": "Document and polish", "description": "Add docs and final touches"}}
        ]
        """
        
        try:
            # Use the AI router to get a response
            import asyncio
            import json
            
            ai_response = asyncio.run(ai_router.route_and_process(prompt))
            
            # Try to parse JSON from the response
            # Look for JSON array in the response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                sub_tasks_data = json.loads(json_str)
                
                sub_task_ids = []
                for i, sub_task in enumerate(sub_tasks_data, 1):
                    # Create each sub-task with the parent's type and adjusted priority
                    sub_priority = "medium" if parent_todo['priority'] in ["high", "critical"] else "low"
                    
                    sub_task_id = self.add_todo(
                        title=f"{i}. {sub_task['title']}",
                        description=sub_task['description'],
                        todo_type=parent_todo['todo_type'],
                        priority=sub_priority,
                        content=None,
                        parent_id=parent_todo['id']
                    )
                    sub_task_ids.append(sub_task_id)
                
                return sub_task_ids
                
        except Exception as e:
            console = Console()
            console.print(f"🤔 AI sub-task generation had an issue: {e}")
            console.print("💡 Let me try a simpler approach...")
        
        # Fallback to simple rule-based splitting
        return self._generate_subtasks_simple(parent_todo)
    
    def _generate_subtasks_simple(self, parent_todo: Dict) -> List[str]:
        """Generate sub-tasks using simple rule-based approach"""
        sub_task_ids = []
        
        # Create generic sub-tasks based on todo type
        if parent_todo['todo_type'] == 'code':
            subtasks = [
                ("Plan & Design", "Plan the implementation approach and design"),
                ("Core Implementation", "Implement the main functionality"),
                ("Testing", "Write and run tests for the implementation"),
                ("Documentation", "Document the implementation and usage")
            ]
        elif parent_todo['todo_type'] == 'text':
            subtasks = [
                ("Research & Planning", "Research and plan the content structure"),
                ("Draft Creation", "Create initial draft of the content"),
                ("Review & Edit", "Review and edit the content"),
                ("Final Polish", "Final review and formatting")
            ]
        else:
            # Generic subtasks
            subtasks = [
                ("Planning Phase", "Plan and analyze the requirements"),
                ("Implementation Phase", "Execute the main work"),
                ("Review Phase", "Review and validate the results")
            ]
        
        for title, description in subtasks:
            sub_task_id = self.add_todo(
                title=f"{parent_todo['title']} - {title}",
                description=description,
                todo_type=parent_todo['todo_type'],
                priority=parent_todo['priority'],
                content=f"Sub-task of: {parent_todo['title']}"
            )
            
            # Set parent relationship
            sub_task = self.get_todo_by_id(sub_task_id)
            if sub_task:
                sub_task["parent_id"] = parent_todo["id"]
                sub_task_ids.append(sub_task_id)
        
        self._save_todos()
        return sub_task_ids
    
    def get_sub_tasks(self, parent_todo_id: str) -> List[Dict]:
        """Get all sub-tasks for a parent todo"""
        return [todo for todo in self.todos if todo.get("parent_id") == parent_todo_id]
    
    def get_parent_todo(self, sub_task_id: str) -> Optional[Dict]:
        """Get the parent todo for a sub-task"""
        sub_task = self.get_todo_by_id(sub_task_id)
        if sub_task and sub_task.get("parent_id"):
            return self.get_todo_by_id(sub_task["parent_id"])
        return None