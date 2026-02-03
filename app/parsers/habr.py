from typing import List, Dict, Any, AsyncGenerator, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.parsers.base import BaseParser
from app.parsers.utils import detect_language, clean_text

class HabrParser(BaseParser):
    def __init__(self, throttle_seconds: float = 1.0):
        super().__init__("Habr", "https://habr.com", throttle_seconds)

    async def fetch_articles(self, limit: int = 20, tags: Optional[List[str]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        urls = [f"{self.base_url}/ru/all/"]
        if tags:
            for tag in tags:
                # Note: Habr hub names might need normalization if passed as "Python" instead of "python"
                urls.append(f"{self.base_url}/ru/hubs/{tag.lower()}/articles/")
        
        count = 0
        for url in urls:
            if count >= limit:
                break
            
            html = await self.get_html(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all("article")
            
            for item in items:
                if count >= limit:
                    break
                try:
                    title_elem = item.find("h2", class_="tm-title")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    a_tag = title_elem.find("a")
                    if not a_tag:
                        continue
                    href = a_tag.get("href")
                    if not isinstance(href, str):
                        continue
                    article_url = self.base_url + href
                    
                    author_elem = item.find("a", class_="tm-user-info__username")
                    author_name = author_elem.get_text(strip=True) if author_elem else "Unknown"
                    author_url = None
                    if author_elem:
                        auth_href = author_elem.get("href")
                        if isinstance(auth_href, str):
                            author_url = self.base_url + auth_href
                    
                    date_elem = item.find("time")
                    date_str = ""
                    if date_elem:
                        date_attr = date_elem.get("datetime")
                        if isinstance(date_attr, str):
                            date_str = date_attr

                    if date_str:
                        published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    else:
                        published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    
                    hubs = [a.get_text(strip=True).replace("*", "").strip() for a in item.find_all("a", class_="tm-article-snippet__hubs-item-link")]
                    
                    votes_elem = item.find("span", class_="tm-votes-meter__value")
                    likes = 0
                    if votes_elem:
                        votes_text = votes_elem.get_text(strip=True).replace("−", "-")
                        try:
                            likes = int(votes_text.replace("+", ""))
                        except ValueError:
                            likes = 0
                    
                    stats = item.find_all("span", class_="tm-icon-counter__value")
                    comments = 0
                    views = 0
                    if len(stats) >= 2:
                        comments_text = stats[0].get_text(strip=True)
                        views_text = stats[1].get_text(strip=True)
                        if "K" in views_text:
                            views = int(float(views_text.replace("K", "")) * 1000)
                        elif views_text.isdigit():
                            views = int(views_text)
                        if comments_text.isdigit():
                            comments = int(comments_text)

                    summary_elem = item.find("div", class_="tm-article-snippet__lead")
                    summary = clean_text(str(summary_elem)) if summary_elem else ""
                    language = detect_language(title + " " + summary)

                    yield {
                        "title": title,
                        "url": article_url,
                        "author": {"name": author_name, "profile_url": author_url},
                        "published_at": published_at,
                        "tags": hubs,
                        "likes": likes,
                        "views": views,
                        "comments": comments,
                        "summary": summary,
                        "language": language,
                        "source": self.name
                    }
                    count += 1
                except Exception:
                    continue
