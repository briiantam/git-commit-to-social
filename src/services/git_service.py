"""Git service for monitoring commits."""
import os
import logging
from datetime import datetime
import git
from ..config.config import REPO_PATH
from ..models.database import store_commit, commit_exists

class GitService:
    """Service for monitoring git repositories for commits."""
    
    def __init__(self, repo_path=REPO_PATH):
        """Initialize the GitService."""
        self.repo_path = repo_path
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize the git repository."""
        try:
            self.repo = git.Repo(self.repo_path)
            logging.info(f"Git repository initialized at {self.repo_path}")
        except git.exc.InvalidGitRepositoryError:
            logging.error(f"Invalid git repository at {self.repo_path}")
            raise
    
    def update_repo(self):
        """Update the local repository."""
        try:
            self.repo.remotes.origin.pull()
            logging.info("Repository updated successfully")
        except Exception as e:
            logging.error(f"Failed to update repository: {str(e)}")
            raise
    
    def get_todays_commits(self):
        """Get all commits made today."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            commits = list(self.repo.iter_commits(
                since=f"{today} 00:00:00",
                until=f"{today} 23:59:59"
            ))
            
            logging.info(f"Found {len(commits)} commits made today")
            return commits
        except Exception as e:
            logging.error(f"Failed to get today's commits: {str(e)}")
            raise
    
    def get_commit_diff(self, commit):
        """
        Get detailed diff content for a commit.
        
        Args:
            commit: A git.Commit object
            
        Returns:
            str: A string containing the diff content
        """
        try:
            parent = commit.parents[0] if commit.parents else None
            
            if not parent:
                return "Initial commit - no diff available"
            
            diffs = parent.diff(commit)
            
            diff_summaries = []
            for diff_item in diffs:
                diff_summary = f"File: {diff_item.a_path}\n"
                diff_summary += f"Change type: {diff_item.change_type}\n"
                
                if diff_item.change_type == 'R':
                    diff_summary += f"Renamed to: {diff_item.b_path}\n"
                
                if diff_item.change_type in ['A', 'M', 'R']:
                    if diff_item.b_blob:
                        # Get the raw diff content
                        try:
                            if hasattr(diff_item, 'diff'):
                                diff_content = diff_item.diff
                                if isinstance(diff_content, bytes):
                                    diff_text = diff_content.decode('utf-8', errors='replace')
                                else:
                                    diff_text = str(diff_content)
                            else:
                                a_blob = diff_item.a_blob.data_stream.read().decode('utf-8', errors='replace') if diff_item.a_blob else ""
                                b_blob = diff_item.b_blob.data_stream.read().decode('utf-8', errors='replace') if diff_item.b_blob else ""
                                
                                if diff_item.change_type == 'A':
                                    diff_text = f"+++ {diff_item.b_path}\n{b_blob}"
                                elif diff_item.change_type == 'M':
                                    diff_text = f"--- {diff_item.a_path}\n+++ {diff_item.b_path}\n"
                                    a_lines = a_blob.split('\n')
                                    b_lines = b_blob.split('\n')
                                    
                                    diff_text += f"First 20 lines of original file:\n{a_blob.split('\n')[:20]}\n"
                                    diff_text += f"First 20 lines of modified file:\n{b_blob.split('\n')[:20]}\n"
                                else:
                                    diff_text = f"--- {diff_item.a_path}\n+++ {diff_item.b_path}\n"
                            
                            lines = diff_text.split('\n')
                            added_lines = []
                            deleted_lines = []
                            context_lines = []
                            
                            for line in lines:
                                if line.startswith('+') and not line.startswith('+++'):
                                    added_lines.append(line[1:])
                                elif line.startswith('-') and not line.startswith('---'):
                                    deleted_lines.append(line[1:])
                                elif not line.startswith('@@') and not line.startswith('diff') and not line.startswith('index'):
                                    context_lines.append(line)
                            
                            if deleted_lines:
                                diff_summary += "\nCode removed:\n```\n"
                                diff_summary += "\n".join(deleted_lines[:20])  # Limit to 20 lines
                                if len(deleted_lines) > 20:
                                    diff_summary += "\n... (more lines omitted)"
                                diff_summary += "\n```\n"
                            
                            if added_lines:
                                diff_summary += "\nCode added:\n```\n"
                                diff_summary += "\n".join(added_lines[:20])  # Limit to 20 lines
                                if len(added_lines) > 20:
                                    diff_summary += "\n... (more lines omitted)"
                                diff_summary += "\n```\n"
                            
                            if context_lines and len(context_lines) > 2:
                                diff_summary += "\nContext:\n```\n"
                                diff_summary += "\n".join(context_lines[:5])  # Limit to 5 lines
                                if len(context_lines) > 5:
                                    diff_summary += "\n... (more lines omitted)"
                                diff_summary += "\n```\n"
                                
                            if not (added_lines or deleted_lines) and diff_item.b_blob:
                                diff_summary += "\nFile content (first 20 lines):\n```\n"
                                content = diff_item.b_blob.data_stream.read().decode('utf-8', errors='replace')
                                content_lines = content.split('\n')[:20]
                                diff_summary += "\n".join(content_lines)
                                if len(content.split('\n')) > 20:
                                    diff_summary += "\n... (more lines omitted)"
                                diff_summary += "\n```\n"
                                
                        except Exception as inner_e:
                            logging.warning(f"Error parsing diff for {diff_item.a_path}: {str(inner_e)}")
                            if diff_item.b_blob:
                                diff_summary += "\nFile content (first 20 lines):\n```\n"
                                try:
                                    content = diff_item.b_blob.data_stream.read().decode('utf-8', errors='replace')
                                    content_lines = content.split('\n')[:20]
                                    diff_summary += "\n".join(content_lines)
                                    if len(content.split('\n')) > 20:
                                        diff_summary += "\n... (more lines omitted)"
                                except Exception as content_e:
                                    diff_summary += f"Error reading file content: {str(content_e)}"
                                diff_summary += "\n```\n"
                
                elif diff_item.change_type == 'D':
                    diff_summary += "\nEntire file was deleted\n"
                    if diff_item.a_blob:
                        try:
                            content = diff_item.a_blob.data_stream.read().decode('utf-8', errors='replace')
                            diff_summary += "Content summary (first 10 lines):\n```\n"
                            content_lines = content.split('\n')[:10]
                            diff_summary += "\n".join(content_lines)
                            if len(content.split('\n')) > 10:
                                diff_summary += "\n... (more lines omitted)"
                        except Exception as content_e:
                            diff_summary += f"Error reading file content: {str(content_e)}"
                        diff_summary += "\n```\n"
                
                diff_summaries.append(diff_summary)
            
            return "\n---\n".join(diff_summaries)
        except Exception as e:
            logging.error(f"Failed to get diff for commit {commit.hexsha}: {str(e)}")
            return f"Error getting diff: {str(e)}"
    
    def process_new_commits(self):
        """Process new commits and store them in the database."""
        try:
            self.update_repo()
            commits = self.get_todays_commits()
            
            processed_count = 0
            for commit in commits:
                if commit_exists(commit.hexsha):
                    continue
                
                files_changed = []
                stats = commit.stats.files
                
                for file_path, file_stats in stats.items():
                    files_changed.append(file_path)
                
                diff_content = self.get_commit_diff(commit)
                
                store_commit(
                    commit_id=commit.hexsha,
                    author=commit.author.name,
                    message=commit.message,
                    timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                    files_changed=files_changed,
                    insertions=commit.stats.total["insertions"],
                    deletions=commit.stats.total["deletions"],
                    diff_content=diff_content
                )
                
                processed_count += 1
            
            return processed_count
        except Exception as e:
            logging.error(f"Failed to process new commits: {str(e)}")
            raise
