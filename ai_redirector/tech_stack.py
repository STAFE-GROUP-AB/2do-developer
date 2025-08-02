"""
Tech Stack Detector - Analyzes repositories to detect technology stack and create memory files
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Set
from rich.console import Console

console = Console()

class TechStackDetector:
    """Detects technology stack from repository analysis"""
    
    def __init__(self):
        self.memory_dir = Path.home() / ".ai_redirector" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Define file patterns for different technologies
        self.tech_patterns = {
            "python": [".py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "javascript": [".js", ".jsx", "package.json", "yarn.lock", "npm-shrinkwrap.json"],
            "typescript": [".ts", ".tsx", "tsconfig.json"],
            "react": ["package.json"], # Special case, checked in content
            "vue": [".vue", "vue.config.js"],
            "angular": ["angular.json", ".angular-cli.json"],
            "node": ["package.json", "server.js", "app.js"],
            "java": [".java", "pom.xml", "build.gradle", "gradle.properties"],
            "csharp": [".cs", ".csproj", ".sln", "packages.config"],
            "cpp": [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", "CMakeLists.txt", "Makefile"],
            "rust": [".rs", "Cargo.toml", "Cargo.lock"],
            "go": [".go", "go.mod", "go.sum"],
            "php": [".php", "composer.json", "composer.lock"],
            "ruby": [".rb", "Gemfile", "Gemfile.lock", ".gemspec"],
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"],
            "kubernetes": [".yaml", ".yml"], # Special case for k8s files
            "terraform": [".tf", ".tfvars"],
            "html": [".html", ".htm"],
            "css": [".css", ".scss", ".sass", ".less"],
            "database": [".sql", ".db", ".sqlite", ".sqlite3"],
            "git": [".gitignore", ".gitattributes", ".git"]
        }
    
    def analyze_repo(self, repo_path: str) -> List[str]:
        """Analyze repository to detect technology stack"""
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            console.print(f"❌ Repository path does not exist: {repo_path}")
            return []
        
        detected_techs = set()
        
        # Walk through repository files
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                file_path = Path(root) / file
                self._analyze_file(file_path, detected_techs)
        
        # Special analysis for package.json content
        package_json = repo_path / "package.json"
        if package_json.exists():
            self._analyze_package_json(package_json, detected_techs)
        
        return sorted(list(detected_techs))
    
    def _analyze_file(self, file_path: Path, detected_techs: Set[str]):
        """Analyze a single file to detect technologies"""
        file_name = file_path.name
        file_suffix = file_path.suffix
        
        # Check file patterns
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if file_name == pattern or file_name.endswith(pattern) or file_suffix == pattern:
                    detected_techs.add(tech)
                    break
        
        # Special cases for Kubernetes YAML files
        if file_suffix in ['.yaml', '.yml']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if any(k8s_keyword in content for k8s_keyword in ['apiVersion:', 'kind:', 'metadata:', 'spec:']):
                        detected_techs.add('kubernetes')
            except Exception:
                pass
    
    def _analyze_package_json(self, package_json_path: Path, detected_techs: Set[str]):
        """Analyze package.json for specific frameworks"""
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            dependencies = {}
            dependencies.update(package_data.get('dependencies', {}))
            dependencies.update(package_data.get('devDependencies', {}))
            
            # Check for specific frameworks
            if 'react' in dependencies or 'react-dom' in dependencies:
                detected_techs.add('react')
            
            if 'vue' in dependencies or '@vue/cli' in dependencies:
                detected_techs.add('vue')
            
            if '@angular/core' in dependencies:
                detected_techs.add('angular')
            
            if 'express' in dependencies or 'fastify' in dependencies:
                detected_techs.add('node')
            
            if 'next' in dependencies or 'nuxt' in dependencies:
                detected_techs.add('react' if 'next' in dependencies else 'vue')
                
        except Exception as e:
            console.print(f"⚠️  Could not analyze package.json: {e}")
    
    def create_memory_files(self, tech_stack: List[str]):
        """Create memory files for detected technologies"""
        console.print("💾 Creating memory files for tech stack...")
        
        for tech in tech_stack:
            self._create_tech_memory_file(tech)
        
        # Create a combined context file
        self._create_combined_context_file(tech_stack)
        
        console.print(f"✅ Memory files created for: {', '.join(tech_stack)}")
    
    def _create_tech_memory_file(self, tech: str):
        """Create a memory file for a specific technology"""
        memory_file = self.memory_dir / f"{tech}_context.json"
        
        # Get technology-specific context
        context = self._get_tech_context(tech)
        
        with open(memory_file, 'w') as f:
            json.dump(context, f, indent=2)
    
    def _get_tech_context(self, tech: str) -> Dict:
        """Get context information for a specific technology"""
        contexts = {
            "python": {
                "description": "Python programming language",
                "common_patterns": ["Object-oriented programming", "PEP 8 style guide", "Virtual environments"],
                "best_practices": ["Use type hints", "Follow PEP 8", "Write docstrings", "Use virtual environments"],
                "common_libraries": ["requests", "numpy", "pandas", "flask", "django", "fastapi"],
                "file_extensions": [".py"],
                "testing_frameworks": ["pytest", "unittest"],
                "package_managers": ["pip", "conda", "poetry"]
            },
            "javascript": {
                "description": "JavaScript programming language",
                "common_patterns": ["Async/await", "ES6+ features", "Module system"],
                "best_practices": ["Use const/let instead of var", "Prefer arrow functions", "Use strict mode"],
                "common_libraries": ["lodash", "axios", "moment", "express"],
                "file_extensions": [".js", ".mjs"],
                "testing_frameworks": ["jest", "mocha", "jasmine"],
                "package_managers": ["npm", "yarn", "pnpm"]
            },
            "react": {
                "description": "React JavaScript library for building user interfaces",
                "common_patterns": ["Component-based architecture", "JSX", "Hooks", "State management"],
                "best_practices": ["Use functional components", "Implement proper key props", "Optimize with useMemo/useCallback"],
                "common_libraries": ["react-router", "redux", "styled-components"],
                "file_extensions": [".jsx", ".tsx"],
                "testing_frameworks": ["react-testing-library", "enzyme"],
                "package_managers": ["npm", "yarn"]
            },
            "docker": {
                "description": "Container platform for packaging applications",
                "common_patterns": ["Multi-stage builds", "Layer optimization", "Health checks"],
                "best_practices": ["Use specific base images", "Minimize layers", "Use .dockerignore"],
                "common_files": ["Dockerfile", "docker-compose.yml"],
                "file_extensions": [],
                "testing_frameworks": ["docker-compose", "testcontainers"],
                "package_managers": []
            }
        }
        
        # Return specific context or generic context
        return contexts.get(tech, {
            "description": f"{tech.title()} technology",
            "common_patterns": [],
            "best_practices": [],
            "common_libraries": [],
            "file_extensions": [],
            "testing_frameworks": [],
            "package_managers": []
        })
    
    def _create_combined_context_file(self, tech_stack: List[str]):
        """Create a combined context file for the entire tech stack"""
        combined_context = {
            "tech_stack": tech_stack,
            "created_at": str(Path.home()),
            "description": f"Combined context for tech stack: {', '.join(tech_stack)}",
            "integration_notes": self._get_integration_notes(tech_stack),
            "recommended_practices": self._get_stack_recommendations(tech_stack)
        }
        
        combined_file = self.memory_dir / "tech_stack_context.json"
        with open(combined_file, 'w') as f:
            json.dump(combined_context, f, indent=2)
    
    def _get_integration_notes(self, tech_stack: List[str]) -> List[str]:
        """Get integration notes for the tech stack combination"""
        notes = []
        
        if "react" in tech_stack and "node" in tech_stack:
            notes.append("Full-stack JavaScript application with React frontend and Node.js backend")
        
        if "python" in tech_stack and "docker" in tech_stack:
            notes.append("Containerized Python application - consider using slim Python base images")
        
        if "kubernetes" in tech_stack and "docker" in tech_stack:
            notes.append("Container orchestration setup - ensure proper resource limits and health checks")
        
        return notes
    
    def _get_stack_recommendations(self, tech_stack: List[str]) -> List[str]:
        """Get recommendations for the tech stack"""
        recommendations = []
        
        if "javascript" in tech_stack or "typescript" in tech_stack:
            recommendations.append("Consider using ESLint and Prettier for code quality")
        
        if "python" in tech_stack:
            recommendations.append("Use virtual environments and requirements.txt or pyproject.toml")
        
        if "docker" in tech_stack:
            recommendations.append("Implement multi-stage builds and use .dockerignore")
        
        return recommendations
    
    def get_memory_context(self, tech: str) -> Dict:
        """Get memory context for a specific technology"""
        memory_file = self.memory_dir / f"{tech}_context.json"
        
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        
        return self._get_tech_context(tech)