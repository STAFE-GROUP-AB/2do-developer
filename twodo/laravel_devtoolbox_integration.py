#!/usr/bin/env python3
"""
Laravel DevToolbox Integration - Integrates the laravel-devtoolbox package for enhanced Laravel analysis
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.table import Table

console = Console()

class LaravelDevToolboxIntegration:
    """Integration with grazulex/laravel-devtoolbox for enhanced Laravel analysis"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.composer_json_path = self.project_path / "composer.json"
        self.artisan_path = self.project_path / "artisan"
        
    def is_laravel_project(self) -> bool:
        """Check if the current directory is a Laravel project"""
        if not self.composer_json_path.exists() or not self.artisan_path.exists():
            return False
            
        try:
            with open(self.composer_json_path, 'r') as f:
                composer_data = json.load(f)
            
            dependencies = composer_data.get('require', {})
            return 'laravel/framework' in dependencies
        except Exception:
            return False
    
    def is_devtoolbox_installed(self) -> bool:
        """Check if laravel-devtoolbox is installed in the project"""
        if not self.composer_json_path.exists():
            return False
            
        try:
            with open(self.composer_json_path, 'r') as f:
                composer_data = json.load(f)
            
            dev_dependencies = composer_data.get('require-dev', {})
            return 'grazulex/laravel-devtoolbox' in dev_dependencies
        except Exception:
            return False
    
    def install_devtoolbox(self, force: bool = False) -> bool:
        """Install laravel-devtoolbox package"""
        if not self.is_laravel_project():
            console.print("❌ Not a Laravel project. Cannot install laravel-devtoolbox.")
            return False
        
        if self.is_devtoolbox_installed() and not force:
            console.print("✅ Laravel DevToolbox is already installed.")
            return True
        
        console.print("📦 Installing Laravel DevToolbox...")
        
        try:
            # Check if composer is available
            if not shutil.which('composer'):
                console.print("❌ Composer not found. Please install Composer first.")
                return False
            
            # Install the package
            result = subprocess.run(
                ['composer', 'require', '--dev', 'grazulex/laravel-devtoolbox'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                console.print("✅ Laravel DevToolbox installed successfully!")
                return True
            else:
                console.print(f"❌ Failed to install Laravel DevToolbox: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            console.print("❌ Installation timed out. Please try again.")
            return False
        except Exception as e:
            console.print(f"❌ Error installing Laravel DevToolbox: {e}")
            return False
    
    def get_available_commands(self) -> List[str]:
        """Get list of available Laravel DevToolbox commands"""
        if not self.is_devtoolbox_installed():
            return []
        
        try:
            result = subprocess.run(
                ['php', 'artisan', 'list', 'dev:'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                commands = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('dev:'):
                        # Extract command name (before first space)
                        command = line.split()[0]
                        commands.append(command)
                return commands
            else:
                return []
                
        except Exception:
            return []
    
    def run_devtoolbox_command(self, command: str, args: List[str] = None, format_output: str = 'array') -> Optional[Dict]:
        """Run a Laravel DevToolbox command and return the output"""
        if not self.is_devtoolbox_installed():
            console.print("❌ Laravel DevToolbox is not installed.")
            return None
        
        if args is None:
            args = []
        
        # Add format option if supported
        if format_output and format_output != 'array':
            args.extend(['--format', format_output])
        
        try:
            cmd = ['php', 'artisan', command] + args
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                if format_output == 'json':
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return {"raw_output": result.stdout}
                else:
                    return {"raw_output": result.stdout}
            else:
                console.print(f"❌ Command failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            console.print("❌ Command timed out")
            return None
        except Exception as e:
            console.print(f"❌ Error running command: {e}")
            return None
    
    def analyze_application(self) -> Optional[Dict]:
        """Run comprehensive application analysis"""
        console.print("🔍 Running Laravel application analysis...")
        
        analysis_results = {}
        
        # Run multiple analysis commands
        commands_to_run = [
            ('dev:scan', ['--all'], 'Application scan'),
            ('dev:models', [], 'Models analysis'),
            ('dev:routes', [], 'Routes analysis'),
            ('dev:routes:unused', [], 'Unused routes'),
        ]
        
        for command, args, description in commands_to_run:
            console.print(f"  📊 {description}...")
            result = self.run_devtoolbox_command(command, args, 'json')
            if result:
                analysis_results[command.replace(':', '_')] = result
        
        return analysis_results
    
    def generate_model_graph(self, output_file: str = None, format_type: str = 'mermaid') -> bool:
        """Generate model relationship graph"""
        args = ['--format', format_type]
        if output_file:
            args.extend(['--output', output_file])
        
        console.print(f"📊 Generating model relationship graph ({format_type})...")
        result = self.run_devtoolbox_command('dev:model:graph', args)
        
        if result and output_file:
            console.print(f"✅ Model graph saved to: {output_file}")
            return True
        elif result:
            console.print("📊 Model relationship graph:")
            console.print(result.get('raw_output', ''))
            return True
        
        return False
    
    def find_unused_routes(self) -> Optional[List[Dict]]:
        """Find unused routes in the application"""
        console.print("🔍 Finding unused routes...")
        result = self.run_devtoolbox_command('dev:routes:unused', [], 'json')
        
        if result and 'unused_routes' in result:
            return result['unused_routes']
        elif result:
            console.print("📊 Unused routes analysis:")
            console.print(result.get('raw_output', ''))
            return []
        
        return None
    
    def analyze_models(self) -> Optional[Dict]:
        """Analyze Laravel models"""
        console.print("🔍 Analyzing Laravel models...")
        result = self.run_devtoolbox_command('dev:models', [], 'json')
        
        if result:
            return result
        
        return None
    
    def trace_sql_queries(self, route: str = None) -> Optional[Dict]:
        """Trace SQL queries for a specific route"""
        args = []
        if route:
            args.extend(['--route', route])
        
        console.print(f"🔍 Tracing SQL queries{' for ' + route if route else ''}...")
        result = self.run_devtoolbox_command('dev:sql:trace', args, 'json')
        
        return result
    
    def check_security_issues(self) -> Optional[Dict]:
        """Check for security issues like unprotected routes"""
        console.print("🔒 Checking for security issues...")
        result = self.run_devtoolbox_command('dev:security:unprotected-routes', ['--critical-only'], 'json')
        
        return result
    
    def get_analysis_summary(self) -> Dict:
        """Get a summary of analysis results for AI context"""
        if not self.is_laravel_project():
            return {"error": "Not a Laravel project"}
        
        if not self.is_devtoolbox_installed():
            return {"error": "Laravel DevToolbox not installed"}
        
        summary = {
            "project_type": "Laravel",
            "devtoolbox_available": True,
            "available_commands": self.get_available_commands(),
            "quick_analysis": {}
        }
        
        # Quick analysis for AI context
        try:
            # Get models count
            models_result = self.run_devtoolbox_command('dev:models', ['--format', 'count'])
            if models_result:
                summary["quick_analysis"]["models_count"] = models_result
            
            # Get routes count  
            routes_result = self.run_devtoolbox_command('dev:routes', ['--format', 'count'])
            if routes_result:
                summary["quick_analysis"]["routes_count"] = routes_result
            
            # Check for unused routes
            unused_routes = self.run_devtoolbox_command('dev:routes:unused', ['--format', 'count'])
            if unused_routes:
                summary["quick_analysis"]["unused_routes_count"] = unused_routes
        
        except Exception as e:
            summary["quick_analysis"]["error"] = str(e)
        
        return summary
    
    def prompt_for_installation(self) -> bool:
        """Prompt user to install Laravel DevToolbox if it's not installed"""
        if not self.is_laravel_project():
            return False
        
        if self.is_devtoolbox_installed():
            return True
        
        console.print(Panel(
            "🛠️ Laravel DevToolbox Integration\n\n"
            "Laravel DevToolbox provides comprehensive analysis tools for Laravel applications:\n"
            "• Deep application scanning and model analysis\n"
            "• Route analysis and unused route detection\n" 
            "• SQL query tracing and N+1 problem detection\n"
            "• Service container analysis\n"
            "• Security scanning\n"
            "• Model relationship diagrams\n\n"
            "This will enhance 2DO's Laravel assistance capabilities significantly.",
            title="Enhanced Laravel Analysis Available",
            border_style="blue"
        ))
        
        if Confirm.ask("Would you like to install Laravel DevToolbox for enhanced Laravel analysis?"):
            return self.install_devtoolbox()
        
        return False
    
    def create_analysis_report(self, output_file: str = None) -> Dict:
        """Create a comprehensive analysis report"""
        if not self.is_devtoolbox_installed():
            console.print("❌ Laravel DevToolbox is required for analysis reports.")
            return {}
        
        console.print("📊 Creating comprehensive Laravel analysis report...")
        
        report = {
            "generated_at": str(Path.cwd()),
            "project_path": str(self.project_path),
            "analysis": {}
        }
        
        # Run comprehensive analysis
        analysis_result = self.analyze_application()
        if analysis_result:
            report["analysis"] = analysis_result
        
        # Add model analysis
        models_result = self.analyze_models()
        if models_result:
            report["models"] = models_result
        
        # Add unused routes
        unused_routes = self.find_unused_routes()
        if unused_routes:
            report["unused_routes"] = unused_routes
        
        # Add security analysis
        security_result = self.check_security_issues()
        if security_result:
            report["security"] = security_result
        
        # Save report if output file specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                console.print(f"✅ Analysis report saved to: {output_file}")
            except Exception as e:
                console.print(f"❌ Failed to save report: {e}")
        
        return report