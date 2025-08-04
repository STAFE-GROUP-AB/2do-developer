#!/usr/bin/env python3
"""
Intent Router - Natural language intent detection for 2DO CLI
Determines user intent from natural language input and routes to appropriate actions
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class IntentMatch:
    """Represents a matched intent with confidence score"""
    intent: str
    confidence: float
    extracted_params: Dict = None

class IntentRouter:
    """Routes natural language input to appropriate 2DO actions"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        
    def _initialize_intent_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize patterns for different intents"""
        return {
            "add-todo": [
                {
                    "patterns": [
                        r"\b(add|create|new|make)\s+(todo|task|item)",
                        r"\b(todo|task).*?\b(add|create|new|make)",
                        r"i\s+(want|need)\s+to\s+(add|create|make)",
                        r"(create|add|make)\s+a\s+(new\s+)?(todo|task)",
                        r"(todo|task)\s+(for|about)",
                        r"remind\s+me\s+(to|about)",
                        r"need\s+to\s+(do|work\s+on|finish|complete)",
                        r"(fix|implement|work\s+on|debug|code|build|test|deploy)",
                        # SMART FILE MODIFICATION PATTERNS
                        r"(change|modify|update|edit|replace)\s+.*\s+(in|from)\s+\w+\.(\w+)",
                        r"(change|update|modify)\s+.*\s+(text|content|code)\s+in\s+\w+",
                        r"replace\s+.*\s+(with|to)\s+.*\s+in\s+\w+",
                        r"(add|insert|include)\s+.*\s+(to|in)\s+\w+\.(\w+)",
                        r"(remove|delete)\s+.*\s+(from|in)\s+\w+\.(\w+)",
                        r"(refactor|restructure|reorganize)\s+.*\s+in\s+\w+",
                        r"(create|add)\s+.*\s+(function|class|method|component)\s+in\s+\w+",
                        r"(fix|debug|solve)\s+.*\s+(bug|issue|error)\s+in\s+\w+",
                    ],
                    "confidence": 0.9
                },
                {
                    "patterns": [
                        r"\b(work|working)\s+on",
                        r"\b(issue|bug|feature|problem)",
                        r"\b(implement|development|coding)",
                    ],
                    "confidence": 0.7
                }
            ],
            "list-todos": [
                {
                    "patterns": [
                        r"\b(list|show|display|view)\s+(todos|tasks|items)",
                        r"(what|which)\s+(todos|tasks).*?(do\s+i\s+have|pending|outstanding)",
                        r"(show|tell)\s+me.*?(todos|tasks|items)",
                        r"(what\s+)?(am\s+i\s+)?(supposed\s+to\s+)?(working\s+on|doing)",
                        r"(current|pending|active)\s+(todos|tasks|work)",
                        r"what\s+(should|can)\s+i\s+(work\s+on|do)",
                        r"todo\s+(list|status)",
                        r"(my\s+)?(todos|tasks|work|items)",
                    ],
                    "confidence": 0.95
                }
            ],
            "create-subtasks": [
                {
                    "patterns": [
                        r"(break\s+down|split|divide)\s+.*(todo|task)",
                        r"(sub|smaller)\s+(todos|tasks)",
                        r"(create|make)\s+(sub|child)\s+(todos|tasks)",
                        r"(todo|task).*?(break|split|divide|smaller)",
                        r"(organize|structure)\s+.*(todo|task)",
                    ],
                    "confidence": 0.9
                }
            ],
            "multitask": [
                {
                    "patterns": [
                        r"(start|begin|run)\s+(multitask|multi.task|parallel)",
                        r"(process|work\s+on)\s+(all|multiple)\s+(todos|tasks)",
                        r"(batch|bulk)\s+(process|execute|run)",
                        r"(do|execute|run)\s+(everything|all\s+todos|all\s+tasks)",
                        r"multitask\s+on\s+(all|my|pending)",
                        r"run.*multitask",
                        r"process.*all.*pending",
                    ],
                    "confidence": 0.9
                }
            ],
            "run-all": [
                {
                    "patterns": [
                        r"\b(run|start|execute)\s+all\b",
                        r"\b(do|work\s+on)\s+everything\b",
                        r"\b(run|start)\s+(all\s+)?(todos|tasks)\b",
                        r"\b(execute|process)\s+(all|everything)\b",
                        r"\ball\s+(todos|tasks)\s+(now|start)\b",
                        r"\bmultitask\s+all\b",
                        r"\brun\s+all\s+(pending|active)\b",
                        r"\bstart\s+working\s+on\s+everything\b",
                    ],
                    "confidence": 0.95
                }
            ],
            "create-github-issue": [
                {
                    "patterns": [
                        r"(create|make|new)\s+.*(github|git)\s+(issue|bug|feature)",
                        r"(report|file|submit)\s+.*(issue|bug)",
                        r"github\s+.*(create|new|add)",
                        r"(issue|bug|feature)\s+.*(github|git|repo|repository)",
                    ],
                    "confidence": 0.95  # Higher confidence than github-issues
                }
            ],
            "github-issues": [
                {
                    "patterns": [
                        r"github\s+(issues|issue)(?!\s+(create|new|add))",  # Negative lookahead for create commands
                        r"(show|list|view)\s+.*(github|git)\s+(issues|issue)",
                        r"(work\s+on|fix|handle)\s+.*(github|git)\s+(issues|issue)",
                        r"(repository|repo)\s+(issues|issue)",
                        r"(sync|import)\s+.*(github|git)",
                    ],
                    "confidence": 0.9  # Lower than create-github-issue
                }
            ],
            "export-todos-to-github": [
                {
                    "patterns": [
                        r"(export|sync|push|send)\s+.*(todos|tasks)\s+.*(github|git)",
                        r"github\s+.*(export|sync|push|send)",
                        r"(create|make)\s+.*(github|git)\s+.*(todos|tasks|from)",
                    ],
                    "confidence": 0.9
                }
            ],
            "parse-markdown": [
                {
                    "patterns": [
                        r"(parse|read|import)\s+.*(markdown|md)",
                        r"markdown\s+.*(parse|read|import|tasks|todos)",
                        r"(load|import)\s+.*(tasks|todos)\s+.*(file|markdown|md)",
                        r"\.md\s+(file|tasks|todos)",
                    ],
                    "confidence": 0.9
                }
            ],
            "browser-integration": [
                {
                    "patterns": [
                        r"(start|open|launch)\s+.*(browser|web)",
                        r"browser\s+.*(start|open|integration|mode)",
                        r"(web|browser)\s+.*(development|dev|server)",
                        r"(refresh|reload)\s+.*(browser|web|page)",
                    ],
                    "confidence": 0.9
                }
            ],
            "remove-todo": [
                {
                    "patterns": [
                        r"(remove|delete|del)\s+(todo|task|item)",
                        r"(todo|task)\s+.*(remove|delete|del)",
                        r"(get\s+rid\s+of|eliminate)\s+.*(todo|task)",
                        r"(remove|delete)\s+.*(by\s+id|specific)",
                        r"(cancel|drop)\s+.*(todo|task)",
                    ],
                    "confidence": 0.9
                }
            ],
            "remove-completed-todos": [
                {
                    "patterns": [
                        r"(remove|delete|clear)\s+.*(completed|done|finished)\s+.*(todos|tasks)",
                        r"(clean\s+up|cleanup)\s+.*(completed|done|finished)",
                        r"(clear|remove|delete)\s+.*(all\s+)?(completed|done|finished)",
                        r"(completed|done|finished)\s+.*(remove|delete|clear|cleanup)",
                        r"(bulk\s+)?(delete|remove)\s+.*(completed|done)",
                        r"(archive|cleanup)\s+.*(todos|tasks)",
                    ],
                    "confidence": 0.95
                }
            ],
            "mcp-management": [
                {
                    "patterns": [
                        r"mcp\s+(server|servers|manage|management)",
                        r"(manage|configure|setup)\s+.*(mcp|servers)",
                        r"(model\s+context\s+protocol|mcp)",
                    ],
                    "confidence": 0.95
                }
            ],
            "chat": [
                {
                    "patterns": [
                        r"(help|assist|support)\s+.*(code|coding|development|programming)",
                        r"(explain|tell\s+me\s+about|how\s+to)",
                        r"(what\s+is|what\s+are|how\s+does)",
                        r"(advice|suggestion|recommend|guidance)",
                        r"(chat|talk|discuss)",
                        r"(question|ask|wonder)",
                    ],
                    "confidence": 0.6
                }
            ],
            "quit": [
                {
                    "patterns": [
                        r"^(quit|exit|bye|goodbye|done|finish|stop|end)$",
                        r"(i.m\s+done|that.s\s+all|nothing\s+else)",
                        r"(see\s+you|talk\s+later|catch\s+you\s+later)",
                    ],
                    "confidence": 0.95
                }
            ]
        }
    
    def analyze_intent(self, user_input: str) -> IntentMatch:
        """Analyze user input and determine the most likely intent"""
        if not user_input or not user_input.strip():
            return IntentMatch("add-todo", 0.5)  # Default to adding todo
        
        user_input_lower = user_input.lower().strip()
        
        # Track all matches with confidence scores
        matches = []
        
        for intent_name, pattern_groups in self.intent_patterns.items():
            for pattern_group in pattern_groups:
                for pattern in pattern_group["patterns"]:
                    if re.search(pattern, user_input_lower):
                        confidence = pattern_group["confidence"]
                        
                        # Boost confidence for exact matches or high-specificity patterns
                        if len(re.findall(pattern, user_input_lower)) > 1:
                            confidence += 0.05
                        
                        # Special boost for specific keywords
                        if intent_name == "multitask" and "multitask" in user_input_lower:
                            confidence += 0.1
                        elif intent_name == "create-github-issue" and "create" in user_input_lower and "github" in user_input_lower:
                            confidence += 0.05
                        
                        # Extract potential parameters (like todo titles, issue numbers, etc.)
                        extracted_params = self._extract_parameters(user_input, intent_name, pattern)
                        
                        matches.append(IntentMatch(
                            intent=intent_name,
                            confidence=confidence,
                            extracted_params=extracted_params
                        ))
        
        if not matches:
            # If no specific pattern matched, determine based on general keywords
            return self._fallback_intent_detection(user_input_lower)
        
        # Return the match with highest confidence, with tie-breaking by specificity
        best_match = max(matches, key=lambda x: (x.confidence, len(x.intent)))
        return best_match
    
    def _extract_parameters(self, user_input: str, intent: str, pattern: str) -> Dict:
        """Extract relevant parameters from user input based on intent"""
        params = {}
        
        if intent == "add-todo":
            # Try to extract a potential todo title
            todo_patterns = [
                r"(?:add|create|make|new)\s+(?:todo|task)\s+(?:for|about|to)\s+(.+?)(?:\.|$|,|\?|!)",
                r"(?:todo|task):\s*(.+?)(?:\.|$|,|\?|!)",
                r"(?:need\s+to|should|must)\s+(.+?)(?:\.|$|,|\?|!)",
                r"(?:fix|implement|work\s+on|debug|code|build|test|deploy)\s+(.+?)(?:\.|$|,|\?|!)",
                r"remind\s+me\s+to\s+(.+?)(?:\.|$|,|\?|!)",
            ]
            
            for todo_pattern in todo_patterns:
                match = re.search(todo_pattern, user_input, re.IGNORECASE)
                if match:
                    params["suggested_title"] = match.group(1).strip()
                    break
        
        elif intent == "create-github-issue":
            # Extract potential issue title
            issue_patterns = [
                r"(?:create|make|new)\s+(?:github\s+)?(?:issue|bug|feature)\s+(?:for|about)\s+(.+?)(?:\.|$|,|\?|!)",
                r"(?:report|file)\s+(?:issue|bug)\s+(.+?)(?:\.|$|,|\?|!)",
            ]
            
            for issue_pattern in issue_patterns:
                match = re.search(issue_pattern, user_input, re.IGNORECASE)
                if match:
                    params["suggested_title"] = match.group(1).strip()
                    break
        
        return params
    
    def _fallback_intent_detection(self, user_input_lower: str) -> IntentMatch:
        """Fallback intent detection for general cases"""
        # Check for common developer keywords
        dev_keywords = ["code", "debug", "fix", "implement", "build", "test", "feature", "bug", "issue"]
        github_keywords = ["github", "git", "repository", "repo", "commit", "pull", "push"]
        
        if any(keyword in user_input_lower for keyword in github_keywords):
            return IntentMatch("github-issues", 0.6)
        elif any(keyword in user_input_lower for keyword in dev_keywords):
            return IntentMatch("add-todo", 0.7)  # Developer tasks default to todos
        elif any(word in user_input_lower for word in ["what", "how", "why", "explain", "help"]):
            return IntentMatch("chat", 0.8)
        else:
            # Default to adding a todo - most common developer action
            return IntentMatch("add-todo", 0.5)
    
    def get_friendly_confirmation(self, intent: str, extracted_params: Dict = None) -> str:
        """Get a friendly confirmation message for the detected intent"""
        messages = {
            "add-todo": [
                "🎯 I'll help you add a new todo!",
                "✨ Let's create a new task for you!",
                "📝 Time to add another item to your todo list!",
                "🚀 Ready to capture that new task!",
            ],
            "list-todos": [
                "📋 Let me show you what's on your plate!",
                "👀 Here's what you're working on...",
                "📊 Time to check your current workload!",
                "🔍 Let's see what tasks are waiting for you!",
            ],
            "create-subtasks": [
                "🔨 Let's break that big task into smaller pieces!",
                "🧩 Time to make that complex todo more manageable!",
                "📏 I'll help you organize that task better!",
            ],
            "multitask": [
                "🚀 Time to get productive! Let's multitask!",
                "⚡ Ready to tackle multiple todos at once!",
                "🎯 Multitasking mode activated - let's do this!",
                "💪 Time to show those todos who's boss!",
            ],
            "run-all": [
                "🔥 ALL SYSTEMS GO! Running everything at once!",
                "⚡ FULL POWER MODE! Let's crush all your todos!",
                "🚀 MAXIMUM PRODUCTIVITY! Processing all tasks now!",
                "💥 BEAST MODE ACTIVATED! All todos starting now!",
                "🎯 THE ULTIMATE SHORTCUT! Everything runs now!",
            ],
            "github-issues": [
                "🐙 Let's check what's happening on GitHub!",
                "📋 Time to sync with your repository issues!",
                "🔍 Diving into your GitHub issues...",
            ],
            "create-github-issue": [
                "🐛 Let's report that issue to GitHub!",
                "📝 I'll help you create a new GitHub issue!",
                "🎯 Time to document that problem properly!",
            ],
            "export-todos-to-github": [
                "📤 Let's get those todos synced to GitHub!",
                "🔄 Time to export your work to GitHub issues!",
                "🚀 Moving your todos to GitHub for better tracking!",
            ],
            "parse-markdown": [
                "📖 Let me parse those markdown files for tasks!",
                "🔍 Scanning for todos in your markdown files...",
                "📋 Extracting tasks from your documentation!",
            ],
            "browser-integration": [
                "🌐 Setting up browser integration for you!",
                "⚡ Getting your dev environment ready!",
                "🚀 Browser mode activated!",
            ],
            "remove-todo": [
                "🗑️ I'll help you remove that todo!",
                "✂️ Time to clean up your task list!",
                "🧹 Let's get rid of that todo for you!",
                "❌ Ready to delete that task!",
            ],
            "remove-completed-todos": [
                "🧽 Time for some spring cleaning!",
                "✨ Let's clear out those completed tasks!",
                "🗂️ I'll help you archive the finished work!",
                "🎉 Ready to celebrate by cleaning up completed todos!",
            ],
            "mcp-management": [
                "🔌 Let's manage your MCP servers!",
                "⚙️ Time to configure those development tools!",
                "🛠️ Setting up your development environment!",
            ],
            "chat": [
                "💬 I'm here to help with whatever you need!",
                "🤖 Ready to assist you with development questions!",
                "💡 What's on your mind? Let's figure it out together!",
                "🎯 I'm your friendly coding companion - what can I help with?",
            ],
            "quit": [
                "👋 Catch you later! Happy coding!",
                "🚀 Until next time - keep building awesome things!",
                "✨ See you soon! Go make something amazing!",
            ]
        }
        
        intent_messages = messages.get(intent, ["Let's get this done!"])
        import random
        message = random.choice(intent_messages)
        
        # Add parameter-specific details if available
        if extracted_params and "suggested_title" in extracted_params:
            if intent == "add-todo":
                message += f" I see you want to work on: '{extracted_params['suggested_title']}'"
            elif intent == "create-github-issue":
                message += f" About: '{extracted_params['suggested_title']}'"
        
        return message
    
    def get_developer_context_prompt(self) -> str:
        """Get context for the AI to be developer-focused and friendly"""
        return """You are 2DO's AI assistant - the friendliest, most helpful developer companion ever created. 

Key personality traits:
- You're a passionate developer who loves helping other developers be more productive
- You're polite, encouraging, and sometimes add a touch of humor to keep things light
- You understand the developer workflow and can relate to coding challenges
- You're never racist, mean, or unhelpful - always supportive and positive
- You make developers feel like they have the best coding buddy ever

Your primary role is to help developers:
- Manage their todos and tasks efficiently
- Stay organized with their development work
- Navigate GitHub issues and project management
- Code faster and smarter
- Feel motivated and supported in their development journey

Always respond with enthusiasm and expertise, like a senior developer mentor who genuinely cares about helping others succeed."""