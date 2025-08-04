#!/usr/bin/env python3
"""
Smart Code Analyzer - Intelligent code analysis and understanding for enhanced development workflow
"""

import os
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from rich.console import Console

console = Console()

@dataclass
class CodeAnalysis:
    """Represents analysis results for a code file"""
    file_path: str
    language: str
    complexity_score: int
    functions: List[Dict]
    classes: List[Dict]
    imports: List[str]
    dependencies: List[str]
    issues: List[Dict]
    suggestions: List[str]
    tech_stack_hints: List[str]

@dataclass
class ProjectAnalysis:
    """Represents analysis results for an entire project"""
    project_path: str
    file_analyses: List[CodeAnalysis]
    overall_complexity: str
    tech_stack: List[str]
    architecture_patterns: List[str]
    potential_issues: List[Dict]
    recommendations: List[str]

class SmartCodeAnalyzer:
    """Advanced code analysis for intelligent development assistance"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.php': 'php',
            '.blade.php': 'blade-php',
            '.vue': 'vue',
            '.jsx': 'react',
            '.tsx': 'react-ts'
        }
        
        # Common patterns for different frameworks
        self.framework_patterns = {
            'laravel': [
                r'use\s+Illuminate\\',
                r'Route::(get|post|put|delete)',
                r'@extends\(',
                r'@section\(',
                r'Artisan::',
                r'Schema::'
            ],
            'livewire': [
                r'use\s+Livewire\\',
                r'extends\s+Component',
                r'wire:',
                r'@livewire\(',
                r'emit\(',
                r'\$this->dispatch'
            ],
            'alpine': [
                r'x-data',
                r'x-show',
                r'x-if',
                r'@click',
                r'x-model',
                r'Alpine\.'
            ],
            'tailwind': [
                r'class="[^"]*(?:bg-|text-|p-|m-|flex|grid)',
                r'@apply\s+',
                r'@tailwind',
                r'@responsive'
            ],
            'react': [
                r'import\s+React',
                r'from\s+[\'"]react[\'"]',
                r'useState',
                r'useEffect',
                r'JSX\.Element',
                r'<[A-Z]\w*'
            ],
            'vue': [
                r'<template>',
                r'<script>',
                r'export\s+default\s*{',
                r'this\.\$',
                r'@click',
                r'v-if|v-for|v-model'
            ]
        }
        
    def analyze_file(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze a single code file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
            
        # Determine language
        language = self._detect_language(file_path)
        if not language:
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            console.print(f"⚠️ Could not read {file_path}: {e}")
            return None
        
        # Perform analysis based on language
        if language == 'python':
            return self._analyze_python_file(str(file_path), content)
        elif language in ['javascript', 'typescript']:
            return self._analyze_js_file(str(file_path), content, language)
        elif language in ['php', 'blade-php']:
            return self._analyze_php_file(str(file_path), content, language)
        else:
            return self._analyze_generic_file(str(file_path), content, language)
    
    def analyze_project(self, project_path: str, max_files: int = 50) -> ProjectAnalysis:
        """Analyze an entire project structure"""
        project_path = Path(project_path)
        file_analyses = []
        
        # Find code files
        code_files = []
        for ext in self.supported_languages.keys():
            code_files.extend(list(project_path.rglob(f"*{ext}"))[:max_files])
        
        # Limit to prevent overwhelming analysis
        code_files = code_files[:max_files]
        
        # Analyze each file
        for file_path in code_files:
            # Skip common directories to ignore
            if any(skip_dir in str(file_path) for skip_dir in ['node_modules', 'vendor', '.git', '__pycache__']):
                continue
                
            analysis = self.analyze_file(file_path)
            if analysis:
                file_analyses.append(analysis)
        
        # Aggregate project-level insights
        return self._aggregate_project_analysis(str(project_path), file_analyses)
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        suffix = file_path.suffix
        
        # Special case for blade.php files
        if str(file_path).endswith('.blade.php'):
            return 'blade-php'
        
        return self.supported_languages.get(suffix)
    
    def _analyze_python_file(self, file_path: str, content: str) -> CodeAnalysis:
        """Analyze Python file using AST"""
        functions = []
        classes = []
        imports = []
        issues = []
        suggestions = []
        tech_stack_hints = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'complexity': self._estimate_function_complexity(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len(methods),
                        'inheritance': len(node.bases)
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Check for specific frameworks
            content_lower = content.lower()
            if 'django' in content_lower or 'from django' in content:
                tech_stack_hints.append('django')
            if 'flask' in content_lower or 'from flask' in content:
                tech_stack_hints.append('flask')
            if 'fastapi' in content_lower:
                tech_stack_hints.append('fastapi')
                
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'message': f"Syntax error: {e}",
                'line': getattr(e, 'lineno', 0)
            })
        
        # Calculate complexity
        complexity_score = len(functions) * 2 + len(classes) * 3 + len(imports)
        
        # Generate suggestions
        if len(functions) > 20:
            suggestions.append("Consider breaking this file into smaller modules")
        if complexity_score > 50:
            suggestions.append("High complexity detected - consider refactoring")
        
        return CodeAnalysis(
            file_path=file_path,
            language='python',
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=[],
            issues=issues,
            suggestions=suggestions,
            tech_stack_hints=tech_stack_hints
        )
    
    def _analyze_js_file(self, file_path: str, content: str, language: str) -> CodeAnalysis:
        """Analyze JavaScript/TypeScript file"""
        functions = []
        classes = []
        imports = []
        issues = []
        suggestions = []
        tech_stack_hints = []
        
        # Basic pattern matching for JS/TS analysis
        
        # Find functions
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'(\w+)\s*:\s*function\s*\(',
            r'(\w+)\s*=>\s*[{(]'
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'function'
                })
        
        # Find classes
        class_matches = re.finditer(r'class\s+(\w+)', content)
        for match in class_matches:
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Find imports
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                imports.append(match.group(1))
        
        # Detect frameworks
        for framework, patterns in self.framework_patterns.items():
            if framework in ['react', 'vue']:
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        tech_stack_hints.append(framework)
                        break
        
        complexity_score = len(functions) * 2 + len(classes) * 3 + len(imports)
        
        return CodeAnalysis(
            file_path=file_path,
            language=language,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=[],
            issues=issues,
            suggestions=suggestions,
            tech_stack_hints=tech_stack_hints
        )
    
    def _analyze_php_file(self, file_path: str, content: str, language: str) -> CodeAnalysis:
        """Analyze PHP/Blade file"""
        functions = []
        classes = []
        imports = []
        issues = []
        suggestions = []
        tech_stack_hints = []
        
        # Find PHP functions
        function_matches = re.finditer(r'function\s+(\w+)\s*\(', content)
        for match in function_matches:
            functions.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1,
                'type': 'function'
            })
        
        # Find PHP classes
        class_matches = re.finditer(r'class\s+(\w+)', content)
        for match in class_matches:
            classes.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Find use statements
        use_matches = re.finditer(r'use\s+([^;]+);', content)
        for match in use_matches:
            imports.append(match.group(1).strip())
        
        # Detect Laravel/Livewire patterns
        for framework, patterns in self.framework_patterns.items():
            if framework in ['laravel', 'livewire', 'alpine', 'tailwind']:
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        tech_stack_hints.append(framework)
                        break
        
        complexity_score = len(functions) * 2 + len(classes) * 3 + len(imports)
        
        # Blade-specific analysis
        if language == 'blade-php':
            blade_directives = re.findall(r'@(\w+)', content)
            if blade_directives:
                suggestions.append(f"Blade template with {len(set(blade_directives))} unique directives")
        
        return CodeAnalysis(
            file_path=file_path,
            language=language,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=[],
            issues=issues,
            suggestions=suggestions,
            tech_stack_hints=tech_stack_hints
        )
    
    def _analyze_generic_file(self, file_path: str, content: str, language: str) -> CodeAnalysis:
        """Generic analysis for unsupported languages"""
        return CodeAnalysis(
            file_path=file_path,
            language=language,
            complexity_score=len(content.split('\n')),
            functions=[],
            classes=[],
            imports=[],
            dependencies=[],
            issues=[],
            suggestions=[],
            tech_stack_hints=[]
        )
    
    def _estimate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Estimate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _aggregate_project_analysis(self, project_path: str, file_analyses: List[CodeAnalysis]) -> ProjectAnalysis:
        """Aggregate individual file analyses into project-level insights"""
        if not file_analyses:
            return ProjectAnalysis(
                project_path=project_path,
                file_analyses=[],
                overall_complexity='low',
                tech_stack=[],
                architecture_patterns=[],
                potential_issues=[],
                recommendations=[]
            )
        
        # Aggregate tech stack hints
        tech_stack = set()
        for analysis in file_analyses:
            tech_stack.update(analysis.tech_stack_hints)
        
        # Calculate overall complexity
        total_complexity = sum(analysis.complexity_score for analysis in file_analyses)
        avg_complexity = total_complexity / len(file_analyses)
        
        if avg_complexity < 10:
            overall_complexity = 'low'
        elif avg_complexity < 25:
            overall_complexity = 'medium'
        else:
            overall_complexity = 'high'
        
        # Detect architecture patterns
        architecture_patterns = []
        if any('laravel' in analysis.tech_stack_hints for analysis in file_analyses):
            architecture_patterns.append('MVC (Laravel)')
        if any('react' in analysis.tech_stack_hints for analysis in file_analyses):
            architecture_patterns.append('Component-based (React)')
        if any('vue' in analysis.tech_stack_hints for analysis in file_analyses):
            architecture_patterns.append('Component-based (Vue)')
        
        # Generate recommendations
        recommendations = []
        if overall_complexity == 'high':
            recommendations.append("Consider refactoring complex files to improve maintainability")
        
        if 'laravel' in tech_stack and 'livewire' in tech_stack and 'tailwind' in tech_stack and 'alpine' in tech_stack:
            recommendations.append("Full TALL stack detected - leverage specialized TALL stack development patterns")
        elif 'laravel' in tech_stack:
            recommendations.append("Laravel project detected - consider adding Livewire for reactive components")
        
        if len(tech_stack) > 3:
            recommendations.append("Multiple technologies detected - ensure proper separation of concerns")
        
        return ProjectAnalysis(
            project_path=project_path,
            file_analyses=file_analyses,
            overall_complexity=overall_complexity,
            tech_stack=sorted(list(tech_stack)),
            architecture_patterns=architecture_patterns,
            potential_issues=[],
            recommendations=recommendations
        )
    
    def get_intelligent_suggestions(self, analysis: ProjectAnalysis) -> List[str]:
        """Generate intelligent development suggestions based on analysis"""
        suggestions = []
        
        # Technology-specific suggestions
        if 'laravel' in analysis.tech_stack:
            suggestions.append("Consider using Laravel best practices: Service classes, Form Requests, and Resource collections")
            
            if 'livewire' not in analysis.tech_stack:
                suggestions.append("Add Livewire for reactive PHP components without complex JavaScript")
        
        if 'tailwind' in analysis.tech_stack:
            suggestions.append("Optimize TailwindCSS by purging unused styles and using component classes")
        
        if 'alpine' in analysis.tech_stack:
            suggestions.append("Leverage Alpine.js for progressive enhancement - start with HTML, add reactivity")
        
        # Complexity-based suggestions
        if analysis.overall_complexity == 'high':
            suggestions.append("Break down complex files using design patterns like Repository, Service, or Factory")
        
        # Architecture suggestions
        if len(analysis.tech_stack) > 1:
            suggestions.append("Consider implementing a clear separation between frontend and backend concerns")
        
        return suggestions