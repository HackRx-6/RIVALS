import re

def beautify_text(s: str) -> str:
    # Remove markdown headers/lists/quotes
    s = re.sub(r'(^|\s)[#>*-]+', ' ', s)
    
    # Remove bold/italic/inline code markers (*, _, `)
    s = re.sub(r'[*_`]', '', s)
    
    
    # Replace newlines with spaces
    s = s.replace('\n', ' ')
    
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    
    return s.strip()
