#!/usr/bin/env python3
"""
Demo script for 2DO
Demonstrates key functionality without requiring API keys
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from twodo.todo_manager import TodoManager
from twodo.tech_stack import TechStackDetector
from twodo.ai_router import AIRouter, ModelCapability

console = Console()

def demo_tech_stack_detection():
    """Demonstrate tech stack detection"""
    console.print(Panel.fit("🔍 Tech Stack Detection Demo", style="bold blue"))
    
    detector = TechStackDetector()
    
    # Analyze current repository
    tech_stack = detector.analyze_repo(".")
    console.print(f"📁 Analyzing current repository...")
    console.print(f"🎯 Detected technologies: {', '.join(tech_stack)}")
    
    # Show memory context for Python
    if "python" in tech_stack:
        python_context = detector.get_memory_context("python")
        console.print(f"\n💾 Python context includes:")
        console.print(f"   - {len(python_context.get('best_practices', []))} best practices")
        console.print(f"   - {len(python_context.get('common_libraries', []))} common libraries")
        console.print(f"   - {len(python_context.get('testing_frameworks', []))} testing frameworks")

def demo_todo_management():
    """Demonstrate todo management"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("📋 Todo Management Demo", style="bold green"))
    
    todo_manager = TodoManager()
    
    # Add some demo todos
    demo_todos = [
        ("Code Review", "Review Python code for best practices", "code", "high"),
        ("Update Documentation", "Update README with new features", "text", "medium"),
        ("Performance Analysis", "Analyze application performance", "general", "low"),
        ("API Integration", "Integrate with new AI models", "code", "critical")
    ]
    
    console.print("Adding demo todos...")
    for title, desc, todo_type, priority in demo_todos:
        todo_manager.add_todo(title, desc, todo_type, priority)
    
    # Display todos in a table
    todos = todo_manager.get_todos()
    table = Table(title="Current Todos")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Priority", style="red")
    table.add_column("Status", style="blue")
    
    for todo in todos[-4:]:  # Show only the demo todos
        table.add_row(
            todo["id"],
            todo["title"],
            todo["todo_type"],
            todo["priority"],
            todo["status"]
        )
    
    console.print(table)
    
    # Show completion stats
    stats = todo_manager.get_completion_stats()
    console.print(f"\n📊 Stats: {stats['total']} total, {stats['pending']} pending, {stats['completed']} completed")

def demo_ai_model_capabilities():
    """Demonstrate AI model capabilities and selection logic"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🤖 AI Model Selection Demo", style="bold yellow"))
    
    # Create demo model capabilities
    models = {
        "gpt-4": ModelCapability(
            name="gpt-4",
            provider="openai",
            strengths=["reasoning", "complex_tasks", "code_analysis"],
            context_length=8192,
            cost_per_token=0.03,
            speed_rating=6
        ),
        "claude-3-haiku": ModelCapability(
            name="claude-3-haiku",
            provider="anthropic",
            strengths=["speed", "simple_tasks", "quick_answers"],
            context_length=200000,
            cost_per_token=0.00025,
            speed_rating=10
        ),
        "gpt-4-turbo": ModelCapability(
            name="gpt-4-turbo",
            provider="openai",
            strengths=["code", "reasoning", "large_context"],
            context_length=128000,
            cost_per_token=0.01,
            speed_rating=7
        )
    }
    
    # Show model comparison
    model_table = Table(title="Available AI Models")
    model_table.add_column("Model", style="cyan")
    model_table.add_column("Provider", style="green")
    model_table.add_column("Strengths", style="yellow")
    model_table.add_column("Speed", style="red")
    model_table.add_column("Context", style="blue")
    
    for model in models.values():
        model_table.add_row(
            model.name,
            model.provider,
            ", ".join(model.strengths[:2]),
            f"{model.speed_rating}/10",
            f"{model.context_length:,}"
        )
    
    console.print(model_table)
    
    # Demo prompt analysis
    demo_prompts = [
        "Fix this Python function that's throwing an error",
        "Quick question: what's 2+2?",
        "Write a comprehensive analysis of machine learning trends",
        "Debug this complex algorithm with multiple edge cases"
    ]
    
    console.print(f"\n🎯 Prompt Analysis Examples:")
    for prompt in demo_prompts:
        # Simulate prompt analysis (simplified)
        if "quick" in prompt.lower() or "2+2" in prompt:
            best_model = "claude-3-haiku (speed optimized)"
        elif "comprehensive" in prompt.lower() or "complex" in prompt.lower():
            best_model = "gpt-4 (reasoning optimized)"
        elif "code" in prompt.lower() or "function" in prompt.lower():
            best_model = "gpt-4-turbo (code optimized)"
        else:
            best_model = "gpt-4 (balanced)"
        
        console.print(f"   📝 '{prompt[:40]}...' → {best_model}")

def demo_multitasking_concept():
    """Demonstrate multitasking concept"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("⚡ Multitasking Engine Demo", style="bold magenta"))
    
    # Create a tree view of the multitasking process
    tree = Tree("🚀 Multitasking Process")
    
    analysis_branch = tree.add("📊 Task Analysis")
    analysis_branch.add("🔍 Analyze todo types and complexity")
    analysis_branch.add("🎯 Select optimal AI model for each task")
    analysis_branch.add("📋 Create optimized prompts")
    
    execution_branch = tree.add("⚡ Parallel Execution")
    execution_branch.add("🔄 Process up to 5 tasks simultaneously")
    execution_branch.add("📈 Track progress in real-time")
    execution_branch.add("🔀 Load balance across AI models")
    
    results_branch = tree.add("📊 Results Aggregation")
    results_branch.add("✅ Collect completed tasks")
    results_branch.add("❌ Handle failed tasks")
    results_branch.add("📋 Generate summary report")
    
    console.print(tree)
    
    console.print(f"\n💡 Benefits:")
    console.print(f"   • Process multiple todos simultaneously")
    console.print(f"   • Optimal AI model selection for each task")
    console.print(f"   • Cost and time optimization")
    console.print(f"   • Automatic error handling and retry logic")

def main():
    """Run the complete demo"""
    console.print(Panel.fit("🚀 2DO - Interactive Demo", style="bold white on blue"))
    console.print("This demo showcases the key features of 2DO without requiring API keys.\n")
    
    try:
        demo_tech_stack_detection()
        demo_todo_management()
        demo_ai_model_capabilities()
        demo_multitasking_concept()
        
        console.print("\n" + "="*60)
        console.print(Panel.fit("✨ Demo Complete!", style="bold green"))
        console.print("To use 2DO with real AI models:")
        console.print("1. Run: 2do setup")
        console.print("2. Enter your API keys for OpenAI, Anthropic, etc.")
        console.print("3. Run: 2do start")
        console.print("4. Start creating todos and let 2DO work its magic! 🎉")
        
    except Exception as e:
        console.print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()