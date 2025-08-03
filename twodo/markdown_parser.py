"""
Markdown Parser - Extracts tasks and todos from markdown files
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from rich.console import Console

console = Console()

class MarkdownTaskParser:
    """Parses markdown files to extract tasks and todos"""
    
    def __init__(self):
        # Patterns for different task formats
        self.task_patterns = [
            r'^\s*-\s*\[\s*\]\s*(.+)$',  # - [ ] task
            r'^\s*\*\s*\[\s*\]\s*(.+)$',  # * [ ] task
            r'^\s*\+\s*\[\s*\]\s*(.+)$',  # + [ ] task
            r'^\s*-\s*TODO:\s*(.+)$',     # - TODO: task
            r'^\s*\*\s*TODO:\s*(.+)$',    # * TODO: task
            r'^\s*#\s*TODO\s*(.+)$',      # # TODO task
            r'^\s*##\s*TODO\s*(.+)$',     # ## TODO task
        ]
        
        # Pattern for completed tasks
        self.completed_patterns = [
            r'^\s*-\s*\[x\]\s*(.+)$',     # - [x] completed task
            r'^\s*\*\s*\[x\]\s*(.+)$',    # * [x] completed task
            r'^\s*\+\s*\[x\]\s*(.+)$',    # + [x] completed task
        ]
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse a markdown file and extract tasks"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            console.print(f"❌ File not found: {file_path}")
            return []
        
        if file_path.suffix.lower() not in ['.md', '.markdown']:
            console.print(f"⚠️  File is not a markdown file: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._parse_content(content, str(file_path))
        
        except Exception as e:
            console.print(f"❌ Error parsing file {file_path}: {e}")
            return []
    
    def _parse_content(self, content: str, source_file: str) -> List[Dict]:
        """Parse markdown content and extract tasks"""
        tasks = []
        lines = content.split('\n')
        
        current_section = ""
        section_stack = []
        
        for line_num, line in enumerate(lines, 1):
            # Track current section/heading
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                section_title = line.strip('#').strip()
                
                # Update section stack based on heading level
                if level <= len(section_stack):
                    section_stack = section_stack[:level-1]
                section_stack.append(section_title)
                current_section = " > ".join(section_stack)
                continue
            
            # Check for tasks
            task_content = self._extract_task(line)
            if task_content:
                task = {
                    'title': task_content.strip(),
                    'description': f"From {source_file}, line {line_num}",
                    'section': current_section,
                    'line_number': line_num,
                    'source_file': source_file,
                    'original_line': line.strip(),
                    'status': 'pending'
                }
                
                # Check if it's a completed task
                if self._is_completed_task(line):
                    task['status'] = 'completed'
                
                tasks.append(task)
        
        return tasks
    
    def _extract_task(self, line: str) -> str:
        """Extract task content from a line"""
        for pattern in self.task_patterns + self.completed_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _is_completed_task(self, line: str) -> bool:
        """Check if a task is marked as completed"""
        for pattern in self.completed_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def parse_directory(self, directory_path: str) -> List[Dict]:
        """Parse all markdown files in a directory"""
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            console.print(f"❌ Directory not found: {directory_path}")
            return []
        
        all_tasks = []
        markdown_files = list(directory_path.rglob("*.md")) + list(directory_path.rglob("*.markdown"))
        
        console.print(f"📄 Found {len(markdown_files)} markdown files")
        
        for md_file in markdown_files:
            # Skip hidden files and common ignore patterns
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if any(ignore in str(md_file) for ignore in ['node_modules', '__pycache__', '.git']):
                continue
                
            console.print(f"📄 Parsing: {md_file.relative_to(directory_path)}")
            file_tasks = self.parse_file(str(md_file))
            all_tasks.extend(file_tasks)
        
        return all_tasks
    
    def get_task_summary(self, tasks: List[Dict]) -> Dict:
        """Get a summary of parsed tasks"""
        summary = {
            'total_tasks': len(tasks),
            'pending_tasks': len([t for t in tasks if t['status'] == 'pending']),
            'completed_tasks': len([t for t in tasks if t['status'] == 'completed']),
            'files_with_tasks': len(set(t['source_file'] for t in tasks)),
            'sections': list(set(t['section'] for t in tasks if t['section']))
        }
        return summary
    
    def create_todos_from_tasks(self, tasks: List[Dict], todo_manager, priority: str = "medium") -> List[str]:
        """Create todo items from parsed tasks"""
        todo_ids = []
        
        for task in tasks:
            if task['status'] == 'pending':  # Only create todos for pending tasks
                todo_id = todo_manager.add_todo(
                    title=task['title'],
                    description=f"From {task['section']} in {Path(task['source_file']).name}",
                    todo_type="text",
                    priority=priority,
                    content=f"Source: {task['source_file']}:{task['line_number']}\nOriginal: {task['original_line']}"
                )
                todo_ids.append(todo_id)
        
        return todo_ids