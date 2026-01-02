from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NewsArticleResponse(BaseModel):
    id: int
    source_name: Optional[str]
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    url_to_image: Optional[str]
    published_at: Optional[datetime]
    content: Optional[str]
    category: Optional[str]
    
    class Config:
        from_attributes = True

class NewsListResponse(BaseModel):
    articles: List[NewsArticleResponse]
    total: int
    page: int
    page_size: int

class SavedArticleResponse(BaseModel):
    id: int
    article: NewsArticleResponse
    saved_at: datetime
    
    class Config:
        from_attributes = True

class SummaryRequest(BaseModel):
    article_url: str

class SummaryResponse(BaseModel):
    summary: str
    article_id: int
