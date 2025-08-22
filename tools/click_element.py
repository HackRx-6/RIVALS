import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def click_element(url: str, tag_name: str, class_names: str, text_content: str) -> str:
    """
    Finds and clicks an element on a webpage based on its tag, classes, and text.

    This tool launches a headless Chrome browser, navigates to a URL, and then
    attempts to locate a specific clickable element. It uses a combination of the
    element's HTML tag, its CSS classes, and the visible text it contains to
    ensure it finds the correct one.

    Args:
        url: The URL of the page where the element exists.
        tag_name: The HTML tag of the element (e.g., 'button', 'a', 'div').
        class_names: A space-separated string of the CSS classes on the element
                     (e.g., 'btn btn-primary start-button').
        text_content: The exact or partial text visible within the element.

    Returns:
        A string confirming the element was clicked, or an error message if it
        could not be found or clicked.
    """
    driver = None
    try:
        # --- Browser Setup ---
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds for elements

        # --- Navigation ---
        driver.get(url)

        # --- Element Location ---
        # 1. Build a robust XPath to find candidates based on tag and text.
        #    Using contains(., 'text') is more flexible than contains(text(), 'text')
        #    as it checks descendant text nodes as well.
        xpath_selector = f"//{tag_name}[contains(., '{text_content}')]"
        
        # 2. Wait for at least one potential element to be present on the page.
        wait.until(EC.presence_of_element_located((By.XPATH, xpath_selector)))
        
        # 3. Get all candidate elements that match the tag and text.
        candidate_elements = driver.find_elements(By.XPATH, xpath_selector)

        if not candidate_elements:
            return f"Error: No elements with tag '{tag_name}' and text '{text_content}' were found."

        # 4. Filter the candidates by checking for the required CSS classes.
        target_element = None
        required_classes = set(class_names.split())

        for element in candidate_elements:
            element_classes = set(element.get_attribute('class').split())
            if required_classes.issubset(element_classes):
                target_element = element
                break # Found the first element that matches all criteria

        # --- Action ---
        if target_element:
            # Scroll the element into view and click it using JavaScript to avoid interception issues
            driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
            time.sleep(0.5) # Brief pause to ensure it's ready for click
            driver.execute_script("arguments[0].click();", target_element)
            return f"Successfully clicked the '{tag_name}' element with text '{text_content}'."
        else:
            return f"Error: Found elements with tag and text, but none had the required classes: '{class_names}'."

    except Exception as e:
        return f"Error: An unexpected error occurred while trying to click the element: {e}"
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    # Note: To run this example, you need to install the required libraries:
    # pip install selenium webdriver-manager

    # This is a mock HTML file to demonstrate the functionality without a live website.
    import os
    html_content = """
    <html>
    <body>
        <h1>Mock Page for Testing</h1>
        <p>Some content here.</p>
        <div style="height: 1500px;"></div> <!-- Spacer to test scrolling -->
        <button class="btn btn-primary action-btn">Do Something Else</button>
        <a href="#" class="btn btn-secondary start-challenge">Start Challenge</a>
        <div class="card-footer text-center">
            <button class="btn btn-success action-btn final-click">Submit Answer</button>
        </div>
    </body>
    </html>
    """
    with open("mock_page.html", "w") as f:
        f.write(html_content)
    
    # Get the file path URL
    file_url = 'file://' + os.path.realpath("mock_page.html")

    print("--- Test Case 1: Clicking the 'a' tag ---")
    result = click_element(
        url=file_url,
        tag_name='a',
        class_names='btn start-challenge',
        text_content='Start Challenge'
    )
    print(result)
    print("-" * 20)

    print("\n--- Test Case 2: Clicking the final button inside a div ---")
    result = click_element(
        url=file_url,
        tag_name='button',
        class_names='btn btn-success final-click',
        text_content='Submit Answer'
    )
    print(result)
    print("-" * 20)
    
    print("\n--- Test Case 3: Failing to find an element with wrong class ---")
    result = click_element(
        url=file_url,
        tag_name='button',
        class_names='btn wrong-class',
        text_content='Submit Answer'
    )
    print(result)
    print("-" * 20)

    # Clean up the mock file
    os.remove("mock_page.html")