"""
Multitasker - Handles parallel processing of multiple todos using different AI models
"""

import asyncio
import concurrent.futures
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, TaskID
from .escape_handler import check_escape_interrupt, EscapeInterrupt, raise_if_interrupted

console = Console()

class Multitasker:
    """Manages parallel execution of todos using optimal AI models"""
    
    def __init__(self, ai_router, todo_manager=None):
        self.ai_router = ai_router
        self.todo_manager = todo_manager
        self.max_workers = 5  # Maximum concurrent tasks
    
    async def process_todo_async(self, todo: Dict, progress_callback=None) -> Dict:
        """Process a single todo asynchronously"""
        todo_id = todo["id"]
        try:
            # Update status to in_progress and persist to file
            if self.todo_manager:
                self.todo_manager.update_todo_status(todo_id, "in_progress")
            else:
                todo["status"] = "in_progress"
            
            # Show what we're working on
            todo_title = todo['title'][:50] + "..." if len(todo['title']) > 50 else todo['title']
            console.print(f"🔨 Starting work on: [bold cyan]{todo_title}[/bold cyan]")
            
            # Check for escape interrupt before starting
            if check_escape_interrupt():
                raise EscapeInterrupt("Todo processing interrupted by escape key")
            
            # Create prompt based on todo type and content
            prompt = self._create_prompt_for_todo(todo)
            
            # Show routing stage
            console.print(f"🤔 Analyzing task requirements for optimal AI model...")
            
            # Check for escape interrupt before AI processing
            if check_escape_interrupt():
                raise EscapeInterrupt("Todo processing interrupted by escape key")
            
            # Route to best AI model and process
            result = await self.ai_router.route_and_process(prompt, todo_context=todo_title)
            
            # Update todo with result and persist to file
            if self.todo_manager:
                # Get the model that was selected for this task
                assigned_model = getattr(self.ai_router, 'last_selected_model', 'auto')
                self.todo_manager.update_todo_status(todo_id, "completed", result, assigned_model)
                # Return updated todo from manager to ensure consistency
                updated_todo = self.todo_manager.get_todo_by_id(todo_id)
                
                # Show completion with enhanced display from PR #46
                console.print(f"✅ Completed: [bold green]{todo_title}[/bold green]")
                
                return updated_todo if updated_todo else todo
            else:
                todo["status"] = "completed"
                todo["result"] = result
                
                # Show completion
                console.print(f"✅ Completed: [bold green]{todo_title}[/bold green]")
                
                return todo
            
        except EscapeInterrupt as e:
            # Handle escape interrupt gracefully
            todo_title = todo['title'][:50] + "..." if len(todo['title']) > 50 else todo['title']
            console.print(f"⚠️ Interrupted: [bold yellow]{todo_title}[/bold yellow] - {str(e)}")
            
            # Update status to interrupted
            if self.todo_manager:
                self.todo_manager.update_todo_status(todo_id, "pending", "Interrupted by user")
                updated_todo = self.todo_manager.get_todo_by_id(todo_id)
                return updated_todo if updated_todo else todo
            else:
                todo["status"] = "pending"
                todo["result"] = "Interrupted by user"
                return todo
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            todo_title = todo['title'][:50] + "..." if len(todo['title']) > 50 else todo['title']
            console.print(f"❌ Error processing [bold red]{todo_title}[/bold red]: {error_msg}")
            
            # Update status to failed and persist to file
            if self.todo_manager:
                try:
                    self.todo_manager.update_todo_status(todo_id, "failed", error_msg)
                    updated_todo = self.todo_manager.get_todo_by_id(todo_id)
                    return updated_todo if updated_todo else todo
                except Exception as save_error:
                    console.print(f"⚠️ Could not save todo status: {save_error}")
                    # Fall back to in-memory update
                    todo["status"] = "failed"
                    todo["result"] = error_msg
                    return todo
            else:
                todo["status"] = "failed"
                todo["result"] = error_msg
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
    
    async def start_multitask(self, todos: List[Dict]):
        """Start multitasking processing of todos with sub-task awareness"""
        console.print(f"🔍 DEBUG: start_multitask called with {len(todos) if todos else 0} todos")
        
        if not todos:
            console.print("No todos to process")
            console.print("🔍 DEBUG: Returning success=False due to no todos")
            return {"success": False, "message": "No todos to process"}
        
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
                console.print("🔍 DEBUG: Processing hierarchically")
                await self._process_hierarchical_async(parent_todos, sub_todos)
                console.print("🔍 DEBUG: Hierarchical processing complete, returning success=True")
                return {"success": True, "message": "Hierarchical processing completed"}
        
        # Run async processing
        console.print("🔍 DEBUG: Starting parallel processing")
        results = await self._process_todos_parallel(todos)
        console.print(f"🔍 DEBUG: Parallel processing complete, got {len(results) if results else 0} results")
        
        # Display results
        self._display_results(results)
        console.print("🔍 DEBUG: Results displayed, returning success=True")
        return {"success": True, "message": f"Processed {len(results)} todos", "results": results}
    
    def _process_hierarchical(self, parent_todos: List[Dict], sub_todos: List[Dict]):
        """Process parent todos first, then their sub-tasks (synchronous version)"""
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
    
    async def _process_hierarchical_async(self, parent_todos: List[Dict], sub_todos: List[Dict]):
        """Process parent todos first, then their sub-tasks (async version)"""
        console.print("📋 Processing in hierarchical order...")
        
        # Process parent todos first
        console.print("\n🔹 Phase 1: Processing parent todos...")
        parent_results = await self._process_todos_parallel(parent_todos)
        
        # Process sub-tasks
        console.print("\n🔹 Phase 2: Processing sub-tasks...")
        sub_results = await self._process_todos_parallel(sub_todos)
        
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
                    # Check for escape interrupt before processing each todo
                    if check_escape_interrupt():
                        raise EscapeInterrupt("Multitasking interrupted by escape key")
                        
                    result = await self.process_todo_async(todo)
                    completed_count += 1
                    
                    # Update progress with current status
                    progress.update(task, 
                                  advance=1, 
                                  description=f"[cyan]Processed {completed_count}/{len(todos)} todos...")
                    return result
            
            # Create tasks for all todos
            tasks = [process_with_semaphore(todo) for todo in todos]
            
            # Wait for all tasks to complete with escape handling
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return [r for r in results if not isinstance(r, Exception)]
            except EscapeInterrupt:
                console.print("\n⚠️ Multitasking interrupted by escape key")
                # Cancel remaining tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                # Return partial results
                completed_results = [r for r in results if r is not None and not isinstance(r, Exception)]
                return completed_results
    
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
                    # Show full result without truncation
                    console.print(f"   📝 Result: {result['result']}")
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
        # CRITICAL FIX: Use asyncio.run for async method call
        asyncio.run(self.start_multitask(filtered_todos))
    
    def process_batch_by_priority(self, todos: List[Dict], priority: str):
        """Process a batch of todos of a specific priority"""
        filtered_todos = [todo for todo in todos if todo["priority"] == priority]
        
        if not filtered_todos:
            console.print(f"No todos with priority '{priority}' found")
            return
        
        console.print(f"🚨 Processing {len(filtered_todos)} todos with priority '{priority}'...")
        # CRITICAL FIX: Use asyncio.run for async method call
        asyncio.run(self.start_multitask(filtered_todos))