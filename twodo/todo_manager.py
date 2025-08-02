"""
Todo Manager - Manages todo lists for codebases and projects
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

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

class TodoManager:
    """Manages todo items and persistence"""
    
    def __init__(self, config_dir=None):
        if config_dir:
            self.todo_dir = Path(config_dir) / "todos"
        else:
            self.todo_dir = Path.home() / ".2do" / "todos"
        self.todo_file = self.todo_dir / "todos.json"
        self.todo_dir.mkdir(parents=True, exist_ok=True)
        self.todos = self._load_todos()
    
    def _load_todos(self) -> List[Dict]:
        """Load todos from file"""
        if self.todo_file.exists():
            with open(self.todo_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_todos(self):
        """Save todos to file"""
        with open(self.todo_file, 'w') as f:
            json.dump(self.todos, f, indent=2, default=str)
    
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
            "result": None
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