import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.models import Base, Article
from app.services.orchestrator import ParsingService
from sqlalchemy import select
from datetime import datetime, timezone
import app.services.orchestrator as orchestrator

@pytest.mark.asyncio
async def test_save_articles():
    # Mock AsyncSessionLocal to use in-memory sqlite
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Patch the AsyncSessionLocal in orchestrator module
    orchestrator.AsyncSessionLocal = TestSessionLocal
    
    service = ParsingService()
    
    test_data = {
        "title": "Test Integration",
        "url": "https://example.com/test",
        "author": {"name": "testauthor", "profile_url": "https://example.com/author"},
        "published_at": datetime.now(timezone.utc).replace(tzinfo=None),
        "tags": ["Tag1", "Tag2"],
        "likes": 10,
        "views": 100,
        "comments": 5,
        "summary": "Summary text",
        "language": "EN",
        "source": "Habr"
    }
    
    await service.save_article(test_data)
    
    from sqlalchemy.orm import selectinload
    async with TestSessionLocal() as session:
        stmt = select(Article).options(selectinload(Article.tags)).where(Article.url == "https://example.com/test")
        result = await session.execute(stmt)
        article = result.scalar_one_or_none()
        
        assert article is not None
        assert article.title == "Test Integration"
        assert len(article.tags) == 2
        
    await service.close()
