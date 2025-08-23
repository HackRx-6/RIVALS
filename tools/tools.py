import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import List, Optional
# ToolsFunctionCalling
from openai import AsyncOpenAI
import time

import json

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
        print(error_message)
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

# -----------------------------------------------------------------------------
# Custom Expected Condition for Selenium (Helper for the new tool)
# -----------------------------------------------------------------------------
class attribute_changed_for_any_element:
    """
    An expectation for checking if a specified attribute has changed for any
    of the elements identified by a list of CSS selectors.
    """
    def __init__(self, selectors: List[str], attribute: str, initial_states: dict):
        self.selectors = selectors
        self.attribute = attribute
        self.initial_states = initial_states

    def __call__(self, driver) -> Optional[str]:
        for selector in self.selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                current_value = element.get_attribute(self.attribute)
                initial_value = self.initial_states.get(selector)
                if current_value != initial_value:
                    return selector
            except NoSuchElementException:
                print(f"Warning: Element with selector '{selector}' not found.")
                continue
        return False

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
        # chrome_options.add_argument("--headless")
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
        

    async def get_interactive_elements(self) -> str:
        """
        Extracts and lists all interactive elements like links, buttons, and input
        fields from the current page, showing their text and URLs/placeholders.
        """
        try:
            await self._ensure_browser_started()

            def _get_elements_sync():
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                elements = []
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True)
                    if text:
                        elements.append({
                            "type": "link",
                            "text": text,
                            "href": link['href']
                        })
                
                # Find all buttons
                for button in soup.find_all('button'):
                    text = button.get_text(strip=True)
                    if text:
                        elements.append({
                            "type": "button",
                            "text": text
                        })

                # Find all text inputs
                for input_tag in soup.find_all('input'):
                    if input_tag.get('type') in ['text', 'email', 'password', 'search', 'tel', 'url', None]:
                        elements.append({
                            "type": "input",
                            "placeholder": input_tag.get('placeholder', 'N/A'),
                            "name": input_tag.get('name', 'N/A')
                        })

                if not elements:
                    return "No interactive elements (links, buttons, inputs) found on the page."
                
                # Return as a formatted JSON string for clarity
                return json.dumps(elements, indent=2)

            return await asyncio.to_thread(_get_elements_sync)
        except Exception as e:
            return f"Error extracting interactive elements: {e}"

    async def read_content(self) -> str:
        """
        Extracts relevant visible text, URLs, and button-related info from the page.
        Returns a JSON string with 'text', 'urls', and 'buttons'.
        """
        try:
            await self._ensure_browser_started()

            def _extract_content():
                time.sleep(0.2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                body = soup.find('body')
                if not body:
                    return {"error": "Could not find <body> tag."}

                # Remove scripts, styles, and hidden elements
                for tag in body.find_all(['script', 'style', 'noscript']):
                    tag.decompose()
                for hidden in body.select('[style*="display:none"], [hidden]'):
                    hidden.decompose()

                # Get visible text
                text = body.get_text(separator="\n", strip=True)

                # Collect URLs (anchors + images + iframes)
                urls = []
                for tag in body.find_all(["a", "img", "iframe"]):
                    href = tag.get("href") or tag.get("src")
                    if href:
                        urls.append(href)

                # Collect button-related elements
                buttons = []
                for btn in body.find_all(["button", "a", "input"]):
                    btn_type = btn.name
                    btn_text = btn.get_text(strip=True) if btn.name != "input" else btn.get("value", "")
                    btn_action = btn.get("onclick") or btn.get("href") or btn.get("formaction") or btn.get("src")
                    if btn_type == "input" and btn.get("type") not in ["button", "submit"]:
                        continue  # ignore non-button inputs
                    buttons.append({
                        "tag": btn_type,
                        "text": btn_text,
                        "action": btn_action
                    })

                return {
                    "text": text[:5000],   # limit to avoid giant payloads
                    "urls": list(set(urls)),
                    "buttons": buttons
                }

            result = await asyncio.to_thread(_extract_content)
            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Error reading content: {e}"})

   
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException

    async def click_element(
    self, 
    tag_name: str = None, 
    text_content: str = None, 
    element_id: str = None, 
    class_name: str = None, 
    css_selector: str = None
    ) -> str:
        try:
            await self._ensure_browser_started()

            def _click():
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
                
                wait = WebDriverWait(self.driver, 10)
                element = None

                # Try CSS selector first
                if css_selector:
                    try:
                        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
                    except:
                        pass

                # Try ID
                if not element and element_id:
                    try:
                        element = wait.until(EC.element_to_be_clickable((By.ID, element_id)))
                    except:
                        pass

                # Try class name
                if not element and class_name:
                    try:
                        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
                    except:
                        pass

                # Try text content with tag name - enhanced with multiple XPath approaches
                if not element and tag_name and text_content:
                    xpaths_to_try = [
                        f"//{tag_name}[contains(text(), '{text_content}')]",
                        f"//{tag_name}[normalize-space(text())='{text_content}']",
                        f"//{tag_name}[contains(@title, '{text_content}')]",
                        f"//{tag_name}[contains(@aria-label, '{text_content}')]"
                    ]
                    
                    for xpath in xpaths_to_try:
                        try:
                            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            break
                        except:
                            continue

                if not element:
                    return "❌ Element not found with the provided selectors."

                # Multiple click strategies
                click_methods = [
                    # Standard click
                    lambda: element.click(),
                    # JavaScript click (bypasses overlays)
                    lambda: self.driver.execute_script("arguments[0].click();", element),
                    # ActionChains click
                    lambda: ActionChains(self.driver).move_to_element(element).click().perform(),
                    # Scroll into view then click
                    lambda: (
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element),
                        __import__('time').sleep(0.5),
                        element.click()
                    )[-1]
                ]

                for i, click_method in enumerate(click_methods):
                    try:
                        click_method()
                        method_names = ["standard click", "JavaScript click", "ActionChains", "scroll + click"]
                        return f"✅ Successfully clicked element ({method_names[i]})."
                    except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                        if i == len(click_methods) - 1:  # Last method
                            return f"❌ All click methods failed. Last error: {str(e)}"
                        continue
                    except Exception as e:
                        if i == len(click_methods) - 1:  # Last method
                            return f"❌ All click methods failed. Last error: {str(e)}"
                        continue

            return await asyncio.to_thread(_click)

        except Exception as e:
            return f"❌ Error while trying to click element: {e}"


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

    # --- NEW TOOL ---
    async def observe_attribute_change(self, selectors: List[str], attribute: str, timeout: int) -> Optional[str]:
        """
        Asynchronously monitors elements for an attribute change.
        """
        await self._ensure_browser_started()
        return await asyncio.to_thread(
            self._observe_attribute_change_sync,
            selectors,
            attribute,
            timeout
        )

    # def _observe_attribute_change_sync(self, selectors: List[str], attribute: str, timeout: int) -> Optional[str]:
    #     """
    #     The synchronous core logic for observing attribute changes.
    #     """
    #     print(f"--- Observing {len(selectors)} elements for changes to '{attribute}' attribute (timeout: {timeout}s) ---")
        
    #     initial_states = {}
    #     for selector in selectors:
    #         try:
    #             element = self.driver.find_element(By.CSS_SELECTOR, selector)
    #             initial_states[selector] = element.get_attribute(attribute)
    #         except NoSuchElementException:
    #             print(f"Error: Could not find element with selector '{selector}' during initial state capture.")
    #             initial_states[selector] = None

    #     print("Initial states captured:", initial_states)

    #     try:
    #         wait = WebDriverWait(self.driver, timeout)
    #         changed_element_selector = wait.until(
    #             attribute_changed_for_any_element(selectors, attribute, initial_states)
    #         )
    #         print(f"✅ Change detected! Element '{changed_element_selector}' changed its '{attribute}' attribute.")
    #         return changed_element_selector
    #     except TimeoutException:
    #         print(f"❌ Timeout of {timeout}s reached. No attribute changes were detected.")
    #         return None
        
    # # --- END NEW TOOL ---

    async def generate_code(self, query: str, code_dir: str = "gen_code") -> str:
        """
        Generates executable code, saves it to a .py file, 
        and returns the file path.
        """
        print(f"Generating code for query: {query}")
        
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
            clean_code = code_match.group(1).strip()
        else:
            clean_code = raw_response

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
            repo_path=".",
            commit_message="Auto-Push",
            should_commit=True 
        )
        
        return file_path
    
    async def run_python_with_input(self, script_path: str, input_file_path: str) -> str:
        """
        Runs a Python script with a given input file and returns its output.
        """
        print(f" 📍📍📍📍📍Running script: {script_path} with input file: {input_file_path}")

        script_path = Path(script_path)
        input_file_path = Path(input_file_path)

        if not script_path.is_file():
            return f"Error: Script file {script_path} does not exist."
        if not input_file_path.is_file():
            return f"Error: Input file {input_file_path} does not exist."

        try:
            with input_file_path.open("r", encoding="utf-8") as f:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            
            if result.returncode != 0:
                return f"Error running script:\n{result.stderr}"
            
            return result.stdout

        except Exception as e:
            return f"Exception occurred: {e}"

    async def generate_code_input_from_file(self, question: str, code_file_path: str) -> str:
        """
        Generates a standard input string and saves it to a file in the 'inputs' directory.
        """
        print(f"Generating code input for question: {question} and code file: {code_file_path}")
        try:
            with open(code_file_path, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            return f"Error: The code file was not found at the specified path: {code_file_path}"
        except Exception as e:
            return f"Error: An unexpected error occurred while reading the code file: {e}"

        try:
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
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert programmer assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )
            formatted_input = response.choices[0].message.content.strip()

            try:
                base_name = os.path.basename(code_file_path)
                name_without_ext = os.path.splitext(base_name)[0]
                code_uuid = name_without_ext.split('_')[-1]
                print(f"Extracted UUID: {code_uuid}")
            except IndexError:
                return f"Error: Could not extract UUID from filename: {code_file_path}. Expected format like 'prefix_uuid.py'."

            output_dir = "inputs"
            os.makedirs(output_dir, exist_ok=True)

            filename = f"input_{code_uuid}.txt"
            file_path = os.path.join(output_dir, filename)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_input)
                print(f"Input successfully saved to: {file_path}")
            except IOError as e:
                return f"Error saving input file: {e}"

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




    async def query_expander(self, query: str) -> str:
        """
        Rewrites a natural language query to be more concise and informative
        by removing noise and converting it to lowercase, while preserving
        case-sensitive information like URLs or addresses.

        Args:
            query (str): The original user prompt.

        Returns:
            str: The refined and expanded query.
        """
        print(f"Expanding query: {query}")
        try:
            # Construct the prompt for the LLM to refine the query.
            # Use specific instructions to guide the LLM's output.
            prompt = f"""
            Refine the following user query to be more direct, informative, and concise.
            Remove all conversational noise, filler words, and unnecessary pleasantries.
            Convert the entire query to lowercase, but preserve the original casing for
            any URLs, file paths, specific names, or addresses.

            Original Query:
            {query}

            Refined Query:
            """
            
            # Call the OpenAI API to get the refined query
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that refines user queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )

            refined_query = response.choices[0].message.content.strip()
            print(f"Refined query: {refined_query}")
            return refined_query

        except Exception as e:
            print(f"Error in query_expander: {e}")
            return query # Return the original query on failure
    
    async def interpret_changes(self, changes_log: List[dict]) -> str:
        import json
        """
        Interprets a list of HTML mutation logs and returns a concise,
        human-readable summary of the changes.

        Args:
            changes_log (List[dict]): A list of dictionaries, where each
                                      dictionary represents a mutation log entry.

        Returns:
            A string summarizing the key changes, such as color changes or
            button state changes, in a format that helps the agent
            understand the pattern.
        """
        prompt = f"""
        You are an expert at interpreting technical change logs. Your task is to analyze the following list of HTML mutation logs and summarize the key events in a concise, step-by-step manner. Focus on what a user would care about, Disregard minor or repetitive changes.

        Example: A button being disabled is an important event. A div's class changing from 'red-active' to 'red-inactive' is a key color change.
        
        Here is the mutation log:
        {json.dumps(changes_log, indent=2)}

        Summary of key events:
        """
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a concise data interpreter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    
    
    import asyncio
    import time
    import json
    from typing import List

    async def monitor_html_changes(self, timeout: int = 5, start_immediately: bool = False) -> str:
        """
        Monitors the webpage for live DOM changes with detailed element tracking
        and returns a comprehensive analysis of patterns detected.

        Args:
            timeout (int): The maximum number of seconds to wait for changes.
            start_immediately (bool): If True, starts monitoring immediately without initial snapshot delay.

        Returns:
            A detailed string analysis of DOM changes and the next required action.
        """
        await self._ensure_browser_started()

        print(f"🔍 Starting comprehensive DOM monitoring for {timeout} seconds...")
        start_time = time.time()
        change_events: List[dict] = []
        
        # Enhanced element tracking with detailed attributes
        def capture_detailed_snapshot():
            return self.driver.execute_script("""
                function getElementDetails(el, path = '') {
                    const details = {
                        tagName: el.tagName,
                        id: el.id || null,
                        className: el.className || null,
                        textContent: el.textContent?.trim().substring(0, 100) || null,
                        style: el.style.cssText || null,
                        attributes: {},
                        path: path,
                        timestamp: Date.now()
                    };
                    
                    // Capture all attributes
                    for (let attr of el.attributes) {
                        details.attributes[attr.name] = attr.value;
                    }
                    
                    return details;
                }
                
                function generatePath(el) {
                    let path = '';
                    while (el && el.tagName) {
                        let selector = el.tagName.toLowerCase();
                        if (el.id) selector += '#' + el.id;
                        else if (el.className) selector += '.' + el.className.split(' ')[0];
                        path = selector + (path ? ' > ' + path : '');
                        el = el.parentElement;
                    }
                    return path;
                }
                
                const snapshot = {};
                const elements = document.querySelectorAll('*');
                elements.forEach((el, index) => {
                    const path = generatePath(el);
                    snapshot[path + `[${index}]`] = getElementDetails(el, path);
                });
                
                return snapshot;
            """)

        previous_snapshot = await asyncio.to_thread(capture_detailed_snapshot)
        change_sequence = []
        
        # If start_immediately is True, reduce the initial delay
        initial_delay = 0.05 if start_immediately else 0.1
        await asyncio.sleep(initial_delay)
        
        while time.time() - start_time < timeout:
            await asyncio.sleep(0.05)  # Very frequent polling for immediate pattern capture
            try:
                current_snapshot = await asyncio.to_thread(capture_detailed_snapshot)
                
                # Detect changes with timestamps
                for element_key, current_details in current_snapshot.items():
                    previous_details = previous_snapshot.get(element_key)
                    if previous_details:
                        changes = {}
                        
                        # Check all trackable properties
                        for prop in ['className', 'style', 'textContent', 'id']:
                            if current_details.get(prop) != previous_details.get(prop):
                                changes[prop] = {
                                    'from': previous_details.get(prop),
                                    'to': current_details.get(prop)
                                }
                        
                        # Check attributes
                        for attr, value in current_details.get('attributes', {}).items():
                            old_value = previous_details.get('attributes', {}).get(attr)
                            if value != old_value:
                                changes[f'attr_{attr}'] = {'from': old_value, 'to': value}
                        
                        if changes:
                            change_event = {
                                'timestamp': current_details['timestamp'],
                                'element': element_key,
                                'path': current_details['path'],
                                'changes': changes,
                                'element_details': {
                                    'tagName': current_details['tagName'],
                                    'id': current_details.get('id'),
                                    'className': current_details.get('className')
                                }
                            }
                            change_events.append(change_event)
                            change_sequence.append(change_event)
                            print(f"✅ Change detected in {element_key}: {list(changes.keys())}")
                
                previous_snapshot = current_snapshot
                
            except Exception as e:
                print(f"Error during snapshot comparison: {e}")

        print(f"📊 Monitoring complete. Captured {len(change_events)} change events.")
        
        if not change_events:
            return "No DOM changes detected during monitoring period. Pattern recognition not possible."
        import json
        # Enhanced pattern analysis prompt
        changes_context = json.dumps({
            'total_changes': len(change_events),
            'monitoring_duration': timeout,
            'change_sequence': change_sequence[-50:],  # Last 50 changes to avoid token limits
            'unique_elements_changed': len(set(event['element'] for event in change_events))
        }, indent=2)

        # Improved prompt for better pattern recognition
        pattern_analysis_prompt = f"""
        You are an expert DOM pattern analyzer. Your task is to analyze a sequence of DOM changes and identify actionable patterns, particularly for sequential interactions like flashing cards, buttons, or grid elements.

        ANALYSIS REQUIREMENTS:
        1. Identify if there's a SEQUENTIAL PATTERN
        2. Determine the INTERACTION TYPE 
        3. Specify the EXACT ACTION PLAN based on the pattern

        PATTERN TYPES TO LOOK FOR:
        - Class changes showing activation/deactivation patterns
        - Style changes indicating visual cues for user interaction

        RESPONSE FORMAT:
        Provide a clear, actionable response with:
        1. Pattern Description: What pattern was detected
        2. Element Sequence: The exact order elements changed (use element IDs, classes, or paths)
        3. Action Plan: Specific steps to replicate the sequence
        DOM CHANGES DATA:
        {changes_context}

        ANALYSIS:
        """

        try:
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert pattern recognition system specialized in DOM interaction sequences. Focus on identifying clickable sequences from visual changes."},
                    {"role": "user", "content": pattern_analysis_prompt}
                ],
                temperature=0.0
            )

            analysis = response.choices[0].message.content.strip()
            
            # Store the analysis for potential follow-up actions
            print(f"🧠 Pattern Analysis Complete:\n{analysis}")
            return analysis

        except Exception as e:
            print(f"Error in pattern analysis: {e}")
    async def click_and_monitor(self, tag_name: str, text_content: str, monitor_timeout: int = 5) -> str:
        """
        Clicks an element and immediately starts monitoring for DOM changes.
        Perfect for "start pattern" buttons that trigger immediate sequences.

        Args:
            tag_name (str): The HTML tag of the element to click.
            text_content (str): The text content of the element to click.
            monitor_timeout (int): How long to monitor after clicking.

        Returns:
            Combined result of the click action and pattern analysis.
        """
        try:
            await self._ensure_browser_started()
            
            # Prepare monitoring setup BEFORE clicking
            def capture_detailed_snapshot():
                return self.driver.execute_script("""
                    function getElementDetails(el, path = '') {
                        const details = {
                            tagName: el.tagName,
                            id: el.id || null,
                            className: el.className || null,
                            textContent: el.textContent?.trim().substring(0, 100) || null,
                            style: el.style.cssText || null,
                            attributes: {},
                            path: path,
                            timestamp: Date.now()
                        };
                        
                        // Capture all attributes
                        for (let attr of el.attributes) {
                            details.attributes[attr.name] = attr.value;
                        }
                        
                        return details;
                    }
                    
                    function generatePath(el) {
                        let path = '';
                        while (el && el.tagName) {
                            let selector = el.tagName.toLowerCase();
                            if (el.id) selector += '#' + el.id;
                            else if (el.className) selector += '.' + el.className.split(' ')[0];
                            path = selector + (path ? ' > ' + path : '');
                            el = el.parentElement;
                        }
                        return path;
                    }
                    
                    const snapshot = {};
                    const elements = document.querySelectorAll('*');
                    elements.forEach((el, index) => {
                        const path = generatePath(el);
                        snapshot[path + `[${index}]`] = getElementDetails(el, path);
                    });
                    
                    return snapshot;
                """)

            print(f"🎯 Preparing to click '{tag_name}' with text '{text_content}' and monitor immediately...")
            
            # Take initial snapshot
            previous_snapshot = await asyncio.to_thread(capture_detailed_snapshot)
            change_events: List[dict] = []
            change_sequence = []
            
            # Click the element
            def _click():
                xpath = f"//{tag_name}[contains(., '{text_content}')]"
                element = self.driver.find_element(By.XPATH, xpath)
                element.click()
                return f"Clicked '{tag_name}' with text '{text_content}'"
            
            click_result = await asyncio.to_thread(_click)
            print(f"✅ {click_result}")
            
            # Start monitoring IMMEDIATELY after click
            start_time = time.time()
            print(f"🔍 Starting immediate pattern monitoring for {monitor_timeout} seconds...")
            
            while time.time() - start_time < monitor_timeout:
                await asyncio.sleep(0.03)  # Ultra-fast polling to catch immediate changes
                try:
                    current_snapshot = await asyncio.to_thread(capture_detailed_snapshot)
                    
                    # Detect changes with timestamps
                    for element_key, current_details in current_snapshot.items():
                        previous_details = previous_snapshot.get(element_key)
                        if previous_details:
                            changes = {}
                            
                            # Check all trackable properties
                            for prop in ['className', 'style', 'textContent', 'id']:
                                if current_details.get(prop) != previous_details.get(prop):
                                    changes[prop] = {
                                        'from': previous_details.get(prop),
                                        'to': current_details.get(prop)
                                    }
                            
                            # Check attributes
                            for attr, value in current_details.get('attributes', {}).items():
                                old_value = previous_details.get('attributes', {}).get(attr)
                                if value != old_value:
                                    changes[f'attr_{attr}'] = {'from': old_value, 'to': value}
                            
                            if changes:
                                change_event = {
                                    'timestamp': current_details['timestamp'],
                                    'element': element_key,
                                    'path': current_details['path'],
                                    'changes': changes,
                                    'element_details': {
                                        'tagName': current_details['tagName'],
                                        'id': current_details.get('id'),
                                        'className': current_details.get('className')
                                    }
                                }
                                change_events.append(change_event)
                                change_sequence.append(change_event)
                                print(f"⚡ Immediate change detected in {element_key}: {list(changes.keys())}")
                    
                    previous_snapshot = current_snapshot
                    
                except Exception as e:
                    print(f"Error during immediate snapshot comparison: {e}")

            print(f"📊 Immediate monitoring complete. Captured {len(change_events)} change events.")
            
            if not change_events:
                return f"{click_result}. No pattern changes detected during monitoring period."
            import json
            # Enhanced pattern analysis for immediate sequences
            changes_context = json.dumps({
                'click_action': click_result,
                'total_changes': len(change_events),
                'monitoring_duration': monitor_timeout,
                'change_sequence': change_sequence,
                'unique_elements_changed': len(set(event['element'] for event in change_events)),
                'immediate_capture': True
            }, indent=2)

            # Specialized prompt for immediate pattern sequences
            pattern_analysis_prompt = f"""
            You are analyzing a pattern sequence that started IMMEDIATELY after clicking a button. This is typically a memory game or sequence challenge where elements flash in a specific order that must be replicated.

            CRITICAL ANALYSIS REQUIREMENTS:
            1. Identify the EXACT SEQUENCE ORDER from timestamps (earliest to latest)
            2. Extract element identifiers that can be used for clicking (IDs, classes, or unique text)
            3. Focus on visual changes like class additions/removals, style changes, or color modifications
            4. Provide a clear ACTION PLAN with the exact click sequence



            RESPONSE FORMAT:
            1. Pattern Type: [Brief description of what happened]
            2. Sequence Order: [List elements in chronological order based on timestamps]
            3. Click Instructions: [Exact sequence to click, with element identifiers]

            PATTERN DATA (IMMEDIATE CAPTURE):
            {changes_context}

            ANALYSIS:
            """

            try:
                response = await client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": "You are a specialized pattern recognition system for immediate sequence games. Focus on timestamp-based ordering and providing precise clicking instructions."},
                        {"role": "user", "content": pattern_analysis_prompt}
                    ],
                    temperature=0.0
                )

                analysis = response.choices[0].message.content.strip()
                
                print(f"🧠 Immediate Pattern Analysis Complete:\n{analysis}")
                return f"{click_result}. {analysis}"

            except Exception as e:
                print(f"Error in immediate pattern analysis: {e}")
                return f"{click_result}. Pattern analysis failed: {e}. Raw changes: {len(change_events)} events detected."
                
        except Exception as e:
            return f"Error in click_and_monitor: {e}"


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
      "description": "Extracts relevant visible text, URLs, and button-related info from the current webpage.",
      "parameters": {
        "type": "object",
        "properties": {},
        "additionalProperties": False
      }
    }
  },
   {
  "type": "function",
  "function": {
    "name": "click_element",
    "description": "Clicks a clickable element (like a button, link, or any interactive element) on the current webpage. Uses multiple fallback strategies including JavaScript click and ActionChains to handle complex scenarios like overlays or elements outside viewport. Supports identification by tag name with text content, element ID, class name, or CSS selector.",
    "parameters": {
      "type": "object",
      "properties": {
        "tag_name": {
          "type": "string",
          "description": "The HTML tag of the element to click (e.g., 'button', 'a', 'div', 'span', 'input'). Used in combination with text_content for text-based element identification."
        },
        "text_content": {
          "type": "string",
          "description": "The visible text content within the element. Can be exact text or partial text that the element contains. Works with tag_name to locate elements by their displayed text."
        },
        "element_id": {
          "type": "string",
          "description": "The unique ID attribute of the element to click (e.g., 'submit-button', 'login-btn'). This is the most reliable method when available."
        },
        "class_name": {
          "type": "string",
          "description": "The CSS class name of the element to click (e.g., 'btn-primary', 'nav-link'). Use only a single class name, not multiple classes."
        },
        "css_selector": {
          "type": "string",
          "description": "A CSS selector to identify the element (e.g., '.btn.primary', '#header > .nav-item:first-child', 'button[type=\"submit\"]'). This allows for complex element selection."
        }
      },
      "required": [],
      "additionalProperties": False
    }
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
    # --- NEW TOOL DEFINITION ---
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "observe_attribute_change",
    #         "description": "Monitors a list of elements for a change in a specified attribute (e.g., 'class'). Waits for a maximum of 'timeout' seconds. Returns the CSS selector of the first element that changes, or null if no change is detected.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "selectors": {
    #                     "type": "array",
    #                     "items": {"type": "string"},
    #                     "description": "An array of CSS selectors for the elements to observe (e.g., ['#box-1', '#box-2'])."
    #                 },
    #                 "attribute": {
    #                     "type": "string",
    #                     "description": "The name of the HTML attribute to monitor for changes (e.g., 'class')."
    #                 },
    #                 "timeout": {
    #                     "type": "integer",
    #                     "description": "The maximum number of seconds to wait for a change."
    #                 }
    #             },
    #             "required": ["selectors", "attribute", "timeout"]
    #         }
    #     }
    # },
    # --- END NEW TOOL DEFINITION ---
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
    },
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
    },
    {
        "type": "function",
        "function": {
            "name": "query_expander",
            "description": "Refines a user's prompt by making it more concise and specific, removing conversational noise, and converting it to lowercase while preserving critical information like URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                    "type": "string",
                    "description": "The original user's prompt to be refined."
                    }
                },
                "required": ["query"]
                }   
            }
    },
   {
    "type": "function",
    "function": {
        "name": "monitor_html_changes",
        "description": "Monitors the webpage for comprehensive DOM changes including class, style, attribute, and content modifications. Captures sequential patterns like flashing cards or buttons and provides detailed analysis of the sequence order for interaction patterns.",
        "parameters": {
            "type": "object",
            "properties": {
                "timeout": {
                    "type": "integer",
                    "description": "The maximum number of seconds to monitor for changes. Recommended 5-10 seconds for pattern detection.",
                    "default": 5
                },
                "start_immediately": {
                    "type": "boolean",
                    "description": "If true, starts monitoring with minimal delay. Use when patterns start immediately.",
                    "default": False
                }
            },
            "required": []
        }
    }
    },
    {
    "type": "function",
    "function": {
        "name": "click_and_monitor",
        "description": "Clicks an element (like 'Start Pattern' button) and IMMEDIATELY begins monitoring for DOM changes. Perfect for capturing patterns that start instantly after clicking. Combines click action with ultra-fast pattern detection.",
        "parameters": {
            "type": "object",
            "properties": {
                "tag_name": {
                    "type": "string",
                    "description": "The HTML tag of the element to click (e.g., 'button', 'a', 'div')."
                },
                "text_content": {
                    "type": "string",
                    "description": "The exact or partial visible text within the element to click."
                },
                "monitor_timeout": {
                    "type": "integer",
                    "description": "How long to monitor for pattern changes after clicking (in seconds). Default is 5.",
                    "default": 5
                }
            },
            "required": ["tag_name", "text_content"]
        }
    }
    },

    {
  "type": "function",
  "function": {
    "name": "get_interactive_elements",
    "description": "Extracts and lists all interactive elements like links, buttons, and input fields from the current page, showing their text and URLs/placeholders.",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
]