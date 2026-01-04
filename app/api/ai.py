from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.news import SummaryRequest, SummaryResponse
from app.services.ai_service import ai_service
from app.services.news_service import news_service
from app.utils.security import get_current_user
from app.models.user import User
from app.models.news import NewsArticle
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_article(
    request: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Summarize request for URL: {request.article_url}")
        article = db.query(NewsArticle).filter(NewsArticle.url == request.article_url).first()
        
        if not article:
            logger.warning(f"Article not found for URL: {request.article_url}")
            raise HTTPException(status_code=404, detail="Article not found in database. Please save it first.")
        
        logger.info(f"Found article ID: {article.id}, has content: {bool(article.content)}, content length: {len(article.content) if article.content else 0}")
        
        if not article.content:
            logger.warning(f"Article {article.id} has no content")
            raise HTTPException(status_code=400, detail="Article content not available for summarization")
        
        if len(article.content.strip()) < 50:
            logger.warning(f"Article {article.id} content too short: {len(article.content)} chars")
            raise HTTPException(status_code=400, detail="Article content is too short for summarization")
        
        summary = await ai_service.summarize_article(db, article.id, article.content)
        logger.info(f"Successfully generated summary for article {article.id}")
        return {
            "summary": summary,
            "article_id": article.id
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in summarize_article: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.post("/summarize/{article_id}", response_model=SummaryResponse)
async def summarize_article_by_id(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        
        if not article:
            logger.warning(f"Article not found for ID: {article_id}")
            raise HTTPException(status_code=404, detail="Article not found")
        
        if not article.content:
            logger.warning(f"Article {article_id} has no content")
            raise HTTPException(status_code=400, detail="Article content not available for summarization")
        
        summary = await ai_service.summarize_article(db, article.id, article.content)
        return {
            "summary": summary,
            "article_id": article.id
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in summarize_article_by_id: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
