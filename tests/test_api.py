import pytest
from httpx import AsyncClient, ASGITransport
from app.api.main import app
from app.db.base import get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.models import Base, Article, Author, Source
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_get_articles():
    # Setup test DB
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Dependency override
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
            
    app.dependency_overrides[get_db] = override_get_db
    
    # Add mock data
    async with TestSessionLocal() as session:
        source = Source(name="Habr", url="")
        author = Author(name="testauthor")
        session.add_all([source, author])
        await session.flush()
        
        article = Article(
            title="API Test",
            url="https://example.com/api-test",
            published_at=datetime.now(timezone.utc).replace(tzinfo=None),
            language="EN",
            source_id=source.id,
            author_id=author.id
        )
        session.add(article)
        await session.commit()
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/articles")
        
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "API Test"
    
    app.dependency_overrides.clear()
