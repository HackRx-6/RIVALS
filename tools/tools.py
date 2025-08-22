# tools.py
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
# ToolsFunctionCalling
from openai import AsyncOpenAI
  
import re
import os
import uuid
import re
client = AsyncOpenAI()
# client = AsyncOpenAI(
#         api_key="YOUR_API_KEY_PLACEHOLDER", # Can be anything, as the proxy uses the header key.
#         base_url="https://register.hackrx.in/llm/openai", # This points all requests to the proxy URL.
#         default_headers={
#             "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
#     })


class ToolsFunctionCalling:
    """
    Manages a single, persistent Selenium WebDriver session.
    This version is fully asynchronous to work with the asyncio framework.
    """
    def __init__(self):
        print("🚀 Initializing browser session setup...")
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Browser driver initialized.")

    async def navigate(self, url: str) -> str:
        """Asynchronously navigates the browser to a specific URL."""
        try:
            await asyncio.to_thread(self.driver.get, url)
            return f"Successfully navigated to {url}."
        except Exception as e:
            return f"Error navigating: {e}"

    async def read_content(self) -> str:
        """Asynchronously reads the HTML body of the current page."""
        try:
            def _get_source():
                import time
                time.sleep(0.5)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                body = soup.find('body')
                if not body: return "Error: Could not find the <body> tag."
                for tag in body.find_all(['script', 'style']):
                    tag.decompose()

                print(str(body))
                return str(body)
            return await asyncio.to_thread(_get_source)
        except Exception as e:
            return f"Error reading content: {e}"

    async def click_element(self, tag_name: str, text_content: str) -> str:
        """Asynchronously clicks an element by its tag and text."""
        try:
            def _click():
                xpath = f"//{tag_name}[contains(., '{text_content}')]"
                element = self.driver.find_element(By.XPATH, xpath)
                element.click()
                return f"Successfully clicked the '{tag_name}' with text '{text_content}'."
            return await asyncio.to_thread(_click)
        except Exception as e:
            return f"Error clicking element: {e}"

    async def input_text(self, placeholder_text: str, text_to_input: str, tag_name: str = "input") -> str:
        """Asynchronously types text into an input field."""
        try:
            def _input():
                xpath = f"//{tag_name}[@placeholder='{placeholder_text}']"
                element = self.driver.find_element(By.XPATH, xpath)
                element.clear()
                element.send_keys(text_to_input)
                return f"Successfully typed '{text_to_input}' into the field."
            return await asyncio.to_thread(_input)
        except Exception as e:
            return f"Error inputting text: {e}"
  

    # --- Make sure this is defined somewhere in your class ---
    # self.output_dir = "generated_code" 
    # os.makedirs(self.output_dir, exist_ok=True)

    async def generate_code(self, query: str):
        """
        Generates executable code, saves it to a .py file, 
        and returns the file path.
        """
        print(f"Generating code for query: {query}")
        
        # Define and ensure the output directory exists
        output_dir = "generated_code"
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

        # Return the path to the newly created file
        return file_path



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
        "description": "Generates executable code for a given coding query without and rreturns the file path where the code is saved.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The coding problem or request to generate code for."
                }
            },
            "required": ["query"]
        }
    }
}
]