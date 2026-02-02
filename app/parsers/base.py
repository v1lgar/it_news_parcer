import asyncio
import httpx
import structlog
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional

logger = structlog.get_logger()

class BaseParser(ABC):
    def __init__(self, name: str, base_url: str, throttle_seconds: float = 1.0):
        self.name = name
        self.base_url = base_url
        self.throttle_seconds = throttle_seconds
        self.client = httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
            timeout=30.0,
            follow_redirects=True
        )

    @abstractmethod
    async def fetch_articles(self, limit: int = 20, tags: Optional[List[str]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch articles from the source, optionally filtered by tags.
        Yields article dictionaries.
        """
        # This is an abstract async generator.
        # We need a dummy yield to make it an AsyncGenerator if it were not abstract.
        # But for @abstractmethod, we just need the type hint.
        if False: yield {}

    async def get_html(self, url: str) -> str:
        """Fetch HTML content of a URL with throttling."""
        await asyncio.sleep(self.throttle_seconds)
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error("Error fetching URL", url=url, error=str(e))
            return ""

    async def close(self):
        await self.client.aclose()
