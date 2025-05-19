import git
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.git_service import GitService

def test_enhanced_diff_extraction():
    """Test the enhanced diff extraction functionality."""
    repo_path = os.environ.get("REPO_PATH", "/home/ubuntu/repos/barebone-ai-app")
    
    git_service = GitService(repo_path=repo_path)
    
    commit = next(git_service.repo.iter_commits())
    
    print(f"Testing enhanced diff extraction for commit: {commit.hexsha}")
    print(f"Author: {commit.author.name}")
    print(f"Message: {commit.message}")
    print(f"Date: {datetime.fromtimestamp(commit.committed_date).isoformat()}")
    print("\n" + "="*60 + "\n")
    
    diff_content = git_service.get_commit_diff(commit)
    
    print("Enhanced diff content:")
    print(diff_content)

if __name__ == "__main__":
    test_enhanced_diff_extraction()
