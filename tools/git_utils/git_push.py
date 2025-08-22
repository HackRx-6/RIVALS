import subprocess

def git_push(repo_path=".", remote="origin", branch="main") -> str:
    """
    Pushes commits to a remote repository.

    Args:
        repo_path (str): Path to the Git repository.
        remote (str): Remote name, e.g., "origin".
        branch (str): Branch to push.

    Returns:
        str: Result message.
    """
    try:
        subprocess.run(
            ["git", "-C", repo_path, "push", remote, branch],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return f"Pushed changes to {remote}/{branch}"
    except subprocess.CalledProcessError as e:
        return f"Error pushing changes: {e.stderr}"


if __name__ == "__main__":
    output = git_push()
    print(output)