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
                
                if diff_item.a_blob and diff_item.b_blob:
                    diff_content = str(diff_item.diff)
                    if len(diff_content) > 500:
                        diff_content = diff_content[:500] + "...[truncated]"
                    diff_summary += f"Changes:\n{diff_content}\n"
                    
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
