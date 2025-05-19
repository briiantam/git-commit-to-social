"""Git service for monitoring commits."""
import os
import logging
from datetime import datetime
import git
from ..config.config import REPO_PATH
from ..models.database import store_commit

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
    
    def process_new_commits(self):
        """Process new commits and store them in the database."""
        try:
            self.update_repo()
            commits = self.get_todays_commits()
            
            for commit in commits:
                files_changed = []
                stats = commit.stats.files
                
                for file_path, file_stats in stats.items():
                    files_changed.append(file_path)
                
                store_commit(
                    commit_id=commit.hexsha,
                    author=commit.author.name,
                    message=commit.message,
                    timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                    files_changed=files_changed,
                    insertions=commit.stats.total["insertions"],
                    deletions=commit.stats.total["deletions"]
                )
            
            return len(commits)
        except Exception as e:
            logging.error(f"Failed to process new commits: {str(e)}")
            raise
