import subprocess

def git_status(repo_path=".") -> str:
    """
    Returns the Git status for the repo.

    Args:
        repo_path (str): Path to the Git repository.

    Returns:
        str: Status output.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "status"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting status: {e.stderr}"



if __name__ == "__main__":
    output = git_status()
    print(output)