import pytest
import respx
import httpx
from app.parsers.habr import HabrParser
from app.parsers.vc import VCParser
from app.parsers.ixbt import IXBTParser

@pytest.mark.asyncio
async def test_habr_parser():
    parser = HabrParser()
    
    mock_html = """
    <html>
    <body>
        <article>
            <h2 class="tm-title"><a href="/ru/articles/123/">Test Article</a></h2>
            <a class="tm-user-info__username" href="/ru/users/testuser/">testuser</a>
            <time datetime="2024-01-01T12:00:00.000Z"></time>
            <a class="tm-article-snippet__hubs-item-link">Python</a>
            <span class="tm-votes-meter__value">+10</span>
            <span class="tm-icon-counter__value">5</span>
            <span class="tm-icon-counter__value">1.5K</span>
            <div class="tm-article-snippet__lead">This is a summary of the test article. It should be long enough for language detection.</div>
        </article>
    </body>
    </html>
    """
    
    with respx.mock:
        respx.get("https://habr.com/ru/all/").mock(return_value=httpx.Response(200, text=mock_html))
        articles = []
        async for a in parser.fetch_articles():
            articles.append(a)
        
    assert len(articles) == 1
    assert articles[0]["title"] == "Test Article"
    assert articles[0]["url"] == "https://habr.com/ru/articles/123/"
    assert articles[0]["author"]["name"] == "testuser"
    assert "Python" in articles[0]["tags"]
    assert articles[0]["likes"] == 10
    assert articles[0]["comments"] == 5
    assert articles[0]["views"] == 1500
    assert articles[0]["language"] == "EN"
    
    await parser.close()

@pytest.mark.asyncio
async def test_vc_parser():
    parser = VCParser()
    
    mock_html = """
    <html>
    <body>
        <div class="feed__item">
            <a class="content-link" href="/flood/12345">VC Test Article</a>
            <a class="content-header-author__name" href="/id/1">testauthor</a>
            <time datetime="2024-01-01T15:00:00+03:00"></time>
            <a class="content-header-subsite__name">Flood</a>
            <span class="vote__value">+5</span>
            <span class="content-footer__comments-count">10</span>
            <div class="content-body">Summary of VC article. It is also in English for detection.</div>
        </div>
    </body>
    </html>
    """
    
    with respx.mock:
        respx.get("https://vc.ru/").mock(return_value=httpx.Response(200, text=mock_html))
        articles = []
        async for a in parser.fetch_articles():
            articles.append(a)
        
    assert len(articles) == 1
    assert articles[0]["title"] == "VC Test Article"
    assert articles[0]["url"] == "https://vc.ru/flood/12345"
    assert articles[0]["author"]["name"] == "testauthor"
    assert "Flood" in articles[0]["tags"]
    assert articles[0]["likes"] == 5
    assert articles[0]["comments"] == 10
    assert articles[0]["language"] == "EN"
    
    await parser.close()

@pytest.mark.asyncio
async def test_ixbt_parser():
    parser = IXBTParser()
    
    mock_html = """
    <html>
    <body>
        <div class="post-list-item">
            <h3><a href="/live/car/test-article.html">iXBT Test Article</a></h3>
            <a class="author-name" href="/live/user/1/">ixbtuser</a>
            <time datetime="2024-01-01T10:00:00+00:00"></time>
            <a class="category">Auto</a>
            <span class="votes-count">15</span>
            <span class="comments-count">3</span>
            <div class="post-content">Это длинный текст на русском языке для того чтобы детектор языка сработал правильно и вернул RU.</div>
        </div>
    </body>
    </html>
    """
    
    with respx.mock:
        respx.get("https://www.ixbt.com/live/").mock(return_value=httpx.Response(200, text=mock_html))
        articles = []
        async for a in parser.fetch_articles():
            articles.append(a)
        
    assert len(articles) == 1
    assert articles[0]["title"] == "iXBT Test Article"
    assert articles[0]["url"] == "https://www.ixbt.com/live/car/test-article.html"
    assert articles[0]["author"]["name"] == "ixbtuser"
    assert "Auto" in articles[0]["tags"]
    assert articles[0]["likes"] == 15
    assert articles[0]["comments"] == 3
    assert articles[0]["language"] == "RU"
    
    await parser.close()
