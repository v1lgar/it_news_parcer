import structlog
from typing import List, Dict, Any
from sqlalchemy import select
from app.db.models import Article, Author, Tag, Source
from app.parsers.habr import HabrParser
from app.parsers.vc import VCParser
from app.parsers.ixbt import IXBTParser
from app.db.base import AsyncSessionLocal

logger = structlog.get_logger()

class ParsingService:
    def __init__(self):
        self.parsers = [
            HabrParser(),
            VCParser(),
            IXBTParser()
        ]

    async def run_all(self, limit: int = 20, tags: List[str] = None):
        logger.info("Starting parsing task for all sources", tags=tags)
        for parser in self.parsers:
            try:
                count = 0
                async for article_data in parser.fetch_articles(limit=limit, tags=tags):
                    await self.save_article(article_data)
                    count += 1
                logger.info("Fetched articles", source=parser.name, count=count)
            except Exception as e:
                logger.error("Error running parser", source=parser.name, error=str(e))
        logger.info("Finished parsing task")

    async def save_article(self, data: Dict[str, Any]):
        async with AsyncSessionLocal() as session:
            try:
                # Check if article already exists
                stmt = select(Article).where(Article.url == data["url"])
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    return
                
                # Get or create Source
                source_stmt = select(Source).where(Source.name == data["source"])
                source_res = await session.execute(source_stmt)
                source = source_res.scalar_one_or_none()
                if not source:
                    source = Source(name=data["source"], url="")
                    session.add(source)
                    await session.flush()
                
                # Get or create Author
                author_stmt = select(Author).where(Author.name == data["author"]["name"])
                author_res = await session.execute(author_stmt)
                author = author_res.scalar_one_or_none()
                if not author:
                    author = Author(name=data["author"]["name"], profile_url=data["author"]["profile_url"])
                    session.add(author)
                    await session.flush()
                
                # Get or create Tags
                tags = []
                for tag_name in data["tags"]:
                    tag_stmt = select(Tag).where(Tag.name == tag_name)
                    tag_res = await session.execute(tag_stmt)
                    tag = tag_res.scalar_one_or_none()
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        await session.flush()
                    tags.append(tag)
                
                # Create Article
                article = Article(
                    title=data["title"],
                    url=data["url"],
                    published_at=data["published_at"],
                    summary=data["summary"],
                    language=data["language"],
                    likes=data["likes"],
                    views=data["views"],
                    comments=data["comments"],
                    source_id=source.id,
                    author_id=author.id,
                    tags=tags
                )
                session.add(article)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Error saving article", url=data.get("url"), error=str(e))

    async def close(self):
        for parser in self.parsers:
            await parser.close()
