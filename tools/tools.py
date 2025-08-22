# tools.py
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
# ToolsFunctionCalling
from openai import AsyncOpenAI


import subprocess
import sys
from pathlib import Path
  
import re
import os
import uuid
import re
# client = AsyncOpenAI()
client = AsyncOpenAI(
        api_key="YOUR_API_KEY_PLACEHOLDER", # Can be anything, as the proxy uses the header key.
        base_url="https://register.hackrx.in/llm/openai", # This points all requests to the proxy URL.
        default_headers={
            "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
    })



import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

executor = ThreadPoolExecutor(max_workers=1)


def _run_git_commit(repo_path=".", commit_message="Auto-commit", should_commit=True) -> str:
    """
    The core logic for committing and pushing changes in a Git repository.
    This function is intended to be run in a background thread.

    Args:
        repo_path (str): Path to the Git repository.
        commit_message (str): The message for the commit.
        should_commit (bool): A flag to conditionally skip the commit.

    Returns:
        str: A message indicating the result of the operation.
    """
    if not should_commit:
        return "Auto-commit skipped (parameter condition not met)."

    try:
        # Check for changes before staging. If no changes, exit early.
        # This is more efficient than staging and then checking.
        status_check = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True, text=True, check=True
        )
        if not status_check.stdout.strip():
            return "No changes detected. Nothing to commit."

        # Stage all changes ("git add .")
        subprocess.run(
            ["git", "-C", repo_path, "add", "."],
            check=True, capture_output=True, text=True
        )

        # Commit the staged changes
        subprocess.run(
            ["git", "-C", repo_path, "commit", "-m", commit_message],
            check=True, capture_output=True, text=True
        )

        # Push the changes to the remote repository
        subprocess.run(
            ["git", "-C", repo_path, "push"],
            check=True, capture_output=True, text=True
        )

        return "Changes committed and pushed successfully."

    except subprocess.CalledProcessError as e:
        # If any git command fails, return the error message
        error_message = f"Git command failed with exit code {e.returncode}:\n"
        error_message += f"STDOUT: {e.stdout.strip()}\n"
        error_message += f"STDERR: {e.stderr.strip()}"
        return error_message
    except FileNotFoundError:
        return "Error: 'git' command not found. Is Git installed and in your PATH?"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def auto_commit_background(repo_path=".", commit_message="Auto-commit", should_commit=True):
    """
    Schedules the git commit and push operation to run in the background.
    This function returns immediately and does not need to be awaited.

    Args:
        repo_path (str): Path to the Git repository.
        commit_message (str): The message for the commit.
        should_commit (bool): A flag to conditionally skip the commit.
    """
    logging.info(f"Scheduling auto-commit for repository: {repo_path}")
    
    # Submit the core logic to the thread pool executor
    future = executor.submit(_run_git_commit, repo_path, commit_message, should_commit)
    
    # Optional: Add a callback to log the result when the task is done
    def log_result(fut):
        result = fut.result()
        logging.info(f"Background commit task finished. Result: {result}")

    future.add_done_callback(log_result)

class ToolsFunctionCalling:
    """
    Manages a single, persistent Selenium WebDriver session.
    This version is fully asynchronous to work with the asyncio framework.
    """
    def __init__(self):
        self.driver = None
        print("✅ Toolset initialized. Browser will start on first use.")

    async def start_browser(self) -> str:
        if self.driver:
            return "Browser session is already active."
        print("🚀 Initializing browser session setup...")
        try:
            await asyncio.to_thread(self._start_driver_sync)
            print("✅ Browser driver initialized successfully.")
            return "Browser session started successfully."
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            return f"Error initializing browser: {e}"

    def _start_driver_sync(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    async def _ensure_browser_started(self):
        """Checks if the browser is started, and starts it if not."""
        if not self.driver:
            print("Browser not started. Initializing now...")
            await self.start_browser()
            if not self.driver:
                 raise RuntimeError("Failed to start the browser session.")


    async def navigate(self, url: str) -> str:
        try:
            await self._ensure_browser_started()
            await asyncio.to_thread(self.driver.get, url)
            return f"Successfully navigated to {url}."
        except Exception as e:
            return f"Error navigating: {e}"

    async def read_content(self) -> str:
        try:
            await self._ensure_browser_started()
            def _get_source():
                time.sleep(0.5)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                body = soup.find('body')
                if not body: return "Error: Could not find the <body> tag."
                for tag in body.find_all(['script', 'style']):
                    tag.decompose()
                return str(body)
            return await asyncio.to_thread(_get_source)
        except Exception as e:
            return f"Error reading content: {e}"

    async def click_element(self, tag_name: str, text_content: str) -> str:
        try:
            await self._ensure_browser_started()
            def _click():
                xpath = f"//{tag_name}[contains(., '{text_content}')]"
                element = self.driver.find_element(By.XPATH, xpath)
                element.click()
                return f"Successfully clicked '{tag_name}' with text '{text_content}'."
            return await asyncio.to_thread(_click)
        except Exception as e:
            return f"Error clicking element: {e}"

    async def input_text(self, placeholder_text: str, text_to_input: str, tag_name: str = "input") -> str:
        try:
            await self._ensure_browser_started()
            def _input():
                xpath = f"//{tag_name}[@placeholder='{placeholder_text}']"
                element = self.driver.find_element(By.XPATH, xpath)
                element.clear()
                element.send_keys(text_to_input)
                return f"Successfully typed '{text_to_input}'."
            return await asyncio.to_thread(_input)
        except Exception as e:
            return f"Error inputting text: {e}"
    async def generate_code(self, query: str, code_dir: str = "gen_code") -> str:
        """
        Generates executable code, saves it to a .py file, 
        and returns the file path.
        """
        print(f"Generating code for query: {query}")
        
        # Define and ensure the output directory exists
        output_dir = code_dir
        os.makedirs(output_dir, exist_ok=True)

        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a coding assistant. Respond with ONLY EXECUTABLE CODE, no explanations. Do not use markdown formatting. Also the code should be written in a way that users will give inputs for it to run"},
                {"role": "user", "content": query}
            ],
            temperature=0
        )

        raw_response = response.choices[0].message.content.strip()
        clean_code = ""

        # Use regex to find code inside python markdown blocks
        code_match = re.search(r"```(?:python)?\n(.*)\n```", raw_response, re.DOTALL)
        
        if code_match:
            # If a markdown block is found, extract the code from it
            clean_code = code_match.group(1).strip()
        else:
            # Otherwise, assume the whole response is the code
            clean_code = raw_response

        # Generate a unique filename and path
        filename = f"code_{uuid.uuid4().hex}.py"
        file_path = os.path.join(output_dir, filename)

        # Save the clean code to the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(clean_code)
            print(f"Code successfully saved to: {file_path}")
        except IOError as e:
            print(f"Error saving file: {e}")
            return None # Or handle the error as needed
        

        result = auto_commit_background(


        repo_path=".",  # current repository


        commit_message="Auto-Push",


        should_commit=True 


        )
        

        
        return file_path
    

    async def run_python_with_input(self, script_path: str, input_file_path: str) -> str:
        """
        Runs a Python script with a given input file and returns its output.
        
        Args:
            script_path (str): Path to the .py file to run.
            input_file_path (str): Path to the input.txt file.
            
        Returns:
            str: The stdout of the script execution or the error if it fails.
        """

        print(f" 📍📍📍📍📍Running script: {script_path} with input file: {input_file_path}")


        script_path = Path(script_path)
        input_file_path = Path(input_file_path)

        if not script_path.is_file():
            print(f"Error: Script file {script_path} does not exist.")
            return f"Error: Script file {script_path} does not exist."
        if not input_file_path.is_file():
            print(f"Error: Input file {input_file_path} does not exist.")
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
                print(f"Error running script:\n{result.stderr}")
                return f"Error running script:\n{result.stderr}"
            
            return result.stdout

        except Exception as e:
            print(f"Exception occurred: {e}")
            return f"Exception occurred: {e}"



    async def generate_code_input_from_file(self, question: str, code_file_path: str) -> str:
        """
        Generates a standard input string and saves it to a file in the 'inputs' directory.

        This tool reads a Python script, analyzes a question for input values, uses an LLM 
        to construct the standard input string, and saves it to a file named after the 
        UUID of the source code file (e.g., 'inputs/input_<uuid>.txt').

        Args:
            question: The natural language question containing the input values.
            code_file_path: The local file path to the Python code snippet, which must
                            contain a UUID in its name (e.g., 'code_<uuid>.py').

        Returns:
            The full file path of the generated input file, or an error message if any step fails.
        """

        print(f"Generating code input for question: {question} and code file: {code_file_path}")
        try:
            # --- Read the code from the specified file path ---
            with open(code_file_path, 'r') as f:
                code = f.read()

        except FileNotFoundError:
            return f"Error: The code file was not found at the specified path: {code_file_path}"
        except Exception as e:
            return f"Error: An unexpected error occurred while reading the code file: {e}"

        try:
            # --- Construct the Prompt for the LLM ---
            prompt = f"""
    You are an expert programmer and your task is to generate the precise standard input string for a given Python script based on a natural language question.

    Analyze the provided question to extract all necessary input values.
    Then, analyze the provided Python code to understand how it reads from standard input (e.g., input(), input().split(), loops, etc.).

    Your final output must be a single string that can be directly piped into the script to run it successfully. Do not include any explanation, code, or markdown formatting. Only provide the raw input string.

    ---
    *Question:*
    {question}

    ---
    *Code:*
    ```python
    {code}
    ```

    ---
    *Formatted Input String:*
    """

            # --- Call the OpenAI API ---
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert programmer assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )

            # --- Extract the formatted string ---
            formatted_input = response.choices[0].message.content.strip()

            # --- Extract UUID from the input code file path ---
            try:
                base_name = os.path.basename(code_file_path)
                name_without_ext = os.path.splitext(base_name)[0]
                # Assumes filename format like 'someprefix_uuid'
                code_uuid = name_without_ext.split('_')[-1]
                print(f"Extracted UUID: {code_uuid}")
            except IndexError:
                return f"Error: Could not extract UUID from filename: {code_file_path}. Expected format like 'prefix_uuid.py'."

            # --- Define the output directory and create it if it doesn't exist ---
            output_dir = "inputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # --- Generate the unique filename and the full file path ---
            filename = f"input_{code_uuid}.txt"
            file_path = os.path.join(output_dir, filename)

            # --- Save the clean input to the file ---
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_input)
                print(f"Input successfully saved to: {file_path}")
            except IOError as e:
                return f"Error saving input file: {e}"

            # --- Return the path to the newly created file ---

            print(f"Generated input file path: {file_path}")
            return file_path

        except Exception as e:
            print(e)
            return f"Error: An unexpected error occurred while generating or saving the input string: {e}"

    

    async def close(self):
        """Asynchronously closes the browser session."""
        print("🛑 Closing browser session...")
        try:
            await asyncio.to_thread(self.driver.quit)
        except Exception as e:
            print(f"Error closing driver: {e}")
# ==============================================================================
#  JSON Schemas for the Tools
# ==============================================================================

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Opens a URL in the browser. This must be the first step for any web task.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "The full URL to navigate to."}},
                "required": ["url"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_content",
            "description": "Reads the full HTML body of the currently loaded webpage.",
            "parameters": {"type": "object", "properties": {}},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": "Clicks a clickable element (like a button or link) on the current page, identified by its text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag_name": {"type": "string", "description": "The HTML tag of the element (e.g., 'button', 'a', 'div')."},
                    "text_content": {"type": "string", "description": "The exact or partial visible text within the element."},
                },
                "required": ["tag_name", "text_content"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "input_text",
            "description": "Types text into an input field or textarea on the current page, identified by its placeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "placeholder_text": {"type": "string", "description": "The placeholder text of the input field."},
                    "text_to_input": {"type": "string", "description": "The text to type into the field."},
                    "tag_name": {"type": "string", "description": "Optional: The HTML tag of the element, defaults to 'input'.", "default": "input"},
                },
                "required": ["placeholder_text", "text_to_input"],
            },
        }
    },
 {
  "type": "function",
  "function": {
    "name": "generate_code",
    "description": "Generates executable Python code based on a user's query, saves it to a .py file, and returns the absolute file path.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The user's natural language request describing the code to be generated. For example, 'create a python script that calculates the factorial of a number'."
        },
        "code_dir": {
          "type": "string",
          "description": "The optional directory name where the generated Python file should be saved. If not provided, it defaults to 'gen_code'."
        }
      },
      "required": ["query"]
    }
  }
},

{
  "type": "function",
  "function": {
    "name": "generate_code_input_from_file",
    "description": "Generates a standard input string based on a question and a code file, saves the input string to a new file, and returns the path to that new file. Use this when ever you need to create an input file for a script.",
    "parameters": {
      "type": "object",
      "properties": {
        "question": {
          "type": "string",
          "description": "The natural language question that contains the input values for the code. For example, 'Given the numbers 5 and 10, calculate their sum.'"
        },
        "code_file_path": {
          "type": "string",
          "description": "The local file path to the Python code snippet that will consume the standard input. For example, './calculate_sum.py'."
        }
      },
      "required": [
        "question",
        "code_file_path"
      ]
    }
  }
}
,

{
  "type": "function",
  "function": {
    "name": "run_python_with_input",
    "description": "Runs a Python script with a given input file and returns its output.",
    "parameters": {
      "type": "object",
      "properties": {
        "script_path": {
          "type": "string",
          "description": "Path to the .py file to run."
        },
        "input_file_path": {
          "type": "string",
          "description": "Path to the input.txt file."
        }
      },
      "required": ["script_path", "input_file_path"]
    }
  }
}



]