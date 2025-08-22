import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def view_website_source(url: str) -> str:
    """
    Fetches and returns the HTML source code of the <body> tag from a given URL,
    after removing all <script> and <style> tags.

    This tool uses a headless Chrome browser to ensure all JavaScript is executed
    before parsing the HTML.

    Args:
        url: The full URL of the website to visit (e.g., 'https://www.example.com').

    Returns:
        A string containing the cleaned HTML of the <body> tag.
        If an error occurs or the body tag is not found, it returns an error message.
    """
    try:
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1200")

        print(f"view_website_body called with: {url}")

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

        # --- MODIFICATION START ---
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Find the body tag
        body = soup.find('body')

        if not body:
            return "Error: Could not find the <body> tag in the page source."

        # Remove all <script> and <style> tags from the body
        for tag in body.find_all(['script', 'style']):
            tag.decompose()
        
        # Return the cleaned HTML of the body


        print(body)
        return body
        # --- MODIFICATION END ---

    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"
    finally:
        # Ensure the driver is closed even if an error occurs
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == '__main__':
    # Note: To run this example, you need to install the required libraries:
    # pip install selenium webdriver-manager beautifulsoup4

    # Example with a known dynamic website
    working_url = "https://www.google.com"
    print(f"Attempting to get body source for URL: {working_url}\n")
    
    body_html = view_website_source(working_url)
    
    print("--- Retrieved Body HTML (first 500 chars) ---")
    print(body_html[:500] + "...")
    print("------------------------------------------")