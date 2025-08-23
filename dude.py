import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- IMPORTANT: UPDATE THIS PATH ---
# Use the full path to your HTML file, for example: 'C:/Users/YourUser/Desktop/challenge.html'
CHALLENGE_FILE_PATH = "https://register.hackrx.in/showdown/v2/startChallenge/ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiMjlzUjNWNUlqb2lVa2xVUlZOSUlpd2lZMmhoYkd4bGJtZGxTVVFpT2lKd1lYUjBaWEp1SWl3aWRYTmxja2xrSWpvaWRYTmxjbDl5YVhSbGMyZ2lMQ0psYldGcGJDSTZJbkpwZEdWemFFQmlZV3BoYW1acGJuTmxjblpvWldGc2RHZ3VhVzRpTENKeWIyeGxJam9pWTI5dmJGOW5kWGtpTENKcFlYUWlPakUzTlRVNU1ERTNNVEFzSW1WNGNDSTZNVGMxTlRrNE9ERXhNSDAuMzJSeDRDZ3drSTNkdUV5eXdmbjZUSUdQQS1DSVBqTmpCdl9CWG1Wc1VxVQ=="
# ------------------------------------

def run_debug_script():
    """
    A simple script to isolate and debug the event watcher.
    """
    print("🚀 Starting debug script...")

    # --- Correct, complete browser setup ---
    chrome_options = webdriver.ChromeOptions()
    # You can add options here, e.g., chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # ----------------------------------------

    # JavaScript payload for the event logger
    log_events_script = """
        const callback = arguments[arguments.length - 1];
        const selector = '.light';
        const attrToWatch = 'class';
        const duration = 8000; // 8 seconds
        
        const eventLog = [];
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length === 0) {
                callback({ status: 'error', message: 'No elements found to observe.' });
                return;
            }
            const observer = new MutationObserver((mutationsList) => {
                for (const mutation of mutationsList) {
                    if (mutation.type === 'attributes' && mutation.attributeName === attrToWatch) {
                        const target = mutation.target;
                        eventLog.push({
                            elementId: target.id,
                            attributeName: mutation.attributeName,
                            newValue: target.getAttribute(attrToWatch)
                        });
                    }
                }
            });
            const container = elements[0].parentElement;
            observer.observe(container, { attributes: true, subtree: true, attributeFilter: [attrToWatch] });
            setTimeout(() => {
                observer.disconnect();
                callback({ status: 'success', log: eventLog });
            }, duration);
        } catch (e) {
            callback({ status: 'error', message: e.message });
        }
    """

    try:
        # 1. Navigate to the page
        driver.get(CHALLENGE_FILE_PATH)
        print("✅ Navigated to page.")
        
        # 2. Intelligently wait for the start button to appear
        print("⏳ Waiting for the start button to appear...")
        wait = WebDriverWait(driver, 10) # Wait up to 10 seconds
        start_button = wait.until(EC.element_to_be_clickable((By.ID, 'startBtn')))
        
        # 3. Click the start button
        start_button.click()
        print("✅ Clicked the 'Start Flashing' button.")
        print("📡 Now listening for events for 8 seconds...")

        # 4. Run the event logger
        result = driver.execute_async_script(log_events_script)

        # 5. Print the result
        print("\n--- Captured Events ---")
        if result and result.get('status') == 'success':
            print(json.dumps(result.get('log', []), indent=2))
        else:
            print("An error occurred or no events were captured.")
            print(result)
        print("---------------------\n")

    finally:
        print("🛑 Closing browser.")
        driver.quit()

if __name__ == "__main__":
    run_debug_script()