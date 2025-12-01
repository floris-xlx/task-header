"""
Markdown file generation and synchronization with Linear.
Generates markdown files with checkboxes that can sync back to Linear.
"""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MarkdownSync:
    """Handles markdown file generation and synchronization."""
    
    def __init__(self, config, linear_client=None):
        """
        Initialize markdown sync.
        
        Args:
            config: Config instance
            linear_client: LinearClient instance (optional)
        """
        self.config = config
        self.linear_client = linear_client
        self.output_dir = config.get("markdown.output_dir", ".")
        self.observer: Optional[Observer] = None
    
    def generate_my_issues_md(self, issues: List[Dict[str, Any]]) -> str:
        """
        Generate my-issues.md file.
        
        Args:
            issues: List of issues
            
        Returns:
            Path to generated file
        """
        filepath = os.path.join(self.output_dir, "my-issues.md")
        
        content = self._generate_markdown_content(
            "My Issues",
            issues,
            "All issues assigned to me"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def generate_team_issues_md(self, team_name: str, issues: List[Dict[str, Any]]) -> str:
        """
        Generate issues-{team}.md file.
        
        Args:
            team_name: Team name
            issues: List of issues
            
        Returns:
            Path to generated file
        """
        # Sanitize team name for filename
        safe_name = re.sub(r'[^\w\-]', '_', team_name.lower())
        filepath = os.path.join(self.output_dir, f"issues-{safe_name}.md")
        
        content = self._generate_markdown_content(
            f"Issues: {team_name}",
            issues,
            f"All issues for team {team_name}"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def generate_project_issues_md(self, project_name: str, issues: List[Dict[str, Any]]) -> str:
        """
        Generate issues-{project}.md file.
        
        Args:
            project_name: Project name
            issues: List of issues
            
        Returns:
            Path to generated file
        """
        # Sanitize project name for filename
        safe_name = re.sub(r'[^\w\-]', '_', project_name.lower())
        filepath = os.path.join(self.output_dir, f"issues-{safe_name}.md")
        
        content = self._generate_markdown_content(
            f"Issues: {project_name}",
            issues,
            f"All issues for project {project_name}"
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _generate_markdown_content(
        self, 
        title: str, 
        issues: List[Dict[str, Any]],
        description: str = ""
    ) -> str:
        """
        Generate markdown content from issues.
        
        Args:
            title: Document title
            issues: List of issues
            description: Document description
            
        Returns:
            Markdown content
        """
        lines = [
            f"# {title}",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ]
        
        if description:
            lines.extend([description, ""])
        
        lines.append("---")
        lines.append("")
        
        # Group issues by state type
        grouped_issues = self._group_issues_by_state(issues)
        
        for state_type, state_issues in grouped_issues.items():
            lines.append(f"## {state_type.title()}")
            lines.append("")
            
            for issue in state_issues:
                checkbox = self._get_checkbox(issue)
                identifier = issue.get('identifier', 'N/A')
                title = issue.get('title', 'No title')
                state_name = issue.get('state', {}).get('name', 'Unknown')
                issue_id = issue.get('id', '')
                
                # Format: - [x] IDENTIFIER: Title [State] <!-- id:issue_id -->
                line = f"{checkbox} **{identifier}**: {title} *[{state_name}]* <!-- id:{issue_id} -->"
                lines.append(line)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _group_issues_by_state(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group issues by state type.
        
        Args:
            issues: List of issues
            
        Returns:
            Dictionary of state type to issues
        """
        grouped = {
            "backlog": [],
            "unstarted": [],
            "started": [],
            "completed": [],
            "canceled": []
        }
        
        for issue in issues:
            state_type = issue.get('state', {}).get('type', 'unstarted')
            
            if state_type in grouped:
                grouped[state_type].append(issue)
            else:
                # Default to unstarted if unknown state type
                grouped['unstarted'].append(issue)
        
        # Remove empty groups
        return {k: v for k, v in grouped.items() if v}
    
    def _get_checkbox(self, issue: Dict[str, Any]) -> str:
        """
        Get checkbox markdown based on issue state.
        
        Args:
            issue: Issue data
            
        Returns:
            Checkbox string
        """
        state_type = issue.get('state', {}).get('type', 'unstarted')
        
        if state_type in ['completed', 'canceled']:
            return "- [x]"
        else:
            return "- [ ]"
    
    def parse_markdown_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse markdown file and extract issue states.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            List of issue updates (id and new state)
        """
        if not os.path.exists(filepath):
            return []
        
        updates = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match: - [x] or - [ ] ... <!-- id:issue_id -->
        pattern = r'- \[([ x])\].*?<!-- id:(\S+) -->'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            checked = match.group(1) == 'x'
            issue_id = match.group(2)
            
            updates.append({
                'id': issue_id,
                'completed': checked
            })
        
        return updates
    
    def sync_markdown_to_linear(self, filepath: str) -> int:
        """
        Sync markdown file changes back to Linear.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            Number of issues updated
        """
        if not self.linear_client:
            raise Exception("Linear client not configured")
        
        updates = self.parse_markdown_file(filepath)
        updated_count = 0
        
        for update in updates:
            issue_id = update['id']
            should_be_completed = update['completed']
            
            try:
                # Get current issue state
                issue = self.linear_client.get_issue(issue_id)
                current_state = issue.get('state', {})
                current_type = current_state.get('type', '')
                
                # Determine if we need to update
                is_completed = current_type in ['completed', 'canceled']
                
                if should_be_completed and not is_completed:
                    # Mark as completed
                    team_id = issue.get('team', {}).get('id')
                    if team_id:
                        states = self.linear_client.get_workflow_states(team_id)
                        completed_state = next(
                            (s for s in states if s['type'] == 'completed'),
                            None
                        )
                        
                        if completed_state:
                            self.linear_client.update_issue_state(
                                issue_id,
                                completed_state['id']
                            )
                            updated_count += 1
                
                elif not should_be_completed and is_completed:
                    # Mark as not completed (reopen)
                    team_id = issue.get('team', {}).get('id')
                    if team_id:
                        states = self.linear_client.get_workflow_states(team_id)
                        unstarted_state = next(
                            (s for s in states if s['type'] == 'unstarted'),
                            None
                        )
                        
                        if unstarted_state:
                            self.linear_client.update_issue_state(
                                issue_id,
                                unstarted_state['id']
                            )
                            updated_count += 1
            
            except Exception as e:
                print(f"Error updating issue {issue_id}: {e}")
        
        return updated_count
    
    def start_watching(self, filepath: str, callback=None):
        """
        Start watching markdown file for changes.
        
        Args:
            filepath: Path to watch
            callback: Optional callback when file changes
        """
        if not self.config.get("markdown.sync_on_edit", True):
            return
        
        class MarkdownFileHandler(FileSystemEventHandler):
            def __init__(self, sync_handler, target_file, cb):
                self.sync_handler = sync_handler
                self.target_file = os.path.abspath(target_file)
                self.callback = cb
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                if os.path.abspath(event.src_path) == self.target_file:
                    print(f"Markdown file modified: {event.src_path}")
                    try:
                        count = self.sync_handler.sync_markdown_to_linear(event.src_path)
                        print(f"Synced {count} issues to Linear")
                        
                        if self.callback:
                            self.callback(count)
                    except Exception as e:
                        print(f"Error syncing: {e}")
        
        # Stop existing observer
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        # Start new observer
        event_handler = MarkdownFileHandler(self, filepath, callback)
        self.observer = Observer()
        
        watch_dir = os.path.dirname(os.path.abspath(filepath))
        self.observer.schedule(event_handler, watch_dir, recursive=False)
        self.observer.start()
    
    def stop_watching(self):
        """Stop watching markdown files."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

