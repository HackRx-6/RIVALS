import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def input_text(url: str, tag_name: str, class_names: str, placeholder_text: str, text_to_input: str) -> str:
    """
    Finds an input field on a webpage and types text into it.

    This tool launches a headless Chrome browser, navigates to a URL, and locates
    a specific input field based on its HTML tag, CSS classes, and placeholder text.
    It then clears the field and types the provided text into it.

    Args:
        url: The URL of the page where the input field exists.
        tag_name: The HTML tag of the element (e.g., 'input', 'textarea').
        class_names: A space-separated string of the CSS classes on the element.
        placeholder_text: The placeholder text of the input field.
        text_to_input: The text that will be typed into the field.

    Returns:
        A string confirming the text was inputted, or an error message if the
        field could not be found or interacted with.
    """
    driver = None
    try:
        # --- Browser Setup ---
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1200")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)

        # --- Navigation ---
        driver.get(url)

        # --- Element Location ---
        # 1. Build a robust XPath to find candidates based on tag and placeholder.
        xpath_selector = f"//{tag_name}[@placeholder='{placeholder_text}']"
        
        # 2. Wait for at least one potential element to be present.
        wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
        
        # 3. Get all candidate elements that match the tag and placeholder.
        candidate_elements = driver.find_elements(By.XPATH, xpath_selector)

        if not candidate_elements:
            return f"Error: No '{tag_name}' elements with placeholder '{placeholder_text}' were found."

        # 4. Filter candidates by checking for the required CSS classes.
        target_element = None
        required_classes = set(class_names.split())

        for element in candidate_elements:
            element_classes = set(element.get_attribute('class').split())
            if required_classes.issubset(element_classes):
                target_element = element
                break

        # --- Action ---
        if target_element:
            # Scroll to the element, clear it, and send keys
            driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
            time.sleep(0.5)
            target_element.clear()
            target_element.send_keys(text_to_input)
            return f"Successfully inputted text into the '{tag_name}' field with placeholder '{placeholder_text}'."
        else:
            return f"Error: Found fields with tag and placeholder, but none had the required classes: '{class_names}'."

    except Exception as e:
        return f"Error: An unexpected error occurred while trying to input text: {e}"
    finally:
        if driver:
            driver.quit()

# --- Example Usage ---
if __name__ == '__main__':
    # Note: To run this example, you need to install the required libraries:
    # pip install selenium webdriver-manager

    import os
    html_content = """
    <html><body>
        <h2>User Information</h2>
        <form>
            <input type="text" class="form-control user-name" placeholder="Enter your username">
            <textarea class="form-control user-bio" placeholder="Tell us about yourself"></textarea>
            <input type="password" class="form-control user-pass" placeholder="Enter password">
        </form>
    </body></html>
    """
    with open("mock_form.html", "w") as f:
        f.write(html_content)
    
    file_url = 'file://' + os.path.realpath("mock_form.html")

    print("--- Test Case 1: Inputting username ---")
    result = input_text(
        url=file_url,
        tag_name='input',
        class_names='form-control user-name',
        placeholder_text='Enter your username',
        text_to_input='test_user_123'
    )
    print(result)
    print("-" * 20)

    print("\n--- Test Case 2: Inputting into a textarea ---")
    result = input_text(
        url=file_url,
        tag_name='textarea',
        class_names='form-control user-bio',
        placeholder_text='Tell us about yourself',
        text_to_input='This is a test biography.'
    )
    print(result)
    print("-" * 20)
    
    print("\n--- Test Case 3: Failing to find an element with wrong placeholder ---")
    result = input_text(
        url=file_url,
        tag_name='input',
        class_names='form-control user-pass',
        placeholder_text='Enter your password', # Mismatch
        text_to_input='password123'
    )
    print(result)
    print("-" * 20)

    os.remove("mock_form.html")
