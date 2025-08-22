import markdown
from bs4 import BeautifulSoup
import re
import html
import unicodedata
import sys
import requests
from urllib.parse import urlparse
import os

# Ensure stdout uses UTF-8 encoding to handle special characters like ₹
sys.stdout.reconfigure(encoding='utf-8')


def clean_text(raw_text: str) -> str:
    """
    Cleans a string by removing common formatting artifacts.
    """
    if isinstance(raw_text, bytes):
        try:
            raw_text = raw_text.decode('utf-8')
        except UnicodeDecodeError:
            raw_text = raw_text.decode('latin1', errors='replace')

    # Step 1: Unescape HTML entities like &amp; or &quot;
    unescaped_text = html.unescape(raw_text)

    # Step 2: Normalize Unicode characters (handles rupee, accents, etc.)
    normalized_text = unicodedata.normalize('NFC', unescaped_text)

    # Step 3: Normalize whitespace (replace multiple spaces, tabs, newlines with a single space)
    cleaned_text = re.sub(r'\s+', ' ', normalized_text)

    return cleaned_text.strip()


def clean_markdown(md_text: str) -> str:
    """
    Converts Markdown to plain, cleaned text.
    """
    if not isinstance(md_text, str):
        return ""

    # Convert Markdown to HTML
    html_text = markdown.markdown(md_text)

    # Strip HTML tags
    soup = BeautifulSoup(html_text, "html.parser")
    plain_text = soup.get_text(separator=' ')

    # Clean entities, Unicode, spacing
    cleaned_text = clean_text(plain_text).replace('*', ' ')
    normalized_spacing = cleaned_text.split()

    return ' '.join(normalized_spacing).strip()


def beautify_text(text: str) -> str:
    """
    Entry point: removes Markdown, HTML tags, weird spacing,
    HTML entities, and ensures plain readable text.
    """
    return clean_markdown(text)


def get_text_from_url(url: str) -> str:
    """
    Fetches visible text from a webpage (ignores scripts/styles).
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove scripts and styles
        for s in soup(['script', 'style']):
            s.decompose()

        return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.RequestException as e:
        return f"Error: Could not retrieve the URL. {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def is_file_url(url: str) -> bool:
    """
    Checks if a URL likely points to a downloadable file.
    """
    try:
        file_extensions = [
            '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.rar', '.7z',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.mp3', '.wav', '.ogg',
            '.mp4', '.avi', '.mov', '.wmv',
            '.json', '.xml', '.csv', '.txt', '.rtf',
            '.bin', '.iso', '.exe', '.dll'
        ]
        path = urlparse(url).path
        _, extension = os.path.splitext(path)
        return extension.lower() in file_extensions
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    raw_markdown = """
    Based on the policy, the claim is admissible.

    **Admissibility:**
    1. **Dependent Eligibility:** Children up to 26...
    2. **Dental Exclusion:** Covered only if...
    """
    print("Beautified:", beautify_text(raw_markdown))

    file_url = "https://hackrx.blob.core.windows.net/assets/example.pdf"
    print(f"Is '{file_url}' a file? {is_file_url(file_url)}")

    website_url = "https://register.hackrx.in/utils/get-secret-token?hackTeam=4366"
    print(f"Is '{website_url}' a file? {is_file_url(website_url)}")
