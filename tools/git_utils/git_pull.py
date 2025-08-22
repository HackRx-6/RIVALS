import subprocess

def git_pull(repo_path=".", remote="origin", branch="main") -> str:
    """
    Pulls changes from a remote repository.

    Args:
        repo_path (str): Path to the Git repository.
        remote (str): Remote name.
        branch (str): Branch to pull.

    Returns:
        str: Result message.
    """
    try:
        subprocess.run(
            ["git", "-C", repo_path, "pull", remote, branch],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return f"Pulled latest changes from {remote}/{branch}"
    except subprocess.CalledProcessError as e:
        return f"Error pulling changes: {e.stderr}"
    
if __name__ == "__main__":
    output = git_pull()
    print(output)