import subprocess

def git_commit(repo_path=".", message="Commit") -> str:
    """
    Commits staged changes.

    Args:
        repo_path (str): Path to the Git repository.
        message (str): Commit message.

    Returns:
        str: Result message.
    """
    try:
        subprocess.run(
            ["git", "-C", repo_path, "commit", "-m", message],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return f"Committed changes with message: '{message}'"
    except subprocess.CalledProcessError as e:
        return f"Error committing changes: {e.stderr}"



if __name__ == "__main__":
    output = git_commit("Auto-committ for testing")
    print(output)