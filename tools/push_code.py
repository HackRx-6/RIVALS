from pathlib import Path
import os
from github import Github

# Read GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "HackRx-6/RIVALS"  # Replace with your repo

PROJECT_ROOT = Path(__file__).parent

def push_current_code():
    """
    Push all files in the project to GitHub whenever called.
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable not set!")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    for file_path in PROJECT_ROOT.rglob("*"):
        if file_path.is_file() and ".git" not in str(file_path):
            relative_path = str(file_path.relative_to(PROJECT_ROOT))

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                existing_file = repo.get_contents(relative_path)
                commit_message = f"Update {relative_path} with latest changes"
                repo.update_file(
                    existing_file.path,
                    commit_message,
                    content,
                    existing_file.sha
                )
            except:
                commit_message = f"Add {relative_path} with latest changes"
                repo.create_file(relative_path, commit_message, content)
