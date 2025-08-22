import subprocess
from pathlib import Path

def get_git_root() -> Path:
    """Returns the path to the root of the git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        raise RuntimeError("Error: Not inside a git repository.")

def git_checkout(branch_name: str) -> str:
    """Checks out a branch using the project root as cwd."""
    try:
        repo_root = get_git_root()
        result = subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Error checking out branch:\n{result.stderr.strip()}"
        return result.stdout.strip() or f"Switched to branch '{branch_name}'"
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    import sys
    branch = sys.argv[1] if len(sys.argv) > 1 else "main"
    output = git_checkout(branch)
    print(output)
