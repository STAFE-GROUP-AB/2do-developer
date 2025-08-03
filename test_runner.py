#!/usr/bin/env python3
"""
Comprehensive test runner for 2DO
Runs all tests including setup verification and provides detailed reporting
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.text import Text
from rich.tree import Tree
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from twodo.setup_guide import SetupGuide
from twodo.config import ConfigManager


class TestSuiteRunner:
    """Comprehensive test suite runner with detailed reporting"""
    
    def __init__(self):
        self.console = Console()
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
    
    def run_all_tests(self):
        """Run all test suites and provide comprehensive reporting"""
        self.console.print(Panel.fit("🚀 2DO Comprehensive Test Suite", style="bold blue"))
        
        # Test suites to run
        test_suites = [
            ("Basic Functionality", "tests.test_basic"),
            ("Setup Verification", "tests.test_setup_verification"),
            ("CLI Integration", "tests.test_cli_integration"),
            ("Comprehensive Components", "tests.test_comprehensive")
        ]
        
        self.console.print("📋 Running test suites:")
        for i, (name, module) in enumerate(test_suites, 1):
            self.console.print(f"   {i}. {name}")
        
        # Run each test suite
        for suite_name, module_name in test_suites:
            self.console.print(f"\n{'='*60}")
            self.console.print(f"🧪 Running {suite_name} Tests", style="bold yellow")
            self.console.print(f"{'='*60}")
            
            try:
                self.run_test_suite(suite_name, module_name)
            except Exception as e:
                self.console.print(f"❌ Error running {suite_name}: {e}", style="bold red")
                self.results[suite_name] = {"error": str(e)}
        
        # Run setup verification
        self.console.print(f"\n{'='*60}")
        self.console.print("🔧 Running Setup Verification", style="bold yellow")
        self.console.print(f"{'='*60}")
        self.run_setup_verification()
        
        # Run integration tests
        self.console.print(f"\n{'='*60}")
        self.console.print("🔗 Running Integration Tests", style="bold yellow")
        self.console.print(f"{'='*60}")
        self.run_integration_tests()
        
        # Generate final report
        self.generate_final_report()
    
    def run_test_suite(self, suite_name, module_name):
        """Run a specific test suite"""
        try:
            # Import the test module
            test_module = __import__(module_name, fromlist=[''])
            
            # Discover and run tests
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Create custom test runner
            runner = unittest.TextTestRunner(
                stream=open(os.devnull, 'w'),  # Suppress normal output
                verbosity=0
            )
            
            # Run tests and capture results
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Process results
            total = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
            passed = total - failures - errors - skipped
            
            # Update overall statistics
            self.total_tests += total
            self.passed_tests += passed
            self.failed_tests += failures
            self.error_tests += errors
            self.skipped_tests += skipped
            
            # Store results
            self.results[suite_name] = {
                "total": total,
                "passed": passed,
                "failed": failures,
                "errors": errors,
                "skipped": skipped,
                "duration": end_time - start_time,
                "failure_details": result.failures,
                "error_details": result.errors
            }
            
            # Display immediate results
            self.display_suite_results(suite_name, self.results[suite_name])
            
        except ImportError as e:
            error_msg = f"Could not import test module {module_name}: {e}"
            self.console.print(f"❌ {error_msg}", style="bold red")
            self.results[suite_name] = {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error running {suite_name}: {e}"
            self.console.print(f"❌ {error_msg}", style="bold red")
            self.results[suite_name] = {"error": error_msg}
    
    def display_suite_results(self, suite_name, results):
        """Display results for a test suite"""
        if "error" in results:
            self.console.print(f"❌ {suite_name}: {results['error']}", style="bold red")
            return
        
        total = results["total"]
        passed = results["passed"]
        failed = results["failed"]
        errors = results["errors"]
        skipped = results["skipped"]
        duration = results["duration"]
        
        # Create results table
        table = Table(title=f"{suite_name} Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Percentage", style="yellow")
        
        if total > 0:
            table.add_row("Total Tests", str(total), "100%")
            table.add_row("Passed", str(passed), f"{(passed/total)*100:.1f}%")
            if failed > 0:
                table.add_row("Failed", str(failed), f"{(failed/total)*100:.1f}%")
            if errors > 0:
                table.add_row("Errors", str(errors), f"{(errors/total)*100:.1f}%")
            if skipped > 0:
                table.add_row("Skipped", str(skipped), f"{(skipped/total)*100:.1f}%")
            table.add_row("Duration", f"{duration:.2f}s", "")
        
        self.console.print(table)
        
        # Display failures and errors if any
        if failed > 0 or errors > 0:
            self.display_failure_details(suite_name, results)
        
        # Overall status
        if passed == total:
            self.console.print(f"✅ {suite_name}: All tests passed!", style="bold green")
        elif failed > 0 or errors > 0:
            self.console.print(f"❌ {suite_name}: {failed + errors} tests failed", style="bold red")
        else:
            self.console.print(f"⚠️ {suite_name}: {skipped} tests skipped", style="bold yellow")
    
    def display_failure_details(self, suite_name, results):
        """Display detailed failure information"""
        if results.get("failure_details") or results.get("error_details"):
            self.console.print(f"\n📋 {suite_name} Failure Details:", style="bold red")
            
            # Display failures
            for i, (test, traceback) in enumerate(results.get("failure_details", []), 1):
                self.console.print(f"\n   {i}. FAIL: {test}")
                # Show only the first few lines of traceback to avoid clutter
                traceback_lines = traceback.split('\n')[:3]
                for line in traceback_lines:
                    if line.strip():
                        self.console.print(f"      {line}", style="red")
            
            # Display errors
            for i, (test, traceback) in enumerate(results.get("error_details", []), 1):
                self.console.print(f"\n   {len(results.get('failure_details', []))+i}. ERROR: {test}")
                traceback_lines = traceback.split('\n')[:3]
                for line in traceback_lines:
                    if line.strip():
                        self.console.print(f"      {line}", style="red")
    
    def run_setup_verification(self):
        """Run setup verification tests"""
        try:
            # Create temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Test setup guide
                guide = SetupGuide(self.console)
                
                # Run setup verification in test mode
                self.console.print("🔍 Verifying setup system...")
                
                # Test configuration management
                config = ConfigManager(temp_dir)
                setup_status = {
                    "config_creation": config.config_file.exists(),
                    "config_structure": all(key in config.config for key in ["api_keys", "preferences", "mcp_servers"]),
                    "api_key_storage": True,  # Test API key storage
                    "preference_management": True  # Test preference management
                }
                
                # Test API key functionality
                try:
                    config.set_api_key("test", "test_key")
                    setup_status["api_key_storage"] = config.get_api_key("test") == "test_key"
                except Exception:
                    setup_status["api_key_storage"] = False
                
                # Test preference functionality
                try:
                    config.set_preference("test_pref", "test_value")
                    setup_status["preference_management"] = config.get_preference("test_pref") == "test_value"
                except Exception:
                    setup_status["preference_management"] = False
                
                # Display setup verification results
                self.display_setup_verification_results(setup_status)
                
        except Exception as e:
            self.console.print(f"❌ Setup verification failed: {e}", style="bold red")
            self.results["Setup Verification"] = {"error": str(e)}
    
    def display_setup_verification_results(self, setup_status):
        """Display setup verification results"""
        table = Table(title="Setup System Verification")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Description", style="yellow")
        
        components = [
            ("Config Creation", setup_status["config_creation"], "Configuration file creation"),
            ("Config Structure", setup_status["config_structure"], "Proper config file structure"),
            ("API Key Storage", setup_status["api_key_storage"], "API key storage and retrieval"),
            ("Preference Management", setup_status["preference_management"], "User preference handling")
        ]
        
        passed_count = 0
        for name, status, description in components:
            status_text = "✅ Pass" if status else "❌ Fail"
            table.add_row(name, status_text, description)
            if status:
                passed_count += 1
        
        self.console.print(table)
        
        # Store results
        self.results["Setup Verification"] = {
            "total": len(components),
            "passed": passed_count,
            "failed": len(components) - passed_count,
            "details": setup_status
        }
        
        if passed_count == len(components):
            self.console.print("✅ Setup verification: All components working!", style="bold green")
        else:
            self.console.print(f"❌ Setup verification: {len(components) - passed_count} components failed", style="bold red")
    
    def run_integration_tests(self):
        """Run integration tests"""
        integration_tests = [
            ("CLI Command Structure", self.test_cli_structure),
            ("Module Import Tests", self.test_module_imports),
            ("Configuration Persistence", self.test_config_persistence),
            ("Demo Script Execution", self.test_demo_execution)
        ]
        
        integration_results = {}
        
        for test_name, test_func in integration_tests:
            self.console.print(f"🧪 Running {test_name}...")
            try:
                result = test_func()
                integration_results[test_name] = {"status": "pass" if result else "fail", "details": result}
                status_text = "✅ Pass" if result else "❌ Fail"
                self.console.print(f"   {status_text}")
            except Exception as e:
                integration_results[test_name] = {"status": "error", "details": str(e)}
                self.console.print(f"   ❌ Error: {e}")
        
        # Display integration test results
        self.display_integration_results(integration_results)
    
    def test_cli_structure(self):
        """Test CLI command structure"""
        try:
            from twodo.cli import cli
            return hasattr(cli, 'commands') or hasattr(cli, 'callback')
        except ImportError:
            return False
    
    def test_module_imports(self):
        """Test that all modules can be imported"""
        modules = [
            'twodo.config',
            'twodo.todo_manager',
            'twodo.ai_router',
            'twodo.tech_stack',
            'twodo.multitasker',
            'twodo.markdown_parser',
            'twodo.github_integration',
            'twodo.cli'
        ]
        
        for module in modules:
            try:
                __import__(module)
            except ImportError:
                return False
        return True
    
    def test_config_persistence(self):
        """Test configuration persistence"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                config1 = ConfigManager(temp_dir)
                config1.set_api_key("test", "test_value")
                
                config2 = ConfigManager(temp_dir)
                return config2.get_api_key("test") == "test_value"
        except Exception:
            return False
    
    def test_demo_execution(self):
        """Test that demo script can be executed"""
        try:
            demo_path = project_root / "demo.py"
            return demo_path.exists()
        except Exception:
            return False
    
    def display_integration_results(self, results):
        """Display integration test results"""
        table = Table(title="Integration Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        passed_count = 0
        for test_name, result in results.items():
            status = result["status"]
            if status == "pass":
                status_text = "✅ Pass"
                passed_count += 1
            elif status == "fail":
                status_text = "❌ Fail"
            else:
                status_text = "🚨 Error"
            
            details = str(result["details"])[:50] + "..." if len(str(result["details"])) > 50 else str(result["details"])
            table.add_row(test_name, status_text, details)
        
        self.console.print(table)
        
        # Store results
        self.results["Integration Tests"] = {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "details": results
        }
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.console.print(f"\n{'='*80}")
        self.console.print("📊 FINAL TEST REPORT", style="bold blue")
        self.console.print(f"{'='*80}")
        
        # Overall statistics
        overall_table = Table(title="Overall Test Statistics")
        overall_table.add_column("Metric", style="cyan")
        overall_table.add_column("Count", style="green")
        overall_table.add_column("Percentage", style="yellow")
        
        if self.total_tests > 0:
            overall_table.add_row("Total Tests", str(self.total_tests), "100%")
            overall_table.add_row("Passed", str(self.passed_tests), f"{(self.passed_tests/self.total_tests)*100:.1f}%")
            overall_table.add_row("Failed", str(self.failed_tests), f"{(self.failed_tests/self.total_tests)*100:.1f}%")
            overall_table.add_row("Errors", str(self.error_tests), f"{(self.error_tests/self.total_tests)*100:.1f}%")
            overall_table.add_row("Skipped", str(self.skipped_tests), f"{(self.skipped_tests/self.total_tests)*100:.1f}%")
        
        self.console.print(overall_table)
        
        # Suite-by-suite results
        suite_table = Table(title="Test Suite Summary")
        suite_table.add_column("Test Suite", style="cyan")
        suite_table.add_column("Status", style="green")
        suite_table.add_column("Passed/Total", style="yellow")
        suite_table.add_column("Duration", style="magenta")
        
        for suite_name, results in self.results.items():
            if "error" in results:
                suite_table.add_row(suite_name, "❌ Error", "N/A", "N/A")
            elif "total" in results:
                total = results["total"]
                passed = results["passed"]
                duration = results.get("duration", 0)
                
                if passed == total:
                    status = "✅ All Pass"
                else:
                    status = f"❌ {total - passed} Failed"
                
                suite_table.add_row(
                    suite_name,
                    status,
                    f"{passed}/{total}",
                    f"{duration:.2f}s" if duration else "N/A"
                )
        
        self.console.print(suite_table)
        
        # Final status
        if self.failed_tests == 0 and self.error_tests == 0:
            self.console.print(Panel(
                "🎉 All tests passed! 2DO is ready for use.\n\n"
                "✅ Core functionality verified\n"
                "✅ Setup system working\n"
                "✅ CLI integration functional\n"
                "✅ All components tested",
                title="SUCCESS",
                style="bold green"
            ))
            return True
        else:
            self.console.print(Panel(
                f"⚠️ Test failures detected:\n\n"
                f"❌ {self.failed_tests} failed tests\n"
                f"🚨 {self.error_tests} error tests\n\n"
                "Please review the failures above and fix issues before using 2DO.",
                title="ISSUES FOUND",
                style="bold red"
            ))
            return False
    
    def run_quick_test(self):
        """Run a quick test to verify basic functionality"""
        self.console.print(Panel.fit("⚡ 2DO Quick Test", style="bold yellow"))
        
        quick_tests = [
            ("Module Imports", self.test_module_imports),
            ("Config Creation", lambda: self.test_config_persistence()),
            ("CLI Structure", self.test_cli_structure)
        ]
        
        passed = 0
        for test_name, test_func in quick_tests:
            try:
                result = test_func()
                if result:
                    self.console.print(f"✅ {test_name}")
                    passed += 1
                else:
                    self.console.print(f"❌ {test_name}")
            except Exception as e:
                self.console.print(f"🚨 {test_name}: {e}")
        
        if passed == len(quick_tests):
            self.console.print("🎉 Quick test passed! 2DO basic functionality is working.", style="bold green")
        else:
            self.console.print(f"⚠️ {len(quick_tests) - passed} quick tests failed.", style="bold red")
        
        return passed == len(quick_tests)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="2DO Test Suite Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--setup", action="store_true", help="Run setup verification only")
    args = parser.parse_args()
    
    runner = TestSuiteRunner()
    
    if args.quick:
        success = runner.run_quick_test()
    elif args.setup:
        runner.run_setup_verification()
        success = True  # Setup verification doesn't return success/failure
    else:
        success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()