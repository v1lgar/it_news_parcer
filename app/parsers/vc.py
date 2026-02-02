import asyncio
from typing import List, Dict, Any, AsyncGenerator
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.parsers.base import BaseParser
from app.parsers.utils import detect_language, clean_text

class VCParser(BaseParser):
    def __init__(self, throttle_seconds: float = 1.0):
        super().__init__("VC.ru", "https://vc.ru", throttle_seconds)

    async def fetch_articles(self, limit: int = 20, tags: List[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        urls = [f"{self.base_url}/"]
        if tags:
            for tag in tags:
                urls.append(f"{self.base_url}/{tag.lower()}/")
        
        count = 0
        for url in urls:
            if count >= limit: break
            
            html = await self.get_html(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all("div", class_="feed__item") or soup.find_all("div", class_="content")
            
            for item in items:
                if count >= limit: break
                try:
                    title_link = item.find("a", class_="content-link") or item.find("div", class_="content-title")
                    if not title_link: 
                        title_link = item.find("a")
                    if not title_link: continue
                    
                    title = title_link.get_text(strip=True)
                    article_url = title_link["href"] if title_link.name == "a" else (title_link.find("a")["href"] if title_link.find("a") else "")
                    if not article_url.startswith("http"):
                        article_url = self.base_url + article_url
                    
                    author_elem = item.find("a", class_="content-header-author__name")
                    author_name = author_elem.get_text(strip=True) if author_elem else "Unknown"
                    author_url = author_elem["href"] if author_elem else None
                    if author_url and not author_url.startswith("http"):
                        author_url = self.base_url + author_url

                    time_elem = item.find("time")
                    published_at = datetime.fromisoformat(time_elem["datetime"].replace("Z", "+00:00")).replace(tzinfo=None) if time_elem and time_elem.get("datetime") else datetime.now(timezone.utc).replace(tzinfo=None)
                    
                    article_tags = []
                    subsite = item.find("a", class_="content-header-subsite__name")
                    if subsite:
                        article_tags.append(subsite.get_text(strip=True))

                    likes = 0
                    votes = item.find("span", class_="vote__value")
                    if votes:
                        try:
                            likes = int(votes.get_text(strip=True).replace("+", "").replace("−", "-"))
                        except: pass
                    
                    comments = 0
                    comm_elem = item.find("span", class_="content-footer__comments-count")
                    if comm_elem:
                        try:
                            comments = int(comm_elem.get_text(strip=True))
                        except: pass

                    summary_elem = item.find("div", class_="content-body") or item.find("p")
                    summary = clean_text(str(summary_elem)) if summary_elem else ""
                    language = detect_language(title + " " + summary)

                    yield {
                        "title": title,
                        "url": article_url,
                        "author": {"name": author_name, "profile_url": author_url},
                        "published_at": published_at,
                        "tags": article_tags,
                        "likes": likes,
                        "views": 0,
                        "comments": comments,
                        "summary": summary,
                        "language": language,
                        "source": self.name
                    }
                    count += 1
                except Exception:
                    continue
