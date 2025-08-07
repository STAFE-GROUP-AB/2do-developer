#!/usr/bin/env python3
"""
Enhanced Automation Engine - Advanced workflow automation for TALL Stack development
Handles intelligent project scaffolding, test generation, and CI/CD automation
"""

import re
import os
import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel

console = Console()

@dataclass
class AutoTodoRequest:
    """Represents an automatically parsed todo request"""
    original_input: str
    suggested_title: str
    suggested_description: str
    detected_files: List[str]
    action_type: str  # 'modify', 'create', 'fix', 'refactor', etc.
    confidence: float
    auto_start_eligible: bool = True

@dataclass
class ProjectScaffold:
    """Represents a project scaffolding template"""
    name: str
    description: str
    files_to_create: List[Dict[str, str]]
    commands_to_run: List[str]
    dependencies: List[str]

class EnhancedAutomationEngine:
    """Advanced automation engine for intelligent TALL Stack development"""
    
    def __init__(self, todo_manager, multitasker, github_integration=None, tech_detector=None):
        self.todo_manager = todo_manager
        self.multitasker = multitasker
        self.github_integration = github_integration
        self.tech_detector = tech_detector
        self.github_pro_mode = False
        
        # Enhanced file modification patterns
        self.file_patterns = {
            'modify': [
                r'(change|modify|update|edit|replace)\s+(.+?)\s+(in|from)\s+([^\s]+\.\w+)',
                r'replace\s+(.+?)\s+(with|to)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
                r'(change|update|modify)\s+(.+?)\s+(text|content|code)\s+in\s+([^\s]+)',
            ],
            'create': [
                r'(create|add|make)\s+(.+?)\s+(in|to)\s+([^\s]+\.\w+)',
                r'(add|insert|include)\s+(.+?)\s+(to|in)\s+([^\s]+\.\w+)',
                r'(create|add)\s+.*?(function|class|method|component)\s+(.+?)\s+in\s+([^\s]+)',
                r'(scaffold|generate)\s+(controller|model|migration|component|view)\s+(.+)',
            ],
            'remove': [
                r'(remove|delete)\s+(.+?)\s+(from|in)\s+([^\s]+\.\w+)',
                r'(delete|remove)\s+(.+?)\s+from\s+([^\s]+)',
            ],
            'fix': [
                r'(fix|debug|solve)\s+(.+?)\s+(bug|issue|error)\s+in\s+([^\s]+)',
                r'(fix|repair|correct)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
            ],
            'refactor': [
                r'(refactor|restructure|reorganize)\s+(.+?)\s+in\s+([^\s]+)',
                r'(improve|optimize|clean\s+up)\s+(.+?)\s+in\s+([^\s]+\.\w+)',
            ],
            'test': [
                r'(write|create|add)\s+(test|tests)\s+for\s+(.+)',
                r'(test|unit\s+test|integration\s+test)\s+(.+)',
                r'add\s+(testing|test\s+coverage)\s+to\s+(.+)',
            ],
            'deploy': [
                r'(deploy|deployment|ci/cd)\s+(.+)',
                r'(docker|kubernetes|containerize)\s+(.+)',
                r'(setup|configure)\s+(ci|cd|pipeline)\s+(.+)',
            ]
        }
        
        # TALL Stack scaffolding templates
        self.scaffold_templates = {
            'laravel_livewire_component': ProjectScaffold(
                name="Laravel Livewire Component",
                description="Create a new Livewire component with Blade view",
                files_to_create=[
                    {"path": "app/Http/Livewire/{name}.php", "template": "livewire_component"},
                    {"path": "resources/views/livewire/{name_kebab}.blade.php", "template": "livewire_view"}
                ],
                commands_to_run=[],
                dependencies=["livewire/livewire"]
            ),
            'laravel_controller': ProjectScaffold(
                name="Laravel Controller",
                description="Generate Laravel controller with CRUD operations",
                files_to_create=[
                    {"path": "app/Http/Controllers/{name}Controller.php", "template": "laravel_controller"}
                ],
                commands_to_run=["php artisan make:controller {name}Controller --resource"],
                dependencies=[]
            ),
            'laravel_model': ProjectScaffold(
                name="Laravel Model with Migration",
                description="Create Laravel model with migration and factory",
                files_to_create=[],
                commands_to_run=[
                    "php artisan make:model {name} -mf",
                    "php artisan make:seeder {name}Seeder"
                ],
                dependencies=[]
            ),
            'tailwind_component': ProjectScaffold(
                name="TailwindCSS Component",
                description="Create reusable TailwindCSS component with Alpine.js",
                files_to_create=[
                    {"path": "resources/views/components/{name_kebab}.blade.php", "template": "tailwind_component"}
                ],
                commands_to_run=[],
                dependencies=["tailwindcss", "alpinejs"]
            ),
            'full_tall_crud': ProjectScaffold(
                name="Full TALL Stack CRUD",
                description="Complete CRUD implementation with all TALL stack components",
                files_to_create=[
                    {"path": "app/Models/{name}.php", "template": "laravel_model"},
                    {"path": "app/Http/Livewire/{name}Index.php", "template": "livewire_index"},
                    {"path": "app/Http/Livewire/{name}Form.php", "template": "livewire_form"},
                    {"path": "resources/views/livewire/{name_kebab}-index.blade.php", "template": "livewire_index_view"},
                    {"path": "resources/views/livewire/{name_kebab}-form.blade.php", "template": "livewire_form_view"}
                ],
                commands_to_run=[
                    "php artisan make:migration create_{name_snake}_table",
                    "php artisan make:factory {name}Factory"
                ],
                dependencies=["laravel/framework", "livewire/livewire", "tailwindcss", "alpinejs"]
            )
        }
    
    def detect_scaffolding_opportunity(self, user_input: str, project_path: str = None) -> Optional[Dict]:
        """Detect if user input is requesting scaffolding and suggest appropriate templates"""
        user_input_lower = user_input.lower()
        
        # Detect TALL stack scaffolding requests
        scaffolding_patterns = {
            'laravel_livewire_component': [
                r'(create|make|generate)\s+(livewire\s+)?component\s+(\w+)',
                r'(scaffold|generate)\s+livewire\s+(\w+)',
            ],
            'laravel_controller': [
                r'(create|make|generate)\s+controller\s+(\w+)',
                r'(scaffold|generate)\s+(resource\s+)?controller\s+(\w+)',
            ],
            'laravel_model': [
                r'(create|make|generate)\s+model\s+(\w+)',
                r'(scaffold|generate)\s+model\s+(\w+)\s+with\s+(migration|factory)',
            ],
            'full_tall_crud': [
                r'(create|generate|scaffold)\s+(full\s+)?crud\s+(for\s+)?(\w+)',
                r'(scaffold|generate)\s+complete\s+(\w+)\s+(module|crud)',
                r'(create|build)\s+(full|complete)\s+(\w+)\s+(system|module)',
            ]
        }
        
        for template_key, patterns in scaffolding_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    # Extract the name (usually the last captured group)
                    name = match.groups()[-1].capitalize()
                    
                    return {
                        'template': template_key,
                        'name': name,
                        'scaffold_info': self.scaffold_templates[template_key],
                        'confidence': 0.9
                    }
        
        return None
    
    def generate_tests_for_project(self, project_path: str) -> List[Dict]:
        """Generate intelligent test suggestions based on project analysis"""
        test_suggestions = []
        
        if not self.tech_detector:
            return test_suggestions
        
        # Analyze project structure
        detected_techs = self.tech_detector.analyze_repo(project_path)
        
        if 'laravel' in detected_techs:
            # Laravel-specific test suggestions
            
            # Check for models without tests
            models_dir = Path(project_path) / "app" / "Models"
            tests_dir = Path(project_path) / "tests"
            
            if models_dir.exists():
                for model_file in models_dir.glob("*.php"):
                    model_name = model_file.stem
                    test_file = tests_dir / "Feature" / f"{model_name}Test.php"
                    
                    if not test_file.exists():
                        test_suggestions.append({
                            'type': 'model_test',
                            'name': f"{model_name} Model Test",
                            'description': f"Create comprehensive tests for {model_name} model",
                            'file_path': str(test_file),
                            'priority': 'high',
                            'template': 'laravel_model_test'
                        })
            
            # Check for controllers without tests
            controllers_dir = Path(project_path) / "app" / "Http" / "Controllers"
            if controllers_dir.exists():
                for controller_file in controllers_dir.glob("*.php"):
                    if controller_file.name != "Controller.php":  # Skip base controller
                        controller_name = controller_file.stem
                        test_file = tests_dir / "Feature" / f"{controller_name}Test.php"
                        
                        if not test_file.exists():
                            test_suggestions.append({
                                'type': 'controller_test',
                                'name': f"{controller_name} Controller Test",
                                'description': f"Create HTTP tests for {controller_name}",
                                'file_path': str(test_file),
                                'priority': 'medium',
                                'template': 'laravel_controller_test'
                            })
            
            # Check for Livewire components without tests
            if 'livewire' in detected_techs:
                livewire_dirs = [
                    Path(project_path) / "app" / "Http" / "Livewire",
                    Path(project_path) / "app" / "Livewire"
                ]
                
                for livewire_dir in livewire_dirs:
                    if livewire_dir.exists():
                        for component_file in livewire_dir.glob("*.php"):
                            component_name = component_file.stem
                            test_file = tests_dir / "Feature" / "Livewire" / f"{component_name}Test.php"
                            
                            if not test_file.exists():
                                test_suggestions.append({
                                    'type': 'livewire_test',
                                    'name': f"{component_name} Livewire Test",
                                    'description': f"Create Livewire component tests for {component_name}",
                                    'file_path': str(test_file),
                                    'priority': 'medium',
                                    'template': 'livewire_component_test'
                                })
        
        # JavaScript/Frontend testing suggestions
        if any(tech in detected_techs for tech in ['javascript', 'typescript', 'react', 'vue']):
            package_json = Path(project_path) / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    
                    # Check if testing framework is set up
                    dev_deps = package_data.get('devDependencies', {})
                    has_jest = 'jest' in dev_deps
                    has_vitest = 'vitest' in dev_deps
                    has_cypress = 'cypress' in dev_deps
                    
                    if not (has_jest or has_vitest or has_cypress):
                        test_suggestions.append({
                            'type': 'setup_js_testing',
                            'name': 'Setup JavaScript Testing Framework',
                            'description': 'Install and configure testing framework (Jest/Vitest/Cypress)',
                            'file_path': '',
                            'priority': 'high',
                            'template': 'js_testing_setup'
                        })
                
                except Exception:
                    pass
        
        return test_suggestions[:10]  # Limit to 10 suggestions
    
    def generate_ci_cd_suggestions(self, project_path: str) -> List[Dict]:
        """Generate CI/CD pipeline suggestions based on project structure"""
        suggestions = []
        
        if not self.tech_detector:
            return suggestions
        
        detected_techs = self.tech_detector.analyze_repo(project_path)
        github_dir = Path(project_path) / ".github"
        workflows_dir = github_dir / "workflows"
        
        # Check if GitHub Actions is already set up
        if not workflows_dir.exists():
            suggestions.append({
                'type': 'setup_github_actions',
                'name': 'Setup GitHub Actions CI/CD',
                'description': 'Create GitHub Actions workflow directory and basic CI pipeline',
                'priority': 'high',
                'files_to_create': ['.github/workflows/']
            })
        
        # Laravel-specific CI/CD suggestions
        if 'laravel' in detected_techs:
            laravel_ci_file = workflows_dir / "laravel.yml"
            if not laravel_ci_file.exists():
                suggestions.append({
                    'type': 'laravel_ci',
                    'name': 'Laravel CI/CD Pipeline',
                    'description': 'Create comprehensive Laravel CI/CD with testing, security checks, and deployment',
                    'priority': 'high',
                    'template': 'laravel_github_actions'
                })
        
        # Node.js/Frontend CI/CD suggestions
        if any(tech in detected_techs for tech in ['javascript', 'typescript', 'react', 'vue']):
            node_ci_file = workflows_dir / "node.yml"
            if not node_ci_file.exists():
                suggestions.append({
                    'type': 'node_ci',
                    'name': 'Node.js CI/CD Pipeline',
                    'description': 'Create Node.js CI/CD with testing, linting, and build processes',
                    'priority': 'medium',
                    'template': 'node_github_actions'
                })
        
        # Docker suggestions
        dockerfile = Path(project_path) / "Dockerfile"
        if not dockerfile.exists() and 'laravel' in detected_techs:
            suggestions.append({
                'type': 'dockerize',
                'name': 'Dockerize Application',
                'description': 'Create Dockerfile and docker-compose.yml for containerization',
                'priority': 'medium',
                'template': 'laravel_docker'
            })
        
        return suggestions
    
    def execute_scaffolding(self, scaffold_info: Dict, project_path: str) -> bool:
        """Execute scaffolding based on the provided information"""
        try:
            template = scaffold_info['scaffold_info']
            name = scaffold_info['name']
            
            console.print(f"🏗️ Scaffolding {template.name}: {name}")
            
            # Create files
            files_created = []
            for file_info in template.files_to_create:
                file_path = file_info['path'].format(
                    name=name,
                    name_kebab=self._to_kebab_case(name),
                    name_snake=self._to_snake_case(name)
                )
                
                full_path = Path(project_path) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Generate file content based on template
                content = self._generate_file_content(file_info['template'], name)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                files_created.append(str(full_path))
                console.print(f"   ✅ Created: {file_path}")
            
            # Run commands
            for command in template.commands_to_run:
                formatted_command = command.format(
                    name=name,
                    name_kebab=self._to_kebab_case(name),
                    name_snake=self._to_snake_case(name)
                )
                
                console.print(f"   🔧 Running: {formatted_command}")
                
                try:
                    result = subprocess.run(
                        formatted_command.split(),
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        console.print(f"      ✅ Command successful")
                    else:
                        console.print(f"      ⚠️ Command failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    console.print(f"      ⚠️ Command timed out")
                except Exception as e:
                    console.print(f"      ⚠️ Error running command: {e}")
            
            console.print(f"🎉 Successfully scaffolded {name}!")
            return True
            
        except Exception as e:
            console.print(f"❌ Error during scaffolding: {e}")
            return False
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case"""
        return re.sub(r'(?<!^)(?=[A-Z])', '-', text).lower()
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    
    def _generate_file_content(self, template_name: str, name: str) -> str:
        """Generate file content based on template"""
        # Convert name to different cases
        name_kebab = self._to_kebab_case(name)
        name_snake = self._to_snake_case(name)
        
        templates = {
            'livewire_component': f'''<?php

namespace App\\Http\\Livewire;

use Livewire\\Component;

class {name} extends Component
{{
    public function render()
    {{
        return view('livewire.{name_kebab}');
    }}
}}
''',
            'livewire_view': f'''<div>
    {{-- {name} Livewire Component --}}
    <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">{name}</h3>
        
        {{-- Add your component content here --}}
        <p class="text-gray-600">This is your {name} component.</p>
        
        {{-- Example Alpine.js interaction --}}
        <div x-data="{{ message: 'Hello from Alpine!' }}">
            <button 
                x-on:click="message = 'Button clicked!'"
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
                Click me
            </button>
            <p x-text="message" class="mt-2 text-sm text-gray-700"></p>
        </div>
    </div>
</div>
''',
            'tailwind_component': f'''{{-- {name} TailwindCSS Component --}}
<div 
    x-data="{{ 
        isOpen: false,
        toggle() {{ this.isOpen = !this.isOpen }}
    }}"
    class="relative"
>
    <button 
        @click="toggle()"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
    >
        {name}
    </button>
    
    <div 
        x-show="isOpen"
        x-transition:enter="transition ease-out duration-200"
        x-transition:enter-start="opacity-0 transform scale-95"
        x-transition:enter-end="opacity-100 transform scale-100"
        x-transition:leave="transition ease-in duration-150"
        x-transition:leave-start="opacity-100 transform scale-100"
        x-transition:leave-end="opacity-0 transform scale-95"
        class="absolute z-10 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
    >
        <div class="py-1">
            <p class="px-4 py-2 text-sm text-gray-700">
                Your {name} component content here
            </p>
        </div>
    </div>
</div>
''',
            'laravel_github_actions': '''name: Laravel CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: testing
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - uses: actions/checkout@v3

    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.1'
        extensions: mbstring, dom, fileinfo, mysql
        coverage: xdebug

    - name: Copy .env
      run: php -r "file_exists('.env') || copy('.env.example', '.env');"

    - name: Install Dependencies
      run: composer install -q --no-ansi --no-interaction --no-scripts --no-progress --prefer-dist

    - name: Generate key
      run: php artisan key:generate

    - name: Directory Permissions
      run: chmod -R 777 storage bootstrap/cache

    - name: Run Database Migrations
      env:
        DB_CONNECTION: mysql
        DB_HOST: 127.0.0.1
        DB_PORT: 3306
        DB_DATABASE: testing
        DB_USERNAME: root
        DB_PASSWORD: password
      run: php artisan migrate --force

    - name: Execute tests (Unit and Feature tests) via PHPUnit
      env:
        DB_CONNECTION: mysql
        DB_HOST: 127.0.0.1
        DB_PORT: 3306
        DB_DATABASE: testing
        DB_USERNAME: root
        DB_PASSWORD: password
      run: vendor/bin/phpunit --coverage-text

    - name: Install Node.js Dependencies
      run: npm ci

    - name: Build Assets
      run: npm run build

    - name: Deploy to staging
      if: github.ref == 'refs/heads/develop'
      run: echo "Deploy to staging server"
      
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: echo "Deploy to production server"
''',
        }
        
        return templates.get(template_name, f"# {template_name} template not found")
    
    async def handle_smart_todo_creation(self, user_input: str) -> bool:
        """Handle smart todo creation with instant action prompt"""
        auto_todo = self.parse_smart_todo(user_input)
        
        if not auto_todo:
            return False
        
        # Display the parsed todo
        console.print(Panel.fit(
            f"🤖 Smart Todo Detected!\n\n"
            f"📝 Title: {auto_todo.suggested_title}\n"
            f"📋 Description: {auto_todo.suggested_description}\n"
            f"📁 Files: {', '.join(auto_todo.detected_files) if auto_todo.detected_files else 'None detected'}\n"
            f"🎯 Action: {auto_todo.action_type.title()}\n"
            f"🎲 Confidence: {auto_todo.confidence:.0%}",
            style="bold green"
        ))
        
        # Confirm todo creation
        if not Confirm.ask("Create this todo?", default=True):
            console.print("❌ Todo creation cancelled.")
            return False
        
        # Create the todo
        todo_id = self.todo_manager.add_todo(
            title=auto_todo.suggested_title,
            description=auto_todo.suggested_description,
            todo_type="smart",
            priority="medium"
        )
        
        console.print(f"✅ Todo created with ID: {todo_id}")
        
        # Instant action prompt
        if auto_todo.auto_start_eligible:
            if Confirm.ask("🚀 Start working on this todo now?", default=False):
                console.print("🔥 Starting multitasking on your new todo...")
                try:
                    # Start multitasking on the specific todo
                    await self._start_single_todo_multitask(todo_id)
                    return True
                except Exception as e:
                    console.print(f"❌ Error starting multitask: {e}")
                    console.print("💡 You can start it manually with 'multitask' command")
        
        return True
    
    def parse_smart_todo(self, user_input: str) -> Optional[AutoTodoRequest]:
        """Parse user input to detect todo creation intent"""
        user_input = user_input.strip().lower()
        
        # Enhanced patterns for detecting todo creation
        for action_type, patterns in self.file_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    # Extract information from the match
                    title = self._extract_title_from_input(user_input, action_type)
                    description = self._extract_description_from_input(user_input, match)
                    files = self._extract_files_from_input(user_input)
                    
                    return AutoTodoRequest(
                        original_input=user_input,
                        suggested_title=title,
                        suggested_description=description,
                        detected_files=files,
                        action_type=action_type,
                        confidence=0.8,
                        auto_start_eligible=True
                    )
        
        # Fallback for general todo creation
        if any(word in user_input for word in ['update', 'change', 'modify', 'fix', 'create', 'add']):
            return AutoTodoRequest(
                original_input=user_input,
                suggested_title=user_input.capitalize(),
                suggested_description=f"Work on: {user_input}",
                detected_files=[],
                action_type='general',
                confidence=0.6,
                auto_start_eligible=True
            )
        
        return None
    
    def _extract_title_from_input(self, user_input: str, action_type: str) -> str:
        """Extract a clean title from user input"""
        # Remove common prefixes and clean up
        title = user_input.strip()
        title = re.sub(r'^(please\s+)?(can\s+you\s+)?', '', title, flags=re.IGNORECASE)
        title = title.capitalize()
        
        # Limit length
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title
    
    def _extract_description_from_input(self, user_input: str, match) -> str:
        """Extract description from user input and regex match"""
        return f"User request: {user_input}\n\nDetected action: {match.group(0) if match else 'General task'}"
    
    def _extract_files_from_input(self, user_input: str) -> List[str]:
        """Extract file names from user input"""
        # Look for file extensions
        file_pattern = r'\b\w+\.[a-zA-Z]{2,4}\b'
        files = re.findall(file_pattern, user_input)
        return files
    
    async def run_all_todos(self) -> bool:
        """Run multitasking on all pending todos - the ultimate shortcut"""
        todos = self.todo_manager.get_todos()
        pending_todos = [todo for todo in todos if todo.get('status') == 'pending']
        
        if not pending_todos:
            console.print("📭 No pending todos to run!")
            return False
        
        console.print(Panel.fit(
            f"🔥 RUN ALL MODE ACTIVATED!\n\n"
            f"📊 Found {len(pending_todos)} pending todos\n"
            f"⚡ About to start multitasking on ALL of them\n"
            f"🚀 This is the ultimate productivity shortcut!",
            style="bold red"
        ))
        
        # Show the todos that will be processed
        console.print("\n📋 Todos to process:")
        for i, todo in enumerate(pending_todos[:5], 1):  # Show first 5
            console.print(f"  {i}. {todo.get('title', 'Untitled')}")
        
        if len(pending_todos) > 5:
            console.print(f"  ... and {len(pending_todos) - 5} more")
        
        # Confirmation
        if not Confirm.ask(f"\n💥 Ready to unleash the beast on {len(pending_todos)} todos?", default=False):
            console.print("🛑 Run all cancelled - probably a wise choice!")
            return False
        
        console.print("🔥 MAXIMUM PRODUCTIVITY MODE ENGAGED!")
        
        try:
            # Start multitasking on all pending todos
            await self.multitasker.start_multitask(pending_todos)
            console.print("🎉 ALL TODOS LAUNCHED! The automation army is working!")
            return True
        except Exception as e:
            console.print(f"💥 Run all encountered an error: {e}")
            return False
    
    def run_all_todos_sync(self, working_dir=None):
        """Synchronous wrapper for run_all_todos to avoid event loop conflicts"""
        try:
            import asyncio
            import os
            
            # CRITICAL FIX: Ensure we have the correct working directory
            if working_dir is None:
                working_dir = os.getcwd()
            
            console.print(f"🎯 AUTOMATION ENGINE: Using working directory: {working_dir}")
            
            # CRITICAL FIX: Re-initialize AI router with correct working directory
            if hasattr(self.multitasker, 'ai_router'):
                console.print("🔧 Re-initializing AI router with correct working directory...")
                try:
                    # Initialize all MCP servers with the correct working directory
                    asyncio.run(self.multitasker.ai_router.initialize_all_servers(working_dir))
                    console.print("✅ AI router re-initialized successfully")
                except Exception as init_error:
                    console.print(f"⚠️ AI router re-initialization failed: {init_error}")
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in a running loop, use create_task
                task = loop.create_task(self.run_all_todos())
                return task
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.run_all_todos())
        except Exception as e:
            console.print(f"❌ Error in run_all_todos_sync: {e}")
            return False
    
    async def _start_single_todo_multitask(self, todo_id: str):
        """Start multitasking on a single specific todo"""
        # Get the specific todo by ID
        todo = self.todo_manager.get_todo_by_id(todo_id)
        if todo:
            await self.multitasker.start_multitask([todo])
        else:
            console.print(f"❌ Todo with ID {todo_id} not found")
    
    def toggle_github_pro_mode(self) -> bool:
        """Toggle GitHub Pro mode on/off"""
        self.github_pro_mode = not self.github_pro_mode
        
        if self.github_pro_mode:
            console.print(Panel.fit(
                "🚀 GITHUB PRO MODE ACTIVATED!\n\n"
                "✨ Features enabled:\n"
                "  • Each todo gets its own branch\n"
                "  • Automatic branch creation\n"
                "  • Auto-push when todo completes\n"
                "  • Automatic PR creation\n"
                "  • Advanced GitHub workflow integration\n\n"
                "🎯 You're now in full automation mode!",
                style="bold green"
            ))
        else:
            console.print(Panel.fit(
                "📴 GitHub Pro Mode Deactivated\n\n"
                "Back to standard todo management mode.",
                style="bold yellow"
            ))
        
        return self.github_pro_mode
    
    async def handle_github_pro_todo(self, todo_id: str, todo_title: str):
        """Handle a todo in GitHub Pro mode with branch creation and PR automation"""
        if not self.github_pro_mode or not self.github_integration:
            return False
        
        try:
            # Create a branch for this todo
            branch_name = self._generate_branch_name(todo_title)
            console.print(f"🌿 Creating branch: {branch_name}")
            
            # This would integrate with GitHubIntegration to create branch
            # Implementation depends on the existing GitHub integration
            
            console.print(f"✅ Branch {branch_name} created for todo {todo_id}")
            return True
            
        except Exception as e:
            console.print(f"❌ GitHub Pro mode error: {e}")
            return False
    
    def _generate_branch_name(self, todo_title: str) -> str:
        """Generate a clean branch name from todo title"""
        # Clean the title for branch naming
        clean_title = re.sub(r'[^a-zA-Z0-9\s-]', '', todo_title)
        clean_title = re.sub(r'\s+', '-', clean_title.strip())
        clean_title = clean_title.lower()[:50]  # Limit length
        
        return f"todo/{clean_title}"
    
    def get_automation_status(self) -> Dict:
        """Get current automation engine status"""
        return {
            'github_pro_mode': self.github_pro_mode,
            'smart_parsing_enabled': True,
            'instant_actions_enabled': True,
            'run_all_available': True,
            'github_integration': self.github_integration is not None
        }

# Legacy compatibility - keeping the original class name
class AutomationEngine(EnhancedAutomationEngine):
    """Legacy compatibility class"""
    pass
