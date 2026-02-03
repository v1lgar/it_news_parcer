from typing import List, Dict, Any, AsyncGenerator, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.parsers.base import BaseParser
from app.parsers.utils import detect_language, clean_text

class VCParser(BaseParser):
    def __init__(self, throttle_seconds: float = 1.0):
        super().__init__("VC.ru", "https://vc.ru", throttle_seconds)

    async def fetch_articles(self, limit: int = 20, tags: Optional[List[str]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        urls = [f"{self.base_url}/"]
        if tags:
            for tag in tags:
                urls.append(f"{self.base_url}/{tag.lower()}/")
        
        count = 0
        for url in urls:
            if count >= limit:
                break
            
            html = await self.get_html(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "lxml")
            items = soup.find_all("div", class_="feed__item") or soup.find_all("div", class_="content")
            
            for item in items:
                if count >= limit:
                    break
                try:
                    title_link = item.find("a", class_="content-link") or item.find("div", class_="content-title")
                    if not title_link:
                        title_link = item.find("a")
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)

                    raw_url = ""
                    if title_link.name == "a":
                        href = title_link.get("href")
                        if isinstance(href, str):
                            raw_url = href
                    else:
                        a_in_title = title_link.find("a")
                        if a_in_title:
                            href = a_in_title.get("href")
                            if isinstance(href, str):
                                raw_url = href

                    if not raw_url:
                        continue

                    article_url = raw_url
                    if not article_url.startswith("http"):
                        article_url = self.base_url + article_url
                    
                    author_elem = item.find("a", class_="content-header-author__name")
                    author_name = author_elem.get_text(strip=True) if author_elem else "Unknown"
                    author_url = None
                    if author_elem:
                        auth_href = author_elem.get("href")
                        if isinstance(auth_href, str):
                            author_url = auth_href
                            if not author_url.startswith("http"):
                                author_url = self.base_url + author_url

                    time_elem = item.find("time")
                    date_str = ""
                    if time_elem:
                        date_attr = time_elem.get("datetime")
                        if isinstance(date_attr, str):
                            date_str = date_attr

                    if date_str:
                        published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                    else:
                        published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    
                    article_tags = []
                    subsite = item.find("a", class_="content-header-subsite__name")
                    if subsite:
                        article_tags.append(subsite.get_text(strip=True))

                    likes = 0
                    votes = item.find("span", class_="vote__value")
                    if votes:
                        try:
                            likes = int(votes.get_text(strip=True).replace("+", "").replace("−", "-"))
                        except Exception:
                            pass
                    
                    comments = 0
                    comm_elem = item.find("span", class_="content-footer__comments-count")
                    if comm_elem:
                        try:
                            comments = int(comm_elem.get_text(strip=True))
                        except Exception:
                            pass

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
