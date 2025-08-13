"""
GitHub Integration - Handles GitHub repository operations, issues, and pull requests
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from github import Github, GithubException
from git import Repo, GitCommandError
from rich.console import Console

console = Console()

class GitHubIntegration:
    """Handles GitHub operations for AI Redirector"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.github = None
        if self.github_token:
            try:
                self.github = Github(self.github_token)
                # Test connection
                self.github.get_user().login
                console.print("✅ GitHub connection established")
            except Exception as e:
                console.print(f"❌ GitHub connection failed: {type(e).__name__}")
                self.github = None
        else:
            console.print("⚠️  No GitHub token provided. GitHub features will be limited.")
    
    def get_repository_info(self, repo_path: str) -> Optional[Dict]:
        """Get repository information from local git repo"""
        try:
            repo = Repo(repo_path)
            if repo.remotes:
                origin_url = repo.remotes.origin.url
                # Parse GitHub URL
                github_info = self._parse_github_url(origin_url)
                if github_info:
                    github_info['local_path'] = repo_path
                    github_info['current_branch'] = repo.active_branch.name
                    github_info['is_dirty'] = repo.is_dirty()
                    return github_info
        except Exception as e:
            console.print(f"⚠️  Could not get repository info: {e}")
        return None
    
    def _parse_github_url(self, url: str) -> Optional[Dict]:
        """Parse GitHub URL to extract owner and repo name"""
        # Handle both HTTPS and SSH URLs
        patterns = [
            r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                owner, repo_name = match.groups()
                return {
                    'owner': owner,
                    'repo_name': repo_name,
                    'full_name': f"{owner}/{repo_name}",
                    'url': url
                }
        return None
    
    def get_repository_issues(self, owner: str, repo_name: str, state: str = "open") -> List[Dict]:
        """Get issues from GitHub repository"""
        if not self.github:
            console.print("❌ GitHub connection not available")
            return []
        
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            issues = repo.get_issues(state=state)
            
            issue_list = []
            for issue in issues:
                if not issue.pull_request:  # Exclude pull requests
                    issue_data = {
                        'number': issue.number,
                        'title': issue.title,
                        'body': issue.body or "",
                        'state': issue.state,
                        'labels': [label.name for label in issue.labels],
                        'assignees': [assignee.login for assignee in issue.assignees],
                        'created_at': issue.created_at.isoformat(),
                        'updated_at': issue.updated_at.isoformat(),
                        'url': issue.html_url,
                        'user': issue.user.login
                    }
                    issue_list.append(issue_data)
            
            return issue_list
        
        except GithubException as e:
            console.print(f"❌ Failed to get issues: {e}")
            return []
    
    def create_issue(self, owner: str, repo_name: str, title: str, body: str, labels: List[str] = None) -> Optional[Dict]:
        """Create a new GitHub issue"""
        if not self.github:
            console.print("❌ GitHub connection not available")
            return None
        
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            
            return {
                'number': issue.number,
                'title': issue.title,
                'url': issue.html_url,
                'created_at': issue.created_at.isoformat()
            }
        
        except GithubException as e:
            console.print(f"❌ Failed to create issue: {e}")
            return None
    
    def create_branch_for_issue(self, repo_path: str, issue_number: int, issue_title: str) -> bool:
        """Create a new branch for working on an issue"""
        try:
            repo = Repo(repo_path)
            
            # Ensure we're on main/master and up to date
            main_branch = self._get_main_branch(repo)
            repo.git.checkout(main_branch)
            
            # Create branch name from issue
            branch_name = f"issue-{issue_number}-{self._sanitize_branch_name(issue_title)}"
            
            # Create and checkout new branch
            repo.git.checkout('-b', branch_name)
            console.print(f"✅ Created and checked out branch: {branch_name}")
            return True
        
        except GitCommandError as e:
            console.print(f"❌ Failed to create branch: {e}")
            return False
    
    def _get_main_branch(self, repo: Repo) -> str:
        """Get the main branch name (main or master)"""
        try:
            repo.git.checkout('main')
            return 'main'
        except GitCommandError:
            try:
                repo.git.checkout('master')
                return 'master'
            except GitCommandError:
                # Return current branch as fallback
                return repo.active_branch.name
    
    def _sanitize_branch_name(self, title: str) -> str:
        """Sanitize issue title for use in branch name"""
        # Convert to lowercase, replace spaces and special chars with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', title.lower())
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        # Limit length and remove trailing hyphens
        return sanitized[:30].strip('-')
    
    def create_pull_request(self, repo_path: str, owner: str, repo_name: str, title: str, body: str, 
                          base_branch: str = "main") -> Optional[Dict]:
        """Create a pull request from current branch"""
        if not self.github:
            console.print("❌ GitHub connection not available")
            return None
        
        try:
            repo_local = Repo(repo_path)
            current_branch = repo_local.active_branch.name
            
            if current_branch == base_branch:
                console.print(f"❌ Cannot create PR: currently on {base_branch} branch")
                return None
            
            # Push current branch to origin
            repo_local.git.push('origin', current_branch)
            
            # Create pull request
            repo_github = self.github.get_repo(f"{owner}/{repo_name}")
            pr = repo_github.create_pull(
                title=title,
                body=body,
                head=current_branch,
                base=base_branch
            )
            
            return {
                'number': pr.number,
                'title': pr.title,
                'url': pr.html_url,
                'created_at': pr.created_at.isoformat(),
                'head_branch': current_branch,
                'base_branch': base_branch
            }
        
        except Exception as e:
            console.print(f"❌ Failed to create pull request: {e}")
            return None
    
    def work_on_issue(self, repo_path: str, owner: str, repo_name: str, issue_number: int) -> bool:
        """Setup to work on a specific issue (create branch, etc.)"""
        # Get issue details
        issues = self.get_repository_issues(owner, repo_name, "open")
        issue = next((i for i in issues if i['number'] == issue_number), None)
        
        if not issue:
            console.print(f"❌ Issue #{issue_number} not found")
            return False
        
        console.print(f"🎯 Working on issue #{issue_number}: {issue['title']}")
        
        # Create branch for issue
        success = self.create_branch_for_issue(repo_path, issue_number, issue['title'])
        
        if success:
            console.print(f"📝 Issue details:")
            console.print(f"   Title: {issue['title']}")
            console.print(f"   Labels: {', '.join(issue['labels'])}")
            console.print(f"   URL: {issue['url']}")
            if issue['body']:
                console.print(f"   Description: {issue['body'][:200]}...")
        
        return success
    
    def create_todos_from_issues(self, owner: str, repo_name: str, todo_manager, 
                                state: str = "open", priority: str = "medium") -> List[str]:
        """Create todos from GitHub issues"""
        issues = self.get_repository_issues(owner, repo_name, state)
        
        if not issues:
            console.print("📝 No issues found")
            return []
        
        todo_ids = []
        for issue in issues:
            # Create todo from issue
            todo_id = todo_manager.add_todo(
                title=f"GitHub Issue #{issue['number']}: {issue['title']}",
                description=f"Work on GitHub issue in {owner}/{repo_name}",
                todo_type="code",
                priority=priority,
                content=f"Issue URL: {issue['url']}\nLabels: {', '.join(issue['labels'])}\n\n{issue['body'][:500]}"
            )
            todo_ids.append(todo_id)
        
        console.print(f"✅ Created {len(todo_ids)} todos from GitHub issues")
        return todo_ids
    
    def finish_issue_work(self, repo_path: str, owner: str, repo_name: str, 
                         issue_number: int, commit_message: str) -> Optional[Dict]:
        """Finish work on an issue and create pull request"""
        try:
            repo = Repo(repo_path)
            current_branch = repo.active_branch.name
            
            # Check if there are changes to commit
            if repo.is_dirty() or repo.untracked_files:
                # Add all changes
                repo.git.add('-A')
                
                # Commit changes
                full_commit_message = f"{commit_message}\n\nCloses #{issue_number}"
                repo.git.commit('-m', full_commit_message)
                console.print(f"✅ Committed changes: {commit_message}")
            
            # Create pull request
            pr_title = f"Fix issue #{issue_number}"
            pr_body = f"This PR addresses issue #{issue_number}.\n\n{commit_message}\n\nCloses #{issue_number}"
            
            pr_info = self.create_pull_request(
                repo_path, owner, repo_name, pr_title, pr_body
            )
            
            if pr_info:
                console.print(f"✅ Created pull request: {pr_info['url']}")
                return pr_info
            
        except Exception as e:
            console.print(f"❌ Failed to finish issue work: {e}")
        
        return None
    
    def create_subtasks_as_issues(self, owner: str, repo_name: str, parent_todo: Dict, sub_tasks: List[Dict]) -> List[Dict]:
        """Create sub-tasks as GitHub issues linked to a parent issue"""
        if not self.github:
            console.print("❌ GitHub connection not available")
            return []
        
        created_issues = []
        
        # Extract parent issue number if it's from a GitHub issue
        parent_issue_number = None
        if "GitHub Issue #" in parent_todo.get("title", ""):
            import re
            match = re.search(r'GitHub Issue #(\d+)', parent_todo["title"])
            if match:
                parent_issue_number = int(match.group(1))
        
        for sub_task in sub_tasks:
            try:
                # Create issue title and body
                if parent_issue_number:
                    title = f"Sub-task of #{parent_issue_number}: {sub_task['title']}"
                    body = f"This is a sub-task of issue #{parent_issue_number}.\n\n"
                else:
                    title = f"Sub-task: {sub_task['title']}"
                    body = f"This is a sub-task of: {parent_todo['title']}\n\n"
                
                body += f"**Description:** {sub_task['description']}\n\n"
                if sub_task.get('content'):
                    body += f"**Additional Context:** {sub_task['content']}\n\n"
                
                body += f"**Priority:** {sub_task['priority']}\n"
                body += f"**Type:** {sub_task['todo_type']}\n"
                
                # Add labels for sub-tasks
                labels = ["sub-task", f"priority-{sub_task['priority']}", f"type-{sub_task['todo_type']}"]
                
                # Create the issue
                issue_info = self.create_issue(owner, repo_name, title, body, labels)
                
                if issue_info:
                    created_issues.append({
                        'todo_id': sub_task['id'],
                        'issue_number': issue_info['number'],
                        'issue_url': issue_info['url'],
                        'title': issue_info['title']
                    })
                    console.print(f"✅ Created issue #{issue_info['number']}: {sub_task['title']}")
                
            except Exception as e:
                console.print(f"❌ Failed to create issue for sub-task {sub_task['title']}: {e}")
        
        return created_issues
    
    def export_todo_with_subtasks_to_github(self, owner: str, repo_name: str, todo: Dict, todo_manager) -> Dict:
        """Export a todo and its sub-tasks as GitHub issues"""
        results = {
            'parent_issue': None,
            'sub_issues': [],
            'success': False
        }
        
        try:
            # First create the parent issue
            parent_title = todo['title']
            parent_body = f"**Description:** {todo['description']}\n\n"
            
            if todo.get('content'):
                parent_body += f"**Additional Context:** {todo['content']}\n\n"
            
            parent_body += f"**Priority:** {todo['priority']}\n"
            parent_body += f"**Type:** {todo['todo_type']}\n"
            
            # Check if this todo has sub-tasks
            sub_tasks = todo_manager.get_sub_tasks(todo['id'])
            if sub_tasks:
                parent_body += f"\n**Sub-tasks ({len(sub_tasks)} items):**\n"
                for i, sub_task in enumerate(sub_tasks, 1):
                    parent_body += f"{i}. {sub_task['title']}\n"
                parent_body += "\n*Note: Sub-tasks will be created as separate linked issues.*"
            
            # Create parent issue
            parent_labels = [f"priority-{todo['priority']}", f"type-{todo['todo_type']}"]
            if sub_tasks:
                parent_labels.append("has-subtasks")
            
            parent_issue = self.create_issue(owner, repo_name, parent_title, parent_body, parent_labels)
            
            if parent_issue:
                results['parent_issue'] = parent_issue
                console.print(f"✅ Created parent issue #{parent_issue['number']}: {parent_title}")
                
                # Create sub-task issues if any exist
                if sub_tasks:
                    # Update the parent todo title to include GitHub issue reference
                    updated_parent_todo = todo.copy()
                    updated_parent_todo['title'] = f"GitHub Issue #{parent_issue['number']}: {todo['title']}"
                    
                    sub_issues = self.create_subtasks_as_issues(owner, repo_name, updated_parent_todo, sub_tasks)
                    results['sub_issues'] = sub_issues
                    
                    if sub_issues:
                        # Update parent issue with links to sub-issues
                        parent_body += f"\n\n**Created Sub-task Issues:**\n"
                        for sub_issue in sub_issues:
                            parent_body += f"- #{sub_issue['issue_number']}: {sub_issue['title']}\n"
                        
                        # Note: We could update the parent issue here if needed
                        console.print(f"✅ Created {len(sub_issues)} sub-task issues")
                
                results['success'] = True
                
        except Exception as e:
            console.print(f"❌ Failed to export todo with sub-tasks: {e}")
        
        return results