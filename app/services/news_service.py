import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models.news import NewsArticle, SavedArticle
from app.utils.redis_client import redis_client

class NewsService:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = settings.NEWS_API_BASE_URL
    
    async def fetch_top_headlines(self, category: Optional[str] = None, country: str = "us", page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        cache_key = f"news:headlines:{category or 'all'}:{country}:{page}:{page_size}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached
        
        params = {
            "apiKey": self.api_key,
            "country": country,
            "page": page,
            "pageSize": page_size
        }
        if category:
            params["category"] = category
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            data = response.json()
        
        redis_client.set(cache_key, data, expire=600)  # Cache for 10 minutes
        return data
    
    async def search_news(self, query: str, page: int = 1, page_size: int = 20, from_date: Optional[str] = None) -> Dict[str, Any]:
        cache_key = f"news:search:{query}:{page}:{page_size}:{from_date or 'all'}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached
        
        params = {
            "apiKey": self.api_key,
            "q": query,
            "page": page,
            "pageSize": page_size,
            "sortBy": "publishedAt"
        }
        if from_date:
            params["from"] = from_date
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            data = response.json()
        
        redis_client.set(cache_key, data, expire=600)
        return data
    
    def save_article_to_db(self, db: Session, article_data: Dict[str, Any]) -> NewsArticle:
        existing = db.query(NewsArticle).filter(NewsArticle.url == article_data["url"]).first()
        if existing:
            return existing
        
        article = NewsArticle(
            source_id=article_data.get("source", {}).get("id"),
            source_name=article_data.get("source", {}).get("name"),
            author=article_data.get("author"),
            title=article_data["title"],
            description=article_data.get("description"),
            url=article_data["url"],
            url_to_image=article_data.get("urlToImage"),
            published_at=datetime.fromisoformat(article_data["publishedAt"].replace("Z", "+00:00")) if article_data.get("publishedAt") else None,
            content=article_data.get("content"),
            category=article_data.get("category")
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        return article
    
    def save_user_article(self, db: Session, user_id: int, article_id: int) -> SavedArticle:
        existing = db.query(SavedArticle).filter(
            SavedArticle.user_id == user_id,
            SavedArticle.article_id == article_id
        ).first()
        if existing:
            return existing
        
        saved = SavedArticle(user_id=user_id, article_id=article_id)
        db.add(saved)
        db.commit()
        db.refresh(saved)
        return saved
    
    def get_user_saved_articles(self, db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[SavedArticle]:
        return db.query(SavedArticle).filter(SavedArticle.user_id == user_id).offset(skip).limit(limit).all()

news_service = NewsService()
