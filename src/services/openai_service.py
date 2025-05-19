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
        """Summarize a list of commits using OpenAI GPT-4o-mini model."""
        if not commits:
            return "no commits were made today. the void stares back. silence."
        
        commits_info = []
        for commit in commits:
            commit_info = (
                f"Commit: {commit['id'][:7]}\n"
                f"Author: {commit['author']}\n"
                f"Message: {commit['message']}\n"
                f"Files changed: {', '.join(commit['files_changed'][:5])}"
                f"{' and more' if len(commit['files_changed']) > 5 else ''}\n"
                f"Stats: +{commit['insertions']}, -{commit['deletions']}\n"
                f"Diff: {commit.get('diff_content', 'No diff available')[:1000]}\n"
            )
            commits_info.append(commit_info)
        
        commits_text = "\n".join(commits_info)
        
        prompt = (
            "below are the commits made to a repository today. "
            "analyze these changes and provide a detailed summary of what actually changed and its impact. "
            "focus on the semantic meaning of the code changes - what functionality was added, modified, or removed? "
            "analyze the actual code content in the diff, not just file names or metadata. "
            "explain how these changes affect the application's behavior or architecture. "
            "if there are multiple commits, identify patterns or themes in the changes. "
            "write as if you are steve jobs on lsd and crack - eccentric, intense, lowercase only, no emojis, "
            "totally unhinged but deeply insightful about technology. "
            "use 1-2 paragraphs, suitable for a brief social media post.\n\n"
            f"{commits_text}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini as specified
                messages=[
                    {"role": "system", "content": "you are steve jobs on lsd and crack. you write in lowercase only, no emojis, intense and eccentric but insightful about technology. when analyzing code changes, focus on understanding what the code actually does and how it impacts the overall application."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500  # Increased for more detailed content
            )
            
            summary = response.choices[0].message.content.strip().lower()  # Ensure lowercase
            logging.info("Successfully generated commit summary")
            return summary
        except Exception as e:
            logging.error(f"Failed to summarize commits: {str(e)}")
            raise
