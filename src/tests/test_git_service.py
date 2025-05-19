"""Tests for the git service."""
import unittest
from unittest.mock import patch, MagicMock
from src.services.git_service import GitService

class TestGitService(unittest.TestCase):
    """Test cases for the GitService class."""
    
    @patch('git.Repo')
    def test_initialize_repo(self, mock_repo):
        """Test initializing the git repository."""
        mock_repo.return_value = MagicMock()
        
        service = GitService(repo_path="/test/path")
        
        mock_repo.assert_called_once_with("/test/path")
        self.assertIsNotNone(service.repo)
    
    @patch('git.Repo')
    def test_update_repo(self, mock_repo):
        """Test updating the git repository."""
        mock_instance = MagicMock()
        mock_repo.return_value = mock_instance
        mock_origin = MagicMock()
        mock_instance.remotes.origin = mock_origin
        
        service = GitService(repo_path="/test/path")
        service.update_repo()
        
        mock_origin.pull.assert_called_once()

if __name__ == '__main__':
    unittest.main()
