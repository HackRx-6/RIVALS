import subprocess

def git_add(repo_path=".", files=".") -> str:
    """
    Stages files for commit.

    Args:
        repo_path (str): Path to the Git repository.
        files (str or list): Files or directories to stage. Default "." stages everything.

    Returns:
        str: Result message.
    """
    try:
        cmd = ["git", "-C", repo_path, "add"]
        if isinstance(files, list):
            cmd.extend(files)
        else:
            cmd.append(files)

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"Added {files} to staging."
    except subprocess.CalledProcessError as e:
        return f"Error adding files: {e.stderr}"
    
    
if __name__ == "__main__":
    output = git_add()
    print(output)