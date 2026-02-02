from app.parsers.utils import detect_language, clean_text

def test_detect_language():
    assert detect_language("Это длинный текст на русском языке для проверки определения языка.") == "RU"
    assert detect_language("This is a long text in English to verify language detection correctly.") == "EN"
    assert detect_language("") == "OTHER"
    assert detect_language("1234567890") == "OTHER"

def test_clean_text():
    html = "<div>Hello <script>alert(1)</script> world!   </div>"
    assert clean_text(html) == "Hello world!"
    
    html_with_ads = "<div>Main content <adv>Buy this!</adv></div>"
    assert clean_text(html_with_ads) == "Main content"
