#!/usr/bin/env python3
"""
Demonstration of the new streaming and local model features
"""
import asyncio
import time
from rich.console import Console
from rich.panel import Panel

# Import our enhanced components
from twodo.ai_router import AIRouter, LocalModelCapability
from twodo.config import ConfigManager

console = Console()

async def demo_streaming():
    """Demonstrate streaming responses"""
    console.print(Panel("🚀 Streaming Response Demo", style="bold blue"))
    
    # Create a simple mock streaming function
    async def mock_stream():
        words = ["Hello,", "this", "is", "a", "demonstration", "of", "real-time", "streaming", "responses!", "✨"]
        for word in words:
            await asyncio.sleep(0.3)  # Simulate model processing time
            yield word + " "
    
    console.print("🤖 AI Response: ", end="")
    async for chunk in mock_stream():
        console.print(chunk, end="")
    console.print("\n")
    console.print("✅ Streaming demo complete!")

def demo_local_models():
    """Demonstrate local model capabilities"""
    console.print(Panel("🏠 Local Models Demo", style="bold green"))
    
    # Create example local models
    models = {
        "llama-3.2-3b": LocalModelCapability(
            name="llama-3.2-3b",
            provider="local",
            strengths=["general", "code", "reasoning", "privacy"],
            context_length=8192,
            cost_per_token=0.0,
            speed_rating=6,
            model_path="~/.2do/models/llama-3.2-3b",
            quantization="4bit",
            memory_requirements_gb=3,
            gpu_required=False
        ),
        "codellama-7b": LocalModelCapability(
            name="codellama-7b",
            provider="local",
            strengths=["code", "programming", "debugging", "privacy"],
            context_length=4096,
            cost_per_token=0.0,
            speed_rating=5,
            model_path="~/.2do/models/codellama-7b",
            quantization="4bit",
            memory_requirements_gb=5,
            gpu_required=False
        )
    }
    
    console.print("📋 Available Local Models:")
    for name, model in models.items():
        console.print(f"  • {name}")
        console.print(f"    ├─ Strengths: {', '.join(model.strengths)}")
        console.print(f"    ├─ Memory: {model.memory_requirements_gb}GB")
        console.print(f"    ├─ Context: {model.context_length:,} tokens")
        console.print(f"    └─ Cost: FREE (${model.cost_per_token}/token)")
        console.print()
    
    console.print("✅ Local models provide:")
    console.print("  🔒 Complete privacy (no external API calls)")
    console.print("  💰 Zero cost per request")
    console.print("  🌐 Offline operation capability")
    console.print("  ⚡ Fast local processing")

def demo_configuration():
    """Demonstrate configuration management"""
    console.print(Panel("⚙️ Configuration Demo", style="bold cyan"))
    
    # Show example configurations
    settings = {
        "enable_streaming": True,
        "enable_local_models": True,
        "show_all_local_models": True,
        "load_only_free_models": True,
        "default_model": "auto",
        "max_parallel_tasks": 5,
        "memory_enabled": True
    }
    
    console.print("📊 Current Configuration:")
    for setting, value in settings.items():
        status = "✅" if value else "❌"
        console.print(f"  {status} {setting}: {value}")
    
    console.print("\n💡 Available Commands:")
    console.print("  • 2do config list - Show all settings")
    console.print("  • 2do config set enable_streaming true")
    console.print("  • 2do local-models --enable")
    console.print("  • 2do streaming --status")

async def main():
    """Run all demos"""
    console.print(Panel.fit("🎯 2DO Enhancement Demonstrations", style="bold magenta"))
    console.print()
    
    # Demo 1: Streaming
    await demo_streaming()
    console.print()
    
    # Demo 2: Local Models
    demo_local_models()
    console.print()
    
    # Demo 3: Configuration
    demo_configuration()
    console.print()
    
    console.print(Panel("🎉 Enhancement Demo Complete!", style="bold green"))
    console.print("🚀 These features are now available in 2DO!")
    console.print("💡 Try them out with the commands shown above.")

if __name__ == "__main__":
    asyncio.run(main())