from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey, Table, Column, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    url: Mapped[str] = mapped_column(String(255))
    articles: Mapped[List["Article"]] = relationship(back_populates="source")

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(512))
    articles: Mapped[List["Article"]] = relationship(back_populates="author")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    articles: Mapped[List["Article"]] = relationship(
        secondary=article_tags, back_populates="tags"
    )

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    full_text: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), index=True) # RU/EN
    
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    author: Mapped["Author"] = relationship(back_populates="articles")
    source: Mapped["Source"] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=article_tags, back_populates="articles"
    )
