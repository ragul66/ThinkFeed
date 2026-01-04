from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.news import NewsListResponse, NewsArticleResponse, SavedArticleResponse
from app.services.news_service import news_service
from app.utils.security import get_current_user
from app.models.user import User
from app.middleware.rate_limit import limiter
from fastapi import Request

router = APIRouter()

@router.get("/headlines", response_model=dict)
@limiter.limit("30/minute")
async def get_headlines(
    request: Request,
    category: Optional[str] = Query(None, description="Category: business, entertainment, general, health, science, sports, technology"),
    country: str = Query("us", description="Country code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    try:
        data = await news_service.fetch_top_headlines(category, country, page, page_size)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=dict)
@limiter.limit("30/minute")
async def search_news(
    request: Request,
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    from_date: Optional[str] = Query(None, description="From date (YYYY-MM-DD)")
):
    try:
        data = await news_service.search_news(q, page, page_size, from_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save/{article_url:path}")
async def save_article(
    article_url: str,
    article_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate article data
        if not article_data.get("url"):
            raise HTTPException(status_code=400, detail="Article URL is required")
        if not article_data.get("title"):
            raise HTTPException(status_code=400, detail="Article title is required")
        
        article = news_service.save_article_to_db(db, article_data)
        saved = news_service.save_user_article(db, current_user.id, article.id)
        return {
            "message": "Article saved successfully",
            "saved_article_id": saved.id,
            "article_id": article.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save article: {str(e)}")

@router.get("/saved", response_model=List[SavedArticleResponse])
async def get_saved_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved_articles = news_service.get_user_saved_articles(db, current_user.id, skip, limit)
    return saved_articles

@router.delete("/saved/{article_id}")
async def remove_saved_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.news import SavedArticle
    saved = db.query(SavedArticle).filter(
        SavedArticle.user_id == current_user.id,
        SavedArticle.article_id == article_id
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved article not found")
    db.delete(saved)
    db.commit()
    return {"message": "Article removed from saved"}
