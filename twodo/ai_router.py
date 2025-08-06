"""
AI Router - Intelligent routing of prompts to the best AI model
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from rich.console import Console
from .config import ConfigManager
from .mcp_client import MCPClient

# Import AI clients
import openai
import anthropic

# Conditional import for Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

console = Console()

@dataclass
class ModelCapability:
    """Represents capabilities of an AI model"""
    name: str
    provider: str
    strengths: List[str]
    context_length: int
    cost_per_token: float
    speed_rating: int  # 1-10, 10 being fastest
    is_free: bool = False  # Whether this model is free to use
    requires_api_key: bool = True  # Whether this model requires an API key

class AIRouter:
    """Routes prompts to the most suitable AI model"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.models = self._initialize_models()
        self.developer_context = ""
        self._setup_clients()
        self.last_selected_model = None
        self.mcp_client = MCPClient(config_manager)
        self.filesystem_initialized = False
    
    def _initialize_models(self) -> Dict[str, ModelCapability]:
        """Initialize available models with their capabilities"""
        models = {}
        
        # Check if we should load only free models by default
        load_only_free = self.config.get_preference("load_only_free_models", True)
        
        # OpenAI models
        if self.config.get_api_key("openai"):
            all_openai_models = {
                "gpt-4o": ModelCapability(
                    name="gpt-4o",
                    provider="openai",
                    strengths=["reasoning", "complex_tasks", "code_analysis", "multimodal", "general", "tall_stack", "testing"],
                    context_length=128000,
                    cost_per_token=0.005,
                    speed_rating=8,
                    is_free=False
                ),
                "gpt-4o-mini": ModelCapability(
                    name="gpt-4o-mini",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks", "cost_effective", "code", "multimodal"],
                    context_length=128000,
                    cost_per_token=0.0002,
                    speed_rating=9,
                    is_free=True  # Free tier available
                ),
                "gpt-4": ModelCapability(
                    name="gpt-4",
                    provider="openai",
                    strengths=["reasoning", "complex_tasks", "code_analysis", "general", "architecture"],
                    context_length=8192,
                    cost_per_token=0.03,
                    speed_rating=6,
                    is_free=False
                ),
                "gpt-3.5-turbo": ModelCapability(
                    name="gpt-3.5-turbo",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks", "code"],
                    context_length=4096,
                    cost_per_token=0.002,
                    speed_rating=9,
                    is_free=True  # Free tier available
                ),
                "gpt-4-turbo": ModelCapability(
                    name="gpt-4-turbo",
                    provider="openai",
                    strengths=["code", "reasoning", "large_context", "analysis", "multimodal", "refactoring"],
                    context_length=128000,
                    cost_per_token=0.01,
                    speed_rating=7,
                    is_free=False
                )
            }
            
            # Add OpenAI models based on preference
            for name, model in all_openai_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Anthropic models
        if self.config.get_api_key("anthropic"):
            all_anthropic_models = {
                "claude-opus-4-20250514": ModelCapability(
                    name="claude-opus-4-20250514",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis", "research", "writing"],
                    context_length=200000,
                    cost_per_token=0.015,
                    speed_rating=6,
                    is_free=False
                ),
                "claude-sonnet-4-20250514": ModelCapability(
                    name="claude-sonnet-4-20250514",
                    provider="anthropic",
                    strengths=["reasoning", "code", "balanced", "general", "analysis"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8,
                    is_free=False
                ),
                "claude-3-7-sonnet-20250219": ModelCapability(
                    name="claude-3-7-sonnet-20250219",
                    provider="anthropic",
                    strengths=["reasoning", "code", "balanced", "general"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8,
                    is_free=False
                ),
                "claude-3-5-sonnet-20241022": ModelCapability(
                    name="claude-3-5-sonnet-20241022",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis", "code", "balanced", "refactoring", "debugging", "tall_stack"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8,
                    is_free=False
                ),
                "claude-3-5-haiku-20241022": ModelCapability(
                    name="claude-3-5-haiku-20241022",
                    provider="anthropic",
                    strengths=["speed", "simple_tasks", "quick_answers", "code", "testing"],
                    context_length=200000,
                    cost_per_token=0.00025,
                    speed_rating=10,
                    is_free=True  # Has free tier
                ),
                "claude-3-opus-20240229": ModelCapability(
                    name="claude-3-opus-20240229",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis", "architecture", "documentation"],
                    context_length=200000,
                    cost_per_token=0.015,
                    speed_rating=5,
                    is_free=False
                )
            }
            
            # Add Anthropic models based on preference
            for name, model in all_anthropic_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Google Gemini models
        if GOOGLE_AI_AVAILABLE and self.config.get_api_key("google"):
            all_google_models = {
                "gemini-1.5-pro": ModelCapability(
                    name="gemini-1.5-pro",
                    provider="google",
                    strengths=["reasoning", "complex_tasks", "multimodal", "large_context", "analysis", "code", "tall_stack"],
                    context_length=2000000,  # 2M tokens
                    cost_per_token=0.0035,
                    speed_rating=7,
                    is_free=False
                ),
                "gemini-1.5-flash": ModelCapability(
                    name="gemini-1.5-flash",
                    provider="google",
                    strengths=["speed", "general", "multimodal", "balanced", "code", "testing"],
                    context_length=1000000,  # 1M tokens
                    cost_per_token=0.00015,
                    speed_rating=9,
                    is_free=True  # Has free tier
                ),
                "gemini-1.0-pro": ModelCapability(
                    name="gemini-1.0-pro",
                    provider="google",
                    strengths=["general", "reasoning", "balanced", "code"],
                    context_length=32000,
                    cost_per_token=0.0005,
                    speed_rating=8,
                    is_free=True  # Has free tier
                )
            }
            
            # Add Google models based on preference
            for name, model in all_google_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Add placeholder models for other providers (will be implemented as providers become available)
        # These models are shown in ai-list but need actual API implementation
        self._add_placeholder_models(models, load_only_free)
        
        return models
    
    def _add_placeholder_models(self, models: Dict[str, ModelCapability], load_only_free: bool):
        """Add placeholder models for providers that have API keys but no full implementation yet"""
        
        # xAI models (Grok)
        if self.config.get_api_key("xai"):
            xai_models = {
                "grok-4": ModelCapability(
                    name="grok-4", 
                    provider="xai",
                    strengths=["reasoning", "general", "conversational"],
                    context_length=32000,
                    cost_per_token=0.01,
                    speed_rating=7,
                    is_free=False
                )
            }
            
            for name, model in xai_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # DeepSeek models
        if self.config.get_api_key("deepseek"):
            deepseek_models = {
                "deepseek-v3": ModelCapability(
                    name="deepseek-v3",
                    provider="deepseek", 
                    strengths=["code", "reasoning", "analysis"],
                    context_length=64000,
                    cost_per_token=0.002,
                    speed_rating=6,
                    is_free=False
                ),
                "deepseek-r1": ModelCapability(
                    name="deepseek-r1",
                    provider="deepseek",
                    strengths=["reasoning", "analysis", "research"],
                    context_length=64000,
                    cost_per_token=0.003,
                    speed_rating=5,
                    is_free=False
                )
            }
            
            for name, model in deepseek_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Mistral models
        if self.config.get_api_key("mistral"):
            mistral_models = {
                "mistral-large-2": ModelCapability(
                    name="mistral-large-2",
                    provider="mistral",
                    strengths=["reasoning", "code", "general", "multilingual"],
                    context_length=128000,
                    cost_per_token=0.006,
                    speed_rating=7,
                    is_free=False
                )
            }
            
            for name, model in mistral_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Cohere models
        if self.config.get_api_key("cohere"):
            cohere_models = {
                "command-r-plus": ModelCapability(
                    name="command-r-plus",
                    provider="cohere",
                    strengths=["general", "reasoning", "commands", "retrieval"],
                    context_length=128000,
                    cost_per_token=0.005,
                    speed_rating=6,
                    is_free=False
                )
            }
            
            for name, model in cohere_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
        
        # Perplexity models
        if self.config.get_api_key("perplexity"):
            perplexity_models = {
                "pplx-70b-online": ModelCapability(
                    name="pplx-70b-online",
                    provider="perplexity",
                    strengths=["search", "general", "realtime", "web_access"],
                    context_length=4000,
                    cost_per_token=0.001,
                    speed_rating=8,
                    is_free=False
                )
            }
            
            for name, model in perplexity_models.items():
                if not load_only_free or model.is_free:
                    models[name] = model
    
    def enable_all_models(self):
        """Enable all available models (including paid ones)"""
        self.config.set_preference("load_only_free_models", False)
        self.models = self._initialize_models()
        console.print("✅ All models enabled! Use 'ai-list' to see available models.")
    
    def set_developer_context(self, context: str):
        """Set the developer context for enhanced AI responses"""
        self.developer_context = context
        console.print(f"🎯 Developer context set ({len(context)} characters)")
    
    def _setup_clients(self):
        """Setup API clients for each provider"""
        self.clients = {}
        
        if self.config.get_api_key("openai"):
            self.clients["openai"] = openai.OpenAI(
                api_key=self.config.get_api_key("openai")
            )
        
        if self.config.get_api_key("anthropic"):
            self.clients["anthropic"] = anthropic.Anthropic(
                api_key=self.config.get_api_key("anthropic")
            )
        
        if GOOGLE_AI_AVAILABLE and self.config.get_api_key("google"):
            genai.configure(api_key=self.config.get_api_key("google"))
            self.clients["google"] = genai
    
    def analyze_prompt(self, prompt: str, file_context: Dict = None) -> Dict[str, float]:
        """Enhanced prompt analysis with development-specific intelligence"""
        prompt_lower = prompt.lower()
        
        analysis = {
            "code": 0.0,
            "reasoning": 0.0,
            "creative": 0.0,
            "speed": 0.0,
            "analysis": 0.0,
            "simple_tasks": 0.0,
            "complex_tasks": 0.0,
            "large_context": 0.0,
            "multimodal": 0.0,
            "tall_stack": 0.0,
            "refactoring": 0.0,
            "testing": 0.0,
            "documentation": 0.0,
            "debugging": 0.0,
            "architecture": 0.0
        }
        
        # Enhanced code-related analysis
        code_keywords = {
            'basic': ['code', 'programming', 'function', 'class', 'method', 'variable'],
            'advanced': ['algorithm', 'optimization', 'refactor', 'architecture', 'design pattern'],
            'debugging': ['debug', 'error', 'bug', 'fix', 'trace', 'troubleshoot'],
            'testing': ['test', 'unit test', 'integration', 'mock', 'assert', 'coverage'],
            'git': ['git', 'commit', 'branch', 'merge', 'pull request', 'repository']
        }
        
        for category, keywords in code_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if category == 'basic':
                    analysis["code"] += 0.7
                elif category == 'advanced':
                    analysis["code"] += 0.9
                    analysis["complex_tasks"] += 0.6
                elif category == 'debugging':
                    analysis["debugging"] += 0.9
                    analysis["reasoning"] += 0.5
                elif category == 'testing':
                    analysis["testing"] += 0.9
                    analysis["code"] += 0.6
                elif category == 'git':
                    analysis["code"] += 0.5
        
        # TALL Stack specific analysis
        tall_keywords = {
            'laravel': ['laravel', 'artisan', 'eloquent', 'blade', 'composer', 'php'],
            'tailwind': ['tailwind', 'tailwindcss', 'css', 'styling', 'utility class'],
            'alpine': ['alpine', 'alpine.js', 'x-data', 'x-show', 'x-if'],
            'livewire': ['livewire', 'wire:', 'component', 'reactive']
        }
        
        for category, keywords in tall_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis["tall_stack"] += 0.8
                analysis["code"] += 0.6
                if category == 'laravel':
                    analysis["complex_tasks"] += 0.5
        
        # File context analysis (if provided)
        if file_context:
            file_ext = file_context.get('extension', '').lower()
            file_type = file_context.get('type', '')
            
            # Adjust analysis based on file type
            if file_ext in ['.php', '.blade.php']:
                analysis["tall_stack"] += 0.6
                analysis["code"] += 0.7
            elif file_ext in ['.js', '.ts', '.vue']:
                analysis["code"] += 0.8
                if 'alpine' in file_context.get('content', '').lower():
                    analysis["tall_stack"] += 0.5
            elif file_ext in ['.css', '.scss']:
                if 'tailwind' in file_context.get('content', '').lower():
                    analysis["tall_stack"] += 0.7
            elif file_ext in ['.md', '.txt']:
                analysis["documentation"] += 0.8
                analysis["creative"] += 0.4
        
        # Enhanced reasoning analysis
        reasoning_keywords = {
            'basic': ['analyze', 'explain', 'why', 'how', 'compare'],
            'advanced': ['evaluate', 'reason', 'logic', 'deduce', 'infer', 'conclude'],
            'architectural': ['design', 'structure', 'pattern', 'best practice', 'principle']
        }
        
        for category, keywords in reasoning_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if category == 'basic':
                    analysis["reasoning"] += 0.6
                elif category == 'advanced':
                    analysis["reasoning"] += 0.8
                elif category == 'architectural':
                    analysis["architecture"] += 0.9
                    analysis["reasoning"] += 0.7
        
        # Creative and documentation analysis
        creative_keywords = ['create', 'write', 'story', 'creative', 'generate', 'design', 'idea', 'documentation']
        doc_keywords = ['document', 'readme', 'guide', 'tutorial', 'docs', 'comment', 'api doc']
        
        if any(keyword in prompt_lower for keyword in creative_keywords):
            analysis["creative"] += 0.6
        
        if any(keyword in prompt_lower for keyword in doc_keywords):
            analysis["documentation"] += 0.8
            analysis["creative"] += 0.4
        
        # Speed and complexity analysis
        speed_keywords = ['quick', 'fast', 'simple', 'brief', 'short', 'immediately']
        complex_keywords = ['complex', 'detailed', 'comprehensive', 'thorough', 'deep', 'complete']
        refactor_keywords = ['refactor', 'restructure', 'reorganize', 'optimize', 'improve']
        
        if any(keyword in prompt_lower for keyword in speed_keywords):
            analysis["speed"] += 0.9
        
        if any(keyword in prompt_lower for keyword in complex_keywords):
            analysis["complex_tasks"] += 0.8
        
        if any(keyword in prompt_lower for keyword in refactor_keywords):
            analysis["refactoring"] += 0.9
            analysis["code"] += 0.7
        
        # Multimodal analysis
        multimodal_keywords = ['image', 'picture', 'screenshot', 'diagram', 'visual', 'ui', 'design']
        if any(keyword in prompt_lower for keyword in multimodal_keywords):
            analysis["multimodal"] += 0.9
        
        # Length-based analysis (enhanced)
        if len(prompt) < 50:
            analysis["simple_tasks"] += 0.7
            analysis["speed"] += 0.5
        elif len(prompt) < 200:
            analysis["simple_tasks"] += 0.3
            analysis["speed"] += 0.2
        elif len(prompt) > 1500:
            analysis["large_context"] += 0.8
            analysis["complex_tasks"] += 0.6
        elif len(prompt) > 800:
            analysis["large_context"] += 0.4
            analysis["complex_tasks"] += 0.3
        
        return analysis
    
    def select_best_model(self, prompt: str, todo_context: str = None, file_context: Dict = None) -> str:
        """Enhanced model selection with development-specific intelligence"""
        if not self.models:
            raise ValueError("No AI models configured. Please run setup first.")
        
        analysis = self.analyze_prompt(prompt, file_context)
        scores = {}
        
        for model_name, model in self.models.items():
            score = 0.0
            
            # Base scoring for model strengths
            for strength in model.strengths:
                if strength in analysis:
                    score += analysis[strength] * 10
            
            # Enhanced scoring logic
            
            # TALL Stack specialization bonus
            if analysis.get("tall_stack", 0) > 0.3:
                if model.provider == "anthropic" and "claude-3-5" in model.name:
                    score += 15  # Claude 3.5 excels at PHP/Laravel
                elif model.provider == "openai" and "gpt-4o" in model.name:
                    score += 12  # GPT-4o is great for full-stack
                elif model.provider == "google" and "gemini" in model.name:
                    score += 8   # Gemini is decent for web dev
            
            # Code-specific bonuses
            if analysis.get("code", 0) > 0.5:
                if "gpt-4" in model.name or "claude-3" in model.name:
                    score += 10  # Premium models for complex code
                if model.provider == "anthropic":
                    score += 5   # Anthropic models are great for code
            
            # Debugging and troubleshooting
            if analysis.get("debugging", 0) > 0.5:
                if "claude-3-5-sonnet" in model.name:
                    score += 20  # Claude 3.5 Sonnet excels at debugging
                elif "gpt-4o" in model.name:
                    score += 15
            
            # Testing and quality assurance
            if analysis.get("testing", 0) > 0.5:
                if model.provider == "openai" and "gpt-4" in model.name:
                    score += 12  # GPT-4 models are good for test generation
                elif "claude-3" in model.name:
                    score += 10
            
            # Architecture and design patterns
            if analysis.get("architecture", 0) > 0.5:
                if "claude-3-opus" in model.name:
                    score += 18  # Opus is excellent for architectural decisions
                elif "gpt-4" in model.name:
                    score += 15
            
            # Documentation tasks
            if analysis.get("documentation", 0) > 0.5:
                if "claude-3" in model.name:
                    score += 12  # Claude models excel at documentation
                elif "gpt-4" in model.name:
                    score += 10
            
            # Refactoring tasks
            if analysis.get("refactoring", 0) > 0.5:
                if "claude-3-5-sonnet" in model.name:
                    score += 18  # Sonnet is excellent for refactoring
                elif "gpt-4" in model.name:
                    score += 12
            
            # Multimodal tasks (images, UI, etc.)
            if analysis.get("multimodal", 0) > 0.5:
                if "gpt-4o" in model.name or "gpt-4-turbo" in model.name:
                    score += 20  # GPT-4o/Turbo have vision capabilities
                elif "claude-3" in model.name:
                    score += 15  # Claude 3 has vision
                elif "gemini" in model.name:
                    score += 12  # Gemini has multimodal capabilities
            
            # Speed optimization
            if analysis.get("speed", 0) > 0.7:
                score += model.speed_rating * analysis["speed"] * 2
                # Bonus for fast models on speed-critical tasks
                if model.speed_rating >= 9:
                    score += 10
            
            # Cost efficiency for simple tasks
            if analysis.get("simple_tasks", 0) > 0.6:
                if model.is_free:
                    score += 15  # Strong preference for free models on simple tasks
                else:
                    cost_efficiency = (1.0 / model.cost_per_token) * 0.2
                    score += cost_efficiency
            
            # Large context handling
            if analysis.get("large_context", 0) > 0.5:
                context_bonus = (model.context_length / 50000) * analysis["large_context"] * 5
                score += min(context_bonus, 20)  # Cap the bonus
            
            # Complex task handling
            if analysis.get("complex_tasks", 0) > 0.5:
                if not model.is_free:  # Premium models for complex tasks
                    score += 8
                if model.context_length > 50000:  # Large context helps with complexity
                    score += 5
            
            # File context bonuses
            if file_context:
                file_ext = file_context.get('extension', '').lower()
                if file_ext in ['.php', '.blade.php'] and "claude" in model.name:
                    score += 8  # Claude is excellent for PHP
                elif file_ext in ['.js', '.ts', '.vue'] and "gpt-4" in model.name:
                    score += 6  # GPT-4 is great for JavaScript
                elif file_ext in ['.css', '.scss'] and analysis.get("tall_stack", 0) > 0:
                    score += 5  # Any good model for TailwindCSS
            
            scores[model_name] = score
        
        # Return the model with the highest score
        best_model = max(scores.items(), key=lambda x: x[1])[0]
        
        # Enhanced logging with analysis insights
        analysis_summary = []
        for key, value in analysis.items():
            if value > 0.3:
                analysis_summary.append(f"{key}({value:.1f})")
        
        analysis_text = ", ".join(analysis_summary) if analysis_summary else "general"
        
        if todo_context:
            console.print(f"🎯 Selected [bold yellow]{best_model}[/bold yellow] for: [italic]{todo_context}[/italic]")
            console.print(f"   📊 Analysis: {analysis_text} | Score: {scores[best_model]:.1f}")
        else:
            console.print(f"🎯 Selected model: [bold yellow]{best_model}[/bold yellow] (score: {scores[best_model]:.1f})")
            console.print(f"   📊 Analysis: {analysis_text}")
        
        self.last_selected_model = best_model
        return best_model
    
    def get_development_context(self, project_path: str = None, files: List[str] = None) -> Dict:
        """Analyze development context from project structure and files"""
        context = {
            "project_type": "unknown",
            "technologies": [],
            "complexity": "medium",
            "file_types": [],
            "frameworks": [],
            "suggested_model_type": "general"
        }
        
        if not project_path and not files:
            return context
        
        # If we have files, analyze them
        if files:
            for file_path in files:
                file_ext = Path(file_path).suffix.lower()
                context["file_types"].append(file_ext)
                
                # Analyze file extension for technology
                if file_ext in ['.php', '.blade.php']:
                    context["technologies"].append("php")
                    context["frameworks"].append("laravel")
                    context["suggested_model_type"] = "tall_stack"
                elif file_ext in ['.js', '.jsx']:
                    context["technologies"].append("javascript")
                    if any('react' in f.lower() for f in files):
                        context["frameworks"].append("react")
                elif file_ext in ['.ts', '.tsx']:
                    context["technologies"].append("typescript")
                elif file_ext in ['.vue']:
                    context["technologies"].append("vue")
                    context["frameworks"].append("vue")
                elif file_ext in ['.py']:
                    context["technologies"].append("python")
                elif file_ext in ['.css', '.scss']:
                    context["technologies"].append("css")
                    if any('tailwind' in f.lower() for f in files):
                        context["frameworks"].append("tailwindcss")
        
        # If we have a project path, analyze structure
        if project_path and Path(project_path).exists():
            project_files = []
            for root, dirs, files_in_dir in os.walk(project_path):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'vendor', '.git', '__pycache__']]
                for file in files_in_dir[:50]:  # Limit analysis to first 50 files
                    project_files.append(file)
            
            # Detect TALL stack
            has_laravel = any('artisan' in f or 'composer.json' in f for f in project_files)
            has_tailwind = any('tailwind.config' in f for f in project_files)
            has_alpine = any('.js' in f for f in project_files)  # Simplified check
            has_livewire = has_laravel  # Assume Livewire if Laravel
            
            if has_laravel and has_tailwind:
                context["project_type"] = "tall_stack"
                context["suggested_model_type"] = "tall_stack"
                context["frameworks"] = ["laravel", "tailwindcss"]
                if has_alpine:
                    context["frameworks"].append("alpine")
                if has_livewire:
                    context["frameworks"].append("livewire")
            
            # Detect other project types
            elif any('package.json' in f for f in project_files):
                context["project_type"] = "javascript"
                if any('react' in f.lower() for f in project_files):
                    context["frameworks"].append("react")
                elif any('vue' in f.lower() for f in project_files):
                    context["frameworks"].append("vue")
                elif any('angular' in f.lower() for f in project_files):
                    context["frameworks"].append("angular")
            
            elif any('requirements.txt' in f or 'pyproject.toml' in f for f in project_files):
                context["project_type"] = "python"
                if any('django' in f.lower() for f in project_files):
                    context["frameworks"].append("django")
                elif any('flask' in f.lower() for f in project_files):
                    context["frameworks"].append("flask")
        
        # Determine complexity based on analysis
        if len(context["frameworks"]) > 2:
            context["complexity"] = "high"
        elif len(context["frameworks"]) > 0:
            context["complexity"] = "medium"
        else:
            context["complexity"] = "low"
        
        return context
    
    async def initialize_filesystem(self, project_path: str = None):
        """Initialize MCP filesystem server for file operations (legacy method)"""
        if not self.filesystem_initialized:
            success = await self.mcp_client.initialize_filesystem_server(project_path)
            self.filesystem_initialized = success
            return success
        return True
    
    async def initialize_all_servers(self, project_path: str = None):
        """Initialize all configured MCP servers for comprehensive tool access"""
        if not self.filesystem_initialized:
            success = await self.mcp_client.initialize_all_configured_servers(project_path)
            self.filesystem_initialized = success
            console.print(f"🚀 All MCP servers initialized: {success}")
            return success
        return True
    
    def _add_file_operation_instructions(self, prompt: str) -> str:
        """Add explicit file operation instructions to prompt when filesystem tools are available"""
        file_operation_context = """
🚨 CRITICAL: You have filesystem tools available and MUST use them for file operations.

🔧 AVAILABLE TOOLS (use these, don't just talk about them):
- read_file(path): Read file contents
- write_file(path, content): Write/update files 
- create_directory(path): Create directories
- list_directory(path): List directory contents

⚡ MANDATORY ACTIONS for file-related tasks:
- For "update README.md" → CALL write_file("README.md", content)
- For "read file" → CALL read_file(path)
- For "create file" → CALL write_file(path, content)
- For "analyze repository" → CALL list_directory(".") then read relevant files

❌ DO NOT:
- Display code examples like ```python write_file(...)```
- Suggest what should be done
- Show mock code blocks

✅ DO:
- Actually call the tools to perform file operations
- Use the tools immediately when file tasks are requested
- Perform real file modifications, not suggestions

🎯 EXAMPLE: If asked to "update README.md", you should:
1. CALL read_file("README.md") to see current content
2. CALL write_file("README.md", new_content) to update it
3. Confirm the file was actually modified

REMEMBER: You have real file system access - USE IT!
"""
        
        return f"{file_operation_context}\n\nUser Request: {prompt}"
    
    async def route_and_process(self, prompt: str, todo_context: str = None) -> str:
        """Route prompt to best model and process it"""
        # Enhance prompt with developer context if available
        enhanced_prompt = prompt
        if self.developer_context and not prompt.startswith("Based on this request:"):
            enhanced_prompt = f"{self.developer_context}\n\nUser request: {prompt}"
        
        # Try the best model first
        try:
            model_name = self.select_best_model(enhanced_prompt, todo_context)
            self.last_selected_model = model_name
            return await self._process_with_model(model_name, enhanced_prompt)
        except Exception as e:
            console.print(f"❌ Primary model failed: {str(e)}")
            
            # Try fallback models
            fallback_models = [name for name in self.models.keys() if name != model_name]
            for fallback_model in fallback_models:
                try:
                    console.print(f"🔄 Trying fallback model: {fallback_model}")
                    self.last_selected_model = fallback_model
                    return await self._process_with_model(fallback_model, enhanced_prompt)
                except Exception as fallback_error:
                    console.print(f"❌ Fallback model {fallback_model} failed: {str(fallback_error)}")
                    continue
            
            # If all models fail, return error
            console.print(f"❌ All models failed. Last error: {str(e)}")
            self.last_selected_model = "failed"
            return f"Error: All AI models are currently unavailable. Please check your API keys and try again."
    
    async def _process_with_model(self, model_name: str, prompt: str) -> str:
        """Process prompt with a specific model"""
        model = self.models[model_name]
        
        if model.provider == "openai":
            return await self._process_openai(model_name, prompt)
        elif model.provider == "anthropic":
            return await self._process_anthropic(model_name, prompt)
        elif model.provider == "google":
            return self._process_google(model_name, prompt)
        elif model.provider in ["xai", "deepseek", "mistral", "cohere", "perplexity"]:
            return self._process_placeholder_provider(model.provider, model_name, prompt)
        else:
            raise ValueError(f"Unsupported provider: {model.provider}")
    
    def _process_placeholder_provider(self, provider: str, model_name: str, prompt: str) -> str:
        """Handle providers that are configured but not yet fully implemented"""
        provider_info = {
            "xai": {
                "name": "xAI (Grok)",
                "api_docs": "https://docs.x.ai/api",
                "note": "xAI API implementation pending. Please check their documentation for the latest API details."
            },
            "deepseek": {
                "name": "DeepSeek",
                "api_docs": "https://platform.deepseek.com/docs",
                "note": "DeepSeek API implementation pending. Please check their documentation for the latest API details."
            },
            "mistral": {
                "name": "Mistral AI",
                "api_docs": "https://docs.mistral.ai/api/",
                "note": "Mistral API implementation pending. Please check their documentation for the latest API details."
            },
            "cohere": {
                "name": "Cohere",
                "api_docs": "https://docs.cohere.com/docs/the-cohere-platform",
                "note": "Cohere API implementation pending. Please check their documentation for the latest API details."
            },
            "perplexity": {
                "name": "Perplexity",
                "api_docs": "https://docs.perplexity.ai/",
                "note": "Perplexity API implementation pending. Please check their documentation for the latest API details."
            }
        }
        
        info = provider_info.get(provider, {
            "name": provider.title(),
            "api_docs": "N/A",
            "note": f"{provider} API implementation pending."
        })
        
        return f"""🚧 **{info['name']} Model Not Yet Implemented**

The model '{model_name}' from {info['name']} is configured but the API integration is not yet implemented.

**Next Steps:**
1. Check the provider's API documentation: {info['api_docs']}
2. The model configuration is saved and ready to use once implemented
3. Consider using an alternative model from OpenAI, Anthropic, or Google for now

**Your Prompt:** {prompt[:200]}{"..." if len(prompt) > 200 else ""}

**Note:** {info['note']}"""
    
    async def _process_openai(self, model_name: str, prompt: str) -> str:
        """Process prompt using OpenAI model with filesystem tools"""
        try:
            client = self.clients["openai"]
            
            # Enhance prompt with file operation instructions if filesystem is available
            enhanced_prompt = prompt
            if self.filesystem_initialized:
                enhanced_prompt = self._add_file_operation_instructions(prompt)
            
            # Prepare messages
            messages = [{"role": "user", "content": enhanced_prompt}]
            
            # Get all available tools for function calling
            tools = self.mcp_client.get_all_tools_for_openai()
            
            # Add tools to the request if available
            request_params = {
                'model': model_name,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 4000
            }
            
            if tools:
                request_params['tools'] = tools
                request_params['tool_choice'] = 'auto'
                console.print(f"🔧 OpenAI model has access to {len(tools)} tools for comprehensive analysis")
            
            # Create completion with or without tools
            response = client.chat.completions.create(**request_params)
            
            # Handle tool calls if tools were provided
            if tools:
                return await self._handle_openai_tool_calls(response, messages, client, model_name)
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "model" in error_msg.lower() and "not found" in error_msg.lower():
                raise ValueError(f"Model '{model_name}' not found or unavailable in OpenAI API")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                raise ValueError(f"Invalid OpenAI API key")
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                raise ValueError(f"Rate limit exceeded for OpenAI API")
            else:
                raise ValueError(f"OpenAI API error: {error_msg}")
    
    async def _handle_openai_tool_calls(self, response, messages, client, model_name):
        """Handle OpenAI tool calls for filesystem operations"""
        message = response.choices[0].message
        
        # If no tool calls, return the message content
        if not message.tool_calls:
            return message.content or "No response generated"
        
        # Add the assistant's message to conversation
        messages.append(message)
        
        # Process each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            console.print(f"🔧 Calling {function_name} with args: {function_args}")
            
            # Execute the filesystem operation via MCP
            try:
                console.print(f"🔍 DEBUG: Executing MCP tool {function_name} with args: {function_args}")
                result = await self.mcp_client.call_filesystem_tool(function_name, function_args)
                console.print(f"✅ {function_name} executed successfully - Result: {str(result)[:200]}")
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name, 
                    "content": str(result)
                })
                
            except Exception as e:
                error_result = f"Error executing {function_name}: {str(e)}"
                console.print(f"❌ {error_result}")
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool", 
                    "name": function_name,
                    "content": error_result
                })
        
        # Get final response after tool execution
        final_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        
        return final_response.choices[0].message.content
    
    async def _handle_anthropic_tool_calls(self, response, messages, client, model_name):
        """Handle Anthropic tool calls for filesystem operations"""
        # Check if the response contains tool use
        content_blocks = response.content
        
        # If no tool use, return the text content
        tool_use_blocks = [block for block in content_blocks if block.type == "tool_use"]
        if not tool_use_blocks:
            # Return text content if available
            text_blocks = [block for block in content_blocks if block.type == "text"]
            return text_blocks[0].text if text_blocks else "No response generated"
        
        # Add the assistant's message to conversation
        messages.append({"role": "assistant", "content": content_blocks})
        
        # Process each tool use block
        tool_results = []
        for tool_block in tool_use_blocks:
            function_name = tool_block.name
            function_args = tool_block.input
            
            console.print(f"🔧 Calling {function_name} with args: {function_args}")
            
            # Execute the MCP tool asynchronously
            try:
                # Use await instead of asyncio.run to prevent event loop conflicts
                result = await self.mcp_client.call_filesystem_tool(function_name, function_args)
                console.print(f"✅ {function_name} executed successfully - Result: {result}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result
                })
            except Exception as e:
                error_result = f"Error executing {function_name}: {str(e)}"
                console.print(f"❌ {error_result}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": error_result,
                    "is_error": True
                })
        
        # Add tool results to conversation
        messages.append({"role": "user", "content": tool_results})
        
        # Get final response after tool execution
        final_response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            messages=messages
        )
        
        # Return the text content from the final response
        text_blocks = [block for block in final_response.content if block.type == "text"]
        return text_blocks[0].text if text_blocks else "No response generated"
    
    async def cleanup(self):
        """Clean up MCP client resources"""
        if self.mcp_client:
            await self.mcp_client.cleanup()
            self.filesystem_initialized = False
    
    async def _process_anthropic(self, model_name: str, prompt: str) -> str:
        """Process prompt using Anthropic model with filesystem tools"""
        try:
            client = self.clients["anthropic"]
            
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Add filesystem tools if available
            tools = None
            if self.filesystem_initialized:
                tools = self.mcp_client.get_all_tools_for_anthropic()
                if tools:
                    console.print(f"🔧 Anthropic model has access to {len(tools)} tools for comprehensive analysis")
            
            # Create completion with or without tools
            if tools:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=4000,
                    messages=messages,
                    tools=tools
                )
                
                # Handle tool calls
                return await self._handle_anthropic_tool_calls(response, messages, client, model_name)
            else:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=4000,
                    messages=messages
                )
                
                return response.content[0].text
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found_error" in error_msg:
                raise ValueError(f"Model '{model_name}' not found or unavailable in Anthropic API")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                raise ValueError(f"Invalid Anthropic API key")
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                raise ValueError(f"Rate limit exceeded for Anthropic API")
            else:
                raise ValueError(f"Anthropic API error: {error_msg}")
    
    def _process_google(self, model_name: str, prompt: str) -> str:
        """Process prompt using Google Gemini model"""
        if not GOOGLE_AI_AVAILABLE:
            raise ValueError("Google Generative AI library not available. Please install google-generativeai.")
        
        try:
            client = self.clients["google"]
            model = client.GenerativeModel(model_name)
            
            # Enhance prompt with file operation instructions if filesystem is available
            enhanced_prompt = prompt
            if self.filesystem_initialized:
                enhanced_prompt = self._add_file_operation_instructions(prompt)
            
            response = model.generate_content(enhanced_prompt)
            
            if response.text:
                return response.text
            else:
                raise ValueError(f"No response text from Google model '{model_name}'")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                raise ValueError(f"Model '{model_name}' not found or unavailable in Google AI API")
            elif "401" in error_msg or "authentication" in error_msg.lower():
                raise ValueError(f"Invalid Google AI API key")
            elif "429" in error_msg or "quota" in error_msg.lower():
                raise ValueError(f"Rate limit or quota exceeded for Google AI API")
            else:
                raise ValueError(f"Google AI API error: {error_msg}")