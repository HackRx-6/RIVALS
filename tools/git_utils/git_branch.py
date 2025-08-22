import subprocess

def git_branch(repo_path=".") -> str:
    """
    Lists all branches in the repo.

    Args:
        repo_path (str): Path to the Git repository.

    Returns:
        str: Branch list.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "branch", "-a"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error listing branches: {e.stderr}"
