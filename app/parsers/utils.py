import re
from langdetect import detect, DetectorFactory
from bs4 import BeautifulSoup

# Ensure consistent results for langdetect
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Detect language of the text. Returns 'RU', 'EN' or 'OTHER'."""
    if not text or len(text.strip()) < 10:
        return "OTHER"
    try:
        lang = detect(text)
        if lang == "ru":
            return "RU"
        elif lang == "en":
            return "EN"
        return "OTHER"
    except Exception:
        return "OTHER"

def clean_text(html_content: str) -> str:
    """Clean HTML content, removing ads and extra whitespace."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove common ad blocks or script/style tags
    for element in soup(["script", "style", "iframe", "adv"]):
        element.decompose()
        
    # Get text and clean whitespace
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
