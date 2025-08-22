import subprocess
import sys
from pathlib import Path

def run_python_with_input(script_path: str, input_file_path: str) -> str:
    """
    Runs a Python script with a given input file and returns its output.
    
    Args:
        script_path (str): Path to the .py file to run.
        input_file_path (str): Path to the input.txt file.
        
    Returns:
        str: The stdout of the script execution or the error if it fails.
    """
    script_path = Path(script_path)
    input_file_path = Path(input_file_path)

    if not script_path.is_file():
        return f"Error: Script file {script_path} does not exist."
    if not input_file_path.is_file():
        return f"Error: Input file {input_file_path} does not exist."

    try:
        # Open the input file in read mode and pass it to the script's stdin
        with input_file_path.open("r", encoding="utf-8") as f:
            # subprocess.run works on both Linux and Windows
            result = subprocess.run(
                [sys.executable, str(script_path)],  # Use the same Python interpreter
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Return output as string instead of bytes
                check=False  # Don't raise exception on non-zero exit
            )
        
        if result.returncode != 0:
            return f"Error running script:\n{result.stderr}"
        
        return result.stdout

    except Exception as e:
        return f"Exception occurred: {e}"

if __name__ == "__main__":
    script_path = sys.argv[1]
    input_file_path = sys.argv[2]
    print(run_python_with_input(script_path, input_file_path))