"""
AI Router - Intelligent routing of prompts to the best AI model
"""

import asyncio
import json
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
                    strengths=["reasoning", "complex_tasks", "code_analysis", "multimodal", "general"],
                    context_length=128000,
                    cost_per_token=0.005,
                    speed_rating=8,
                    is_free=False
                ),
                "gpt-4o-mini": ModelCapability(
                    name="gpt-4o-mini",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks", "cost_effective"],
                    context_length=128000,
                    cost_per_token=0.0002,
                    speed_rating=9,
                    is_free=True  # Free tier available
                ),
                "gpt-4": ModelCapability(
                    name="gpt-4",
                    provider="openai",
                    strengths=["reasoning", "complex_tasks", "code_analysis", "general"],
                    context_length=8192,
                    cost_per_token=0.03,
                    speed_rating=6,
                    is_free=False
                ),
                "gpt-3.5-turbo": ModelCapability(
                    name="gpt-3.5-turbo",
                    provider="openai",
                    strengths=["speed", "general", "simple_tasks"],
                    context_length=4096,
                    cost_per_token=0.002,
                    speed_rating=9,
                    is_free=True  # Free tier available
                ),
                "gpt-4-turbo": ModelCapability(
                    name="gpt-4-turbo",
                    provider="openai",
                    strengths=["code", "reasoning", "large_context", "analysis"],
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
                    strengths=["reasoning", "creative", "complex_analysis", "code", "balanced"],
                    context_length=200000,
                    cost_per_token=0.003,
                    speed_rating=8,
                    is_free=False
                ),
                "claude-3-5-haiku-20241022": ModelCapability(
                    name="claude-3-5-haiku-20241022",
                    provider="anthropic",
                    strengths=["speed", "simple_tasks", "quick_answers"],
                    context_length=200000,
                    cost_per_token=0.00025,
                    speed_rating=10,
                    is_free=True  # Has free tier
                ),
                "claude-3-opus-20240229": ModelCapability(
                    name="claude-3-opus-20240229",
                    provider="anthropic",
                    strengths=["reasoning", "creative", "complex_analysis"],
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
                    strengths=["reasoning", "complex_tasks", "multimodal", "large_context", "analysis"],
                    context_length=2000000,  # 2M tokens
                    cost_per_token=0.0035,
                    speed_rating=7,
                    is_free=False
                ),
                "gemini-1.5-flash": ModelCapability(
                    name="gemini-1.5-flash",
                    provider="google",
                    strengths=["speed", "general", "multimodal", "balanced"],
                    context_length=1000000,  # 1M tokens
                    cost_per_token=0.00015,
                    speed_rating=9,
                    is_free=True  # Has free tier
                ),
                "gemini-1.0-pro": ModelCapability(
                    name="gemini-1.0-pro",
                    provider="google",
                    strengths=["general", "reasoning", "balanced"],
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
    
    def select_best_model(self, prompt: str, todo_context: str = None) -> str:
        """Select the best model for a given prompt with optional todo context"""
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
        
        # Show model selection with context
        if todo_context:
            console.print(f"🎯 Selected [bold yellow]{best_model}[/bold yellow] for: [italic]{todo_context}[/italic] (score: {scores[best_model]:.2f})")
        else:
            console.print(f"🎯 Selected model: {best_model} (score: {scores[best_model]:.2f})")
        return best_model
    
    def set_developer_context(self, context: str):
        """Set developer context for enhanced prompts"""
        self.developer_context = context
    
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