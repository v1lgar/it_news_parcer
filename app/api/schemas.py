from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class AuthorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    profile_url: Optional[str] = None

class TagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str

class ArticleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    url: str
    published_at: datetime
    summary: Optional[str] = None
    language: str
    views: int
    likes: int
    comments: int
    author: AuthorSchema
    tags: List[TagSchema]
