# Git Commit to Social

A tool that monitors commits to a Git repository, summarizes them using OpenAI's GPT-mini model, and posts daily summaries to X (Twitter).

## Features

- Monitors commits to a specified Git repository (barebone-ai-app)
- Analyzes commit messages and code changes
- Generates daily summaries at 10:30 PM HKT using OpenAI's GPT-mini model
- Posts summaries to X (Twitter)
- Includes error handling with 3 retries
- Handles X API rate limiting
- Stores commit data in SQLite database
- Comprehensive logging and monitoring

## Installation

1. Clone the repository:
```bash
git clone https://github.com/briiantam/git-commit-to-social.git
cd git-commit-to-social
```

2. Install the package:
```bash
pip install -e .
```

3. Create a `.env` file based on the `.env.example` template:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your API keys and configuration.

## Configuration

The following environment variables can be configured in the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key
- `X_API_KEY`: Your X (Twitter) API key
- `X_API_SECRET`: Your X (Twitter) API secret
- `X_ACCESS_TOKEN`: Your X (Twitter) access token
- `X_ACCESS_TOKEN_SECRET`: Your X (Twitter) access token secret
- `REPO_PATH`: Path to the Git repository to monitor (default: `/home/ubuntu/repos/barebone-ai-app`)
- `DAILY_SUMMARY_TIME_HKT`: Time to generate and post daily summaries in HKT (default: `22:30`)

## Usage

Run the application:

```bash
git-commit-to-social
```

The application will:
1. Monitor the specified Git repository for new commits
2. Generate a summary of all commits made each day at 10:30 PM HKT
3. Post the summary to X (Twitter)

## Testing

To test the application without posting to X, you can modify the `twitter_service.py` file to print the tweet instead of posting it.

## License

MIT
