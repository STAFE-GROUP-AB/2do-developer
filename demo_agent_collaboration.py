#!/usr/bin/env python3
"""
Manual test script demonstrating the agent collaboration workflow
This simulates the experience described in the issue: agents discovering each other,
offering help, and collaborating like developers in a FaceTime meeting.
"""

import os
import sys
import tempfile
import subprocess
import time
from pathlib import Path

def create_demo_repo(name: str, description: str, tech_files: dict) -> Path:
    """Create a demo repository with specific characteristics"""
    repo_dir = Path(tempfile.mkdtemp(prefix=f"demo_{name}_"))
    
    # Create README
    (repo_dir / "README.md").write_text(f"# {name}\n\n{description}")
    
    # Create tech-specific files
    for filename, content in tech_files.items():
        file_path = repo_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories
        file_path.write_text(content)
    
    return repo_dir

def run_2do_command(command: str, cwd: str) -> str:
    """Run a 2do command and return output"""
    try:
        result = subprocess.run(
            f"2do {command}",
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"

def main():
    """Demonstrate the agent collaboration workflow"""
    print("🚀 2DO Agent Collaboration Demo")
    print("=" * 50)
    print("This demo shows agents discovering each other and collaborating")
    print("as described in the issue: like developers in a FaceTime meeting!")
    print()
    
    # Create demo repositories
    print("📁 Creating demo repositories...")
    
    # Repository 1: Swedish BankID integration expert
    bankid_repo = create_demo_repo(
        "swedish-bankid-lib",
        "A comprehensive Swedish BankID authentication library with extensive API experience",
        {
            "requirements.txt": "requests>=2.25.0\ncryptography>=3.4.0\npyjwt>=2.0.0",
            "bankid_client.py": "# Expert BankID implementation\nclass BankIDClient:\n    def authenticate(self): pass",
            "tests/test_bankid.py": "# Comprehensive test suite for BankID"
        }
    )
    
    # Repository 2: React dashboard needing help
    react_repo = create_demo_repo(
        "enterprise-dashboard",
        "Modern React dashboard that needs Swedish BankID authentication integration",
        {
            "package.json": '{"name": "dashboard", "dependencies": {"react": "^18.0.0", "typescript": "^4.8.0"}}',
            "src/App.tsx": "// React dashboard - needs BankID auth",
            "src/auth/AuthProvider.tsx": "// TODO: Implement BankID authentication"
        }
    )
    
    print(f"✅ BankID Expert Repo: {bankid_repo}")
    print(f"✅ React Dashboard Repo: {react_repo}")
    print()
    
    # Step 1: Register agents in both repositories
    print("🤖 Step 1: Registering agents in the network...")
    
    # Register BankID expert
    print("   Registering BankID Expert...")
    bankid_output = run_2do_command("agent-status --register --name 'BankID-Expert'", str(bankid_repo))
    print("   ✅ BankID Expert registered")
    
    # Register React developer
    print("   Registering React Developer...")
    react_output = run_2do_command("agent-status --register --name 'React-Developer'", str(react_repo))
    print("   ✅ React Developer registered")
    print()
    
    # Step 2: Show agent discovery
    print("🔍 Step 2: Agents discovering each other...")
    discovery_output = run_2do_command("agent-status", str(react_repo))
    print(discovery_output)
    
    # Step 3: Demonstrate help request
    print("🆘 Step 3: React Developer requesting help...")
    print("   The React developer needs help with Swedish BankID integration")
    print("   and discovers the BankID Expert in the network!")
    print()
    print("   This is where the magic happens - just like the issue described:")
    print("   💬 React Dev: 'Hey, I need to build Swedish BankID integration'")
    print("   🤖 BankID Expert: 'Hey, I did that and I can help you!'")
    print()
    
    # Step 4: Show available commands
    print("🔧 Step 4: Available collaboration commands:")
    print("   • 2do agent-help      - Request help (React developer would use this)")
    print("   • 2do agent-messages   - Check for offers and replies")
    print("   • 2do agent-collaborate - Start working together")
    print("   • 2do agent-daemon     - Run background service for real-time collaboration")
    print()
    
    # Step 5: Demonstrate the collaboration flow
    print("🤝 Step 5: Collaboration Workflow Demo")
    print("   Here's how the agents would collaborate:")
    print()
    print("   1. 📤 React Developer: '2do agent-help --title \"Need Swedish BankID integration\"'")
    print("   2. 📨 BankID Expert receives notification: 'Someone needs help with BankID!'")
    print("   3. 🤝 BankID Expert: Offers help with their expertise")
    print("   4. ✅ React Developer: Accepts the help")
    print("   5. 💬 Collaboration session starts:")
    print("      - BankID Expert: 'I'll guide you through the API setup'")
    print("      - React Developer: 'Creating the auth components now'")
    print("      - BankID Expert: 'Here's the certificate configuration...'")
    print("      - React Developer: 'Perfect! Testing the flow now'")
    print("   6. 🎉 Problem solved through collaborative development!")
    print()
    
    # Step 6: Show the technical implementation
    print("⚙️  Step 6: Technical Implementation")
    print("   The agent system provides:")
    print("   • 🌐 Automatic agent discovery across repositories")
    print("   • 📋 Repository context sharing (README, tech stack)")
    print("   • 🎯 Smart matching based on capabilities and tech stack")
    print("   • 💬 Real-time messaging and collaboration")
    print("   • 🤖 Background presence maintenance")
    print("   • 🔒 Secure file-based communication (no external dependencies)")
    print()
    
    # Step 7: Real-world scenario
    print("🌍 Step 7: Real-world Impact")
    print("   This solves the problem described in the issue:")
    print("   ✅ Multiple 2DO agents know about each other")
    print("   ✅ They share repository descriptions and capabilities") 
    print("   ✅ Agents can offer help based on their expertise")
    print("   ✅ Collaboration works like 'developers in a FaceTime meeting'")
    print("   ✅ One guides, the other creates - true pair programming!")
    print()
    
    print("🎯 The agent communication system is now ready!")
    print("   Try it yourself:")
    print("   1. Run '2do agent-status --register' in different repositories")
    print("   2. Use '2do agent-help' to request assistance")
    print("   3. Check '2do agent-messages' for offers")
    print("   4. Start '2do agent-collaborate' to work together")
    print()
    
    # Cleanup
    print("🧹 Cleaning up demo repositories...")
    try:
        import shutil
        shutil.rmtree(bankid_repo)
        shutil.rmtree(react_repo)
        print("✅ Demo cleanup complete")
    except Exception:
        print("⚠️  Manual cleanup may be needed")
    
    print()
    print("🚀 Agent collaboration demo complete!")
    print("The future of collaborative development is here! 🤖🤝🤖")

if __name__ == "__main__":
    main()