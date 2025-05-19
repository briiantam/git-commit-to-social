"""OpenAI service for summarizing commits."""
import logging
from openai import OpenAI
from ..config.config import OPENAI_API_KEY, MAX_RETRIES, RETRY_DELAY
from ..utils.retry import retry

class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self, api_key=OPENAI_API_KEY):
        """Initialize the OpenAIService."""
        self.client = OpenAI(api_key=api_key)
        logging.info("OpenAI service initialized")
    
    @retry(max_retries=MAX_RETRIES, delay=RETRY_DELAY)
    def summarize_commits(self, commits):
        """Summarize a list of commits using OpenAI GPT-mini model."""
        if not commits:
            return "No commits were made today."
        
        commits_info = []
        for commit in commits:
            commit_info = (
                f"Commit: {commit['id'][:7]}\n"
                f"Author: {commit['author']}\n"
                f"Message: {commit['message']}\n"
                f"Files changed: {', '.join(commit['files_changed'][:5])}"
                f"{' and more' if len(commit['files_changed']) > 5 else ''}\n"
                f"Stats: +{commit['insertions']}, -{commit['deletions']}\n"
            )
            commits_info.append(commit_info)
        
        commits_text = "\n".join(commits_info)
        
        prompt = (
            "Below are the commits made to a repository today. "
            "Please provide a concise, engaging summary of these commits, "
            "focusing on the key changes, new features, or improvements. "
            "Use 1-2 paragraphs, suitable for posting on X (Twitter).\n\n"
            f"{commits_text}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-mini",  # Using GPT-mini as specified
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes code changes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=280  # Twitter's character limit
            )
            
            summary = response.choices[0].message.content.strip()
            logging.info("Successfully generated commit summary")
            return summary
        except Exception as e:
            logging.error(f"Failed to summarize commits: {str(e)}")
            raise
