import subprocess

def git_log(repo_path=".", max_entries=5) -> str:
    """
    Returns the Git commit history.

    Args:
        repo_path (str): Path to the Git repository.
        max_entries (int): Number of commits to show.

    Returns:
        str: Commit log.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", f"-n{max_entries}", "--oneline"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error fetching log: {e.stderr}"
    

    
if __name__ == "__main__":
    output = git_log()
    print(output)