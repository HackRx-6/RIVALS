import subprocess

def auto_commit(repo_path=".", commit_message="Auto-commit", should_commit=True) -> str:
    """
    Conditionally commits and pushes changes in a Git repository.
    
    Args:
        repo_path (str): Path to the Git repository.
        commit_message (str): Commit message.
        should_commit (bool): Only commit if True.
    
    Returns:
        str: Result message.
    """
    if not should_commit:
        return "Auto-commit skipped (parameter condition not met)."

    try:
        # Stage all changes
        subprocess.run(
            ["git", "-C", repo_path, "add", "."],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check if there are any changes to commit
        diff_check = subprocess.run(
            ["git", "-C", repo_path, "diff-index", "--quiet", "HEAD", "--"],
            text=True
        )
        if diff_check.returncode == 0:
            return "No changes detected. Nothing to commit."

        # Commit changes
        subprocess.run(
            ["git", "-C", repo_path, "commit", "-m", commit_message],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Push changes
        subprocess.run(
            ["git", "-C", repo_path, "push"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        return "Changes committed and pushed successfully."

    except subprocess.CalledProcessError as e:
        return f"Git command failed:\n{e.stderr}"


# Main workflow
if __name__ == "__main__":
    # Auto-commit the changes
    result = auto_commit(
        repo_path=".",  # current repository
        commit_message="Auto-update output.txt for ROUND_6",
        should_commit=True  # only commit if this condition is True
    )
    print(result)