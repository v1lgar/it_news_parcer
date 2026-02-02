from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.db.base import get_db
from app.db.models import Article, Tag
from app.api.schemas import ArticleSchema

app = FastAPI(title="IT News Parser API")

@app.get("/articles", response_model=List[ArticleSchema])
async def get_articles(
    tag: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.tags)
    )
    
    filters = []
    if tag:
        query = query.join(Article.tags).where(Tag.name == tag)
    
    if date_from:
        filters.append(Article.published_at >= date_from)
    if date_to:
        filters.append(Article.published_at <= date_to)
        
    if filters:
        query = query.where(and_(*filters))
        
    query = query.order_by(Article.published_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    return articles

@app.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag.name).order_by(Tag.name))
    return result.scalars().all()

@app.get("/health")
async def health():
    return {"status": "ok"}
