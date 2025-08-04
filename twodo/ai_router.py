"""
AI Router - Intelligent routing of prompts to the best AI model
"""

import asyncio
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import openai
import anthropic
from rich.console import Console

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

class AIRouter:
    """Routes prompts to the most suitable AI model"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.models = self._initialize_models()
        self._setup_clients()
        self.last_selected_model = None
    
    def _initialize_models(self) -> Dict[str, ModelCapability]:
        """Initialize available models with their capabilities"""
        models = {}
        
        # OpenAI models
        if self.config.get_api_key("openai"):
            models.update({
                "gpt-4o": ModelCapability(
                    name="gpt-4o",
                    provider="openai",
                    strengths=["reasoning", "complex_tasks", "code_analysis", "multimodal", "general"],
                    context_length=128000,
                    cost_per_token=0.005,
                    speed_rating=8
                ),
                "gpt-4o-mini": ModelCapability(
                    name="gpt-4o-mini",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks", "cost_effective"],
                    context_length=128000,
                    cost_per_token=0.0002,
                    speed_rating=9
                ),
                "gpt-4": ModelCapability(
                    name="gpt-4",
                    provider="openai",
                    strengths=["reasoning", "complex_tasks", "code_analysis", "general"],
                    context_length=8192,
                    cost_per_token=0.03,
                    speed_rating=6
                ),
                "gpt-3.5-turbo": ModelCapability(
                    name="gpt-3.5-turbo",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks"],
                    context_length=4096,
                    cost_per_token=0.002,
                    speed_rating=9
                ),
                "gpt-4-turbo": ModelCapability(
                    name="gpt-4-turbo",
                    provider="openai",
                    strengths=["code", "reasoning", "large_context", "analysis"],
                    context_length=128000,
                    cost_per_token=0.01,
                    speed_rating=7
                )
            })
        
        # Anthropic models
        if self.config.get_api_key("anthropic"):
            models.update({
                "claude-opus-4-20250514": ModelCapability(
                    name="claude-opus-4-20250514",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis", "research", "writing"],
                    context_length=200000,
                    cost_per_token=0.015,
                    speed_rating=6
                ),
                "claude-sonnet-4-20250514": ModelCapability(
                    name="claude-sonnet-4-20250514",
                    provider="anthropic",
                    strengths=["reasoning", "code", "balanced", "general", "analysis"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8
                ),
                "claude-3-7-sonnet-20250219": ModelCapability(
                    name="claude-3-7-sonnet-20250219",
                    provider="anthropic",
                    strengths=["reasoning", "code", "balanced", "general"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8
                ),
                "claude-3-5-sonnet-20241022": ModelCapability(
                    name="claude-3-5-sonnet-20241022",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis", "code", "balanced"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8
                ),
                "claude-3-5-haiku-20241022": ModelCapability(
                    name="claude-3-5-haiku-20241022",
                    provider="anthropic",
                    strengths=["speed", "simple_tasks", "quick_answers"],
                    context_length=200000,
                    cost_per_token=0.00025,
                    speed_rating=10
                ),
                "claude-3-opus-20240229": ModelCapability(
                    name="claude-3-opus-20240229",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis"],
                    context_length=200000,
                    cost_per_token=0.015,
                    speed_rating=5
                )
            })
        
        # Google Gemini models
        if GOOGLE_AI_AVAILABLE and self.config.get_api_key("google"):
            models.update({
                "gemini-1.5-pro": ModelCapability(
                    name="gemini-1.5-pro",
                    provider="google",
                    strengths=["reasoning", "complex_tasks", "multimodal", "large_context", "analysis"],
                    context_length=2000000,  # 2M tokens
                    cost_per_token=0.0035,
                    speed_rating=7
                ),
                "gemini-1.5-flash": ModelCapability(
                    name="gemini-1.5-flash",
                    provider="google",
                    strengths=["speed", "general", "multimodal", "balanced"],
                    context_length=1000000,  # 1M tokens
                    cost_per_token=0.00015,
                    speed_rating=9
                ),
                "gemini-1.0-pro": ModelCapability(
                    name="gemini-1.0-pro",
                    provider="google",
                    strengths=["general", "reasoning", "balanced"],
                    context_length=32000,
                    cost_per_token=0.0005,
                    speed_rating=8
                )
            })
        
        return models
    
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
    
    def analyze_prompt(self, prompt: str) -> Dict[str, float]:
        """Analyze prompt to determine task type and requirements"""
        prompt_lower = prompt.lower()
        
        analysis = {
            "code": 0.0,
            "reasoning": 0.0,
            "creative": 0.0,
            "speed": 0.0,
            "analysis": 0.0,
            "simple_tasks": 0.0,
            "complex_tasks": 0.0,
            "large_context": 0.0
        }
        
        # Code-related keywords
        code_keywords = ['code', 'programming', 'function', 'class', 'debug', 'script', 'algorithm', 'git', 'repository']
        if any(keyword in prompt_lower for keyword in code_keywords):
            analysis["code"] += 0.8
        
        # Reasoning keywords
        reasoning_keywords = ['analyze', 'explain', 'why', 'how', 'compare', 'evaluate', 'reason', 'logic']
        if any(keyword in prompt_lower for keyword in reasoning_keywords):
            analysis["reasoning"] += 0.7
        
        # Creative keywords
        creative_keywords = ['create', 'write', 'story', 'creative', 'generate', 'design', 'idea']
        if any(keyword in prompt_lower for keyword in creative_keywords):
            analysis["creative"] += 0.6
        
        # Speed indicators
        speed_keywords = ['quick', 'fast', 'simple', 'brief', 'short']
        if any(keyword in prompt_lower for keyword in speed_keywords):
            analysis["speed"] += 0.9
        
        # Complex task indicators
        complex_keywords = ['complex', 'detailed', 'comprehensive', 'thorough', 'deep']
        if any(keyword in prompt_lower for keyword in complex_keywords):
            analysis["complex_tasks"] += 0.8
        
        # Length-based analysis
        if len(prompt) < 100:
            analysis["simple_tasks"] += 0.5
            analysis["speed"] += 0.3
        elif len(prompt) > 1000:
            analysis["large_context"] += 0.7
            analysis["complex_tasks"] += 0.4
        
        return analysis
    
    def select_best_model(self, prompt: str) -> str:
        """Select the best model for a given prompt"""
        if not self.models:
            raise ValueError("No AI models configured. Please run setup first.")
        
        analysis = self.analyze_prompt(prompt)
        scores = {}
        
        for model_name, model in self.models.items():
            score = 0.0
            
            # Score based on model strengths and prompt analysis
            for strength in model.strengths:
                if strength in analysis:
                    score += analysis[strength] * 10
            
            # Adjust for speed if speed is important
            if analysis.get("speed", 0) > 0.5:
                score += model.speed_rating * analysis["speed"]
            
            # Adjust for cost efficiency (prefer cheaper models for simple tasks)
            if analysis.get("simple_tasks", 0) > 0.5:
                score += (1.0 / model.cost_per_token) * 0.1
            
            # Adjust for context length requirements
            if analysis.get("large_context", 0) > 0.5:
                score += (model.context_length / 10000) * analysis["large_context"]
            
            scores[model_name] = score
        
        # Return the model with the highest score
        best_model = max(scores.items(), key=lambda x: x[1])[0]
        console.print(f"🎯 Selected model: {best_model} (score: {scores[best_model]:.2f})")
        return best_model
    
    def route_and_process(self, prompt: str) -> str:
        """Route prompt to best model and process it"""
        # Try the best model first
        try:
            model_name = self.select_best_model(prompt)
            self.last_selected_model = model_name
            return self._process_with_model(model_name, prompt)
        except Exception as e:
            console.print(f"❌ Primary model failed: {str(e)}")
            
            # Try fallback models
            fallback_models = [name for name in self.models.keys() if name != model_name]
            for fallback_model in fallback_models:
                try:
                    console.print(f"🔄 Trying fallback model: {fallback_model}")
                    self.last_selected_model = fallback_model
                    return self._process_with_model(fallback_model, prompt)
                except Exception as fallback_error:
                    console.print(f"❌ Fallback model {fallback_model} failed: {str(fallback_error)}")
                    continue
            
            # If all models fail, return error
            console.print(f"❌ All models failed. Last error: {str(e)}")
            self.last_selected_model = "failed"
            return f"Error: All AI models are currently unavailable. Please check your API keys and try again."
    
    def _process_with_model(self, model_name: str, prompt: str) -> str:
        """Process prompt with a specific model"""
        model = self.models[model_name]
        
        if model.provider == "openai":
            return self._process_openai(model_name, prompt)
        elif model.provider == "anthropic":
            return self._process_anthropic(model_name, prompt)
        elif model.provider == "google":
            return self._process_google(model_name, prompt)
        else:
            raise ValueError(f"Unsupported provider: {model.provider}")
    
    def _process_openai(self, model_name: str, prompt: str) -> str:
        """Process prompt using OpenAI model"""
        try:
            client = self.clients["openai"]
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
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
    
    def _process_anthropic(self, model_name: str, prompt: str) -> str:
        """Process prompt using Anthropic model"""
        try:
            client = self.clients["anthropic"]
            
            response = client.messages.create(
                model=model_name,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
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
            
            response = model.generate_content(prompt)
            
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