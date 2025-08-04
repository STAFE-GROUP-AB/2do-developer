"""
Multitasker - Handles parallel processing of multiple todos using different AI models
"""

import asyncio
import concurrent.futures
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, TaskID

console = Console()

class Multitasker:
    """Manages parallel execution of todos using optimal AI models"""
    
    def __init__(self, ai_router):
        self.ai_router = ai_router
        self.max_workers = 5  # Maximum concurrent tasks
    
    async def process_todo_async(self, todo: Dict, progress_callback=None) -> Dict:
        """Process a single todo asynchronously"""
        try:
            # Update status to in_progress
            todo["status"] = "in_progress"
            
            # Show what we're working on
            todo_title = todo['title'][:50] + "..." if len(todo['title']) > 50 else todo['title']
            console.print(f"🔨 Starting work on: [bold cyan]{todo_title}[/bold cyan]")
            
            # Create prompt based on todo type and content
            prompt = self._create_prompt_for_todo(todo)
            
            # Show routing stage
            console.print(f"🤔 Analyzing task requirements for optimal AI model...")
            
            # Route to best AI model and process
            result = self.ai_router.route_and_process(prompt, todo_context=todo_title)
            
            # Update todo with result
            todo["status"] = "completed"
            todo["result"] = result
            
            # Show completion
            console.print(f"✅ Completed: [bold green]{todo_title}[/bold green]")
            
            return todo
            
        except Exception as e:
            todo_title = todo['title'][:50] + "..." if len(todo['title']) > 50 else todo['title']
            console.print(f"❌ Error processing [bold red]{todo_title}[/bold red]: {str(e)}")
            todo["status"] = "failed"
            todo["result"] = f"Error: {str(e)}"
            return todo
    
    def _create_prompt_for_todo(self, todo: Dict) -> str:
        """Create an appropriate prompt based on todo type and content"""
        base_prompt = f"Task: {todo['title']}\nDescription: {todo['description']}\n"
        
        # Add context for sub-tasks
        if todo.get("parent_id"):
            base_prompt += "NOTE: This is a sub-task that is part of a larger project.\n"
            base_prompt += "Focus on this specific component while keeping the broader context in mind.\n"
        elif todo.get("sub_task_ids") and len(todo.get("sub_task_ids", [])) > 0:
            base_prompt += f"NOTE: This is a parent task with {len(todo['sub_task_ids'])} sub-tasks.\n"
            base_prompt += "Provide a high-level approach that can guide the individual sub-tasks.\n"
        
        if todo["todo_type"] == "code":
            base_prompt += "This is a coding task. Please provide a complete solution with code examples and explanations.\n"
        elif todo["todo_type"] == "text":
            base_prompt += "This is a text-based task. Please provide a comprehensive written response.\n"
        elif todo["todo_type"] == "image":
            base_prompt += "This relates to image processing or analysis.\n"
        
        if todo["content"]:
            base_prompt += f"\nAdditional context:\n{todo['content']}\n"
        
        base_prompt += f"\nPriority: {todo['priority']}\n"
        
        # Adjust prompt based on priority and task type
        if todo.get("parent_id"):
            base_prompt += "Please provide a focused solution for this specific sub-task."
        else:
            base_prompt += "Please provide a detailed and actionable response."
        
        return base_prompt
    
    def start_multitask(self, todos: List[Dict]):
        """Start multitasking processing of todos with sub-task awareness"""
        if not todos:
            console.print("No todos to process")
            return
        
        # Analyze todos for sub-task relationships
        parent_todos = [todo for todo in todos if not todo.get("parent_id")]
        sub_todos = [todo for todo in todos if todo.get("parent_id")]
        
        console.print(f"🚀 Starting multitask processing for {len(todos)} todos...")
        console.print(f"   📁 {len(parent_todos)} parent todos")
        console.print(f"   📎 {len(sub_todos)} sub-tasks")
        
        # Offer processing options
        if sub_todos and parent_todos:
            from rich.prompt import Prompt, Confirm
            
            if Confirm.ask("Process parent todos and sub-tasks hierarchically (parents first)?"):
                self._process_hierarchical(parent_todos, sub_todos)
                return
        
        # Run async processing
        results = asyncio.run(self._process_todos_parallel(todos))
        
        # Display results
        self._display_results(results)
    
    def _process_hierarchical(self, parent_todos: List[Dict], sub_todos: List[Dict]):
        """Process parent todos first, then their sub-tasks"""
        console.print("📋 Processing in hierarchical order...")
        
        # Process parent todos first
        console.print("\n🔹 Phase 1: Processing parent todos...")
        parent_results = asyncio.run(self._process_todos_parallel(parent_todos))
        
        # Process sub-tasks
        console.print("\n🔹 Phase 2: Processing sub-tasks...")
        sub_results = asyncio.run(self._process_todos_parallel(sub_todos))
        
        # Combine and display all results
        all_results = parent_results + sub_results
        console.print("\n📊 Combined Results:")
        self._display_results(all_results)
    
    async def _process_todos_parallel(self, todos: List[Dict]) -> List[Dict]:
        """Process todos in parallel with progress tracking"""
        
        # Show overview of what will be processed
        console.print(f"\n📋 About to process {len(todos)} todos:")
        for i, todo in enumerate(todos[:5], 1):  # Show first 5
            todo_preview = todo['title'][:40] + "..." if len(todo['title']) > 40 else todo['title']
            console.print(f"   {i}. [cyan]{todo_preview}[/cyan] ({todo['priority']} priority)")
        if len(todos) > 5:
            console.print(f"   ... and {len(todos) - 5} more todos")
        console.print("")
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Processing {len(todos)} todos...", total=len(todos))
            completed_count = 0
            
            # Create semaphore to limit concurrent tasks
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_with_semaphore(todo):
                nonlocal completed_count
                async with semaphore:
                    result = await self.process_todo_async(todo)
                    completed_count += 1
                    
                    # Update progress with current status
                    progress.update(task, 
                                  advance=1, 
                                  description=f"[cyan]Processed {completed_count}/{len(todos)} todos...")
                    return result
            
            # Create tasks for all todos
            tasks = [process_with_semaphore(todo) for todo in todos]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return [r for r in results if not isinstance(r, Exception)]
    
    def _display_results(self, results: List[Dict]):
        """Display processing results"""
        console.print("\n" + "="*60)
        console.print("📊 Multitask Processing Results")
        console.print("="*60)
        
        completed = 0
        failed = 0
        
        for result in results:
            status = result["status"]
            if status == "completed":
                completed += 1
                console.print(f"✅ {result['title']} - COMPLETED")
                if result.get("result"):
                    # Show first 100 chars of result
                    preview = result["result"][:100] + "..." if len(result["result"]) > 100 else result["result"]
                    console.print(f"   📝 Result preview: {preview}")
            elif status == "failed":
                failed += 1
                console.print(f"❌ {result['title']} - FAILED")
                if result.get("result"):
                    console.print(f"   ⚠️  Error: {result['result']}")
        
        console.print(f"\n📈 Summary: {completed} completed, {failed} failed out of {len(results)} total")
    
    def process_batch_by_type(self, todos: List[Dict], todo_type: str):
        """Process a batch of todos of a specific type"""
        filtered_todos = [todo for todo in todos if todo["todo_type"] == todo_type]
        
        if not filtered_todos:
            console.print(f"No todos of type '{todo_type}' found")
            return
        
        console.print(f"🎯 Processing {len(filtered_todos)} todos of type '{todo_type}'...")
        self.start_multitask(filtered_todos)
    
    def process_batch_by_priority(self, todos: List[Dict], priority: str):
        """Process a batch of todos of a specific priority"""
        filtered_todos = [todo for todo in todos if todo["priority"] == priority]
        
        if not filtered_todos:
            console.print(f"No todos with priority '{priority}' found")
            return
        
        console.print(f"🚨 Processing {len(filtered_todos)} todos with priority '{priority}'...")
        self.start_multitask(filtered_todos)