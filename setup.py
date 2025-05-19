from setuptools import setup, find_packages

setup(
    name="git-commit-to-social",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "tweepy>=4.0.0",
        "gitpython>=3.0.0",
        "apscheduler>=3.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "git-commit-to-social=src.main:main",
        ],
    },
)
