from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def visit_url(url: str) -> str:
    """
    Visits a given URL using a headless Chrome browser to simulate a user visit.

    This tool launches a headless instance of Google Chrome to navigate to the
    provided URL. It waits for the page to fully load, executing any necessary
    JavaScript. Its primary purpose is to trigger any actions that might occur
    on page load and confirm that the page is accessible.

    Args:
        url: The full URL of the website to visit (e.g., 'https://www.example.com').

    Returns:
        A string confirming successful navigation, or an error message if the
        navigation fails.
    """
    driver = None  # Initialize driver to None
    try:
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Automatically download and manage the ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set a page load timeout to prevent hanging
        driver.set_page_load_timeout(20)

        # Navigate to the URL
        driver.get(url)

        # If the get() method completes without an exception, navigation was successful.
        return f"Successfully navigated to the URL: {url}"

    except Exception as e:
        return f"Error: An unexpected error occurred while trying to visit the URL with Chrome: {e}"
    finally:
        # Ensure the driver is closed even if an error occurs
        if driver:
            driver.quit()

# --- Example Usage ---
if __name__ == '__main__':
    # Note: To run this example, you need to install the required libraries:
    # pip install selenium webdriver-manager

    # Example with a known working URL
    working_url = "https://www.google.com"
    print(f"Attempting to visit URL: {working_url}\n")
    
    status_message = visit_url(working_url)
    
    print("--- Navigation Status ---")
    print(status_message)
    print("-------------------------\n")

    # Example with a non-existent URL to show error handling
    invalid_url = "https://thissitedoesnotexist.invalid"
    print(f"Attempting to visit URL: {invalid_url}\n")
    
    status_message = visit_url(invalid_url)
    
    print("--- Navigation Status ---")
    print(status_message)
    print("-------------------------")
