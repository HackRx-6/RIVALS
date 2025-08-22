import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def view_website_source(url: str) -> str:
    """
    Fetches and returns the full HTML source code from a given URL using a headless Chrome browser.

    This tool launches a headless instance of Google Chrome to navigate to the
    provided URL. It waits for the page to load and executes JavaScript, then
    returns the final HTML source. This is essential for modern, single-page
    applications (SPAs) or any website that relies on JavaScript to render its content.

    Args:
        url: The full URL of the website to visit (e.g., 'https://www.example.com').

    Returns:
        A string containing the full, JavaScript-rendered HTML source of the webpage.
        If the navigation fails, it returns an error message.
    """
    try:
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1200")

        # Automatically download and manage the ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set a page load timeout to prevent hanging
        driver.set_page_load_timeout(20)

        # Navigate to the URL
        driver.get(url)

        # Get the page source after JavaScript has executed
        html_source = driver.page_source
        
        return html_source

    except Exception as e:
        return f"Error: An unexpected error occurred while processing the website with Chrome: {e}"
    finally:
        # Ensure the driver is closed even if an error occurs
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == '__main__':
    # Note: To run this example, you need to install the required libraries:
    # pip install selenium webdriver-manager

    # Example for the scenario you provided
    # NOTE: The token in the URL is a placeholder and will not work.
    target_url = "https://register.hackrx.in/showdown/startChallenge/placeholder_base64_token"
    
    print(f"Attempting to get source for URL with Chrome: {target_url}\n")
    
    # We expect an error or a login page, as the token is invalid.
    html_source = view_website_source(target_url)
    
    print("--- Retrieved Source (first 500 chars) ---")
    print(html_source[:500] + "...")
    print("------------------------------------------\n")

    # Example with a known dynamic website
    working_url = "https://www.google.com"
    print(f"Attempting to get source for URL with Chrome: {working_url}\n")
    
    html_source = view_website_source(working_url)
    
    print("--- Retrieved Source (first 500 chars) ---")
    print(html_source[:500] + "...")
    print("------------------------------------------")