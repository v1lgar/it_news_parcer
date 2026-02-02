from typing import List, Dict, Any, AsyncGenerator, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
from app.parsers.base import BaseParser
from app.parsers.utils import detect_language, clean_text

class IXBTParser(BaseParser):
    def __init__(self, throttle_seconds: float = 1.0):
        super().__init__("iXBT Live", "https://www.ixbt.com/live", throttle_seconds)

    async def fetch_articles(self, limit: int = 20, tags: Optional[List[str]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        urls = [f"{self.base_url}/"]
        if tags:
            for tag in tags:
                urls.append(f"{self.base_url}/blog/{tag.lower()}/")
        
        count = 0
        for url in urls:
            if count >= limit:
                break
            
            html = await self.get_html(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all("div", class_="post-list-item") or soup.find_all("article")
            
            for item in items:
                if count >= limit:
                    break
                try:
                    title_elem = item.find("h3") or item.find("h2") or item.find("a", class_="post-title")
                    if not title_elem:
                        continue
                    
                    title_link = None
                    if title_elem.name == "a":
                        title_link = title_elem
                    else:
                        title_link = title_elem.find("a")
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)

                    raw_url = ""
                    href = title_link.get("href")
                    if isinstance(href, str):
                        raw_url = href

                    if not raw_url:
                        continue

                    article_url = raw_url
                    if not article_url.startswith("http"):
                        if article_url.startswith("/"):
                            article_url = "https://www.ixbt.com" + article_url
                        else:
                            article_url = self.base_url + "/" + article_url
                    
                    author_elem = item.find("a", class_="author-name") or item.find("span", class_="author")
                    author_name = author_elem.get_text(strip=True) if author_elem else "Unknown"
                    author_url = None
                    if author_elem and author_elem.name == "a":
                        auth_href = author_elem.get("href")
                        if isinstance(auth_href, str):
                            author_url = auth_href

                    if author_url and not author_url.startswith("http"):
                        if author_url.startswith("/"):
                            author_url = "https://www.ixbt.com" + author_url
                        else:
                            author_url = self.base_url + "/" + author_url

                    published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    time_elem = item.find("time")
                    date_str = ""
                    if time_elem:
                        date_attr = time_elem.get("datetime")
                        if isinstance(date_attr, str):
                            date_str = date_attr

                    if date_str:
                        try:
                            published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        except Exception:
                            pass
                    
                    article_tags = []
                    cat_elem = item.find("a", class_="category") or item.find("span", class_="category")
                    if cat_elem:
                        article_tags.append(cat_elem.get_text(strip=True))

                    likes = 0
                    votes = item.find("span", class_="votes-count") or item.find("div", class_="votes")
                    if votes:
                        try:
                            likes = int(re.sub(r'[^\d\-]', '', votes.get_text(strip=True)))
                        except Exception:
                            pass
                    
                    comments = 0
                    comm_elem = item.find("span", class_="comments-count")
                    if comm_elem:
                        try:
                            comments = int(re.sub(r'[^\d]', '', comm_elem.get_text(strip=True)))
                        except Exception:
                            pass

                    summary_elem = item.find("div", class_="post-content") or item.find("p")
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
