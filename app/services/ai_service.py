import google.generativeai as genai
from sqlalchemy.orm import Session
from app.config import settings
from app.models.news import ArticleSummary, NewsArticle
from app.utils.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        try:
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
                logger.error("Gemini API key not configured")
                raise ValueError("Gemini API key not configured")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("AI Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Service: {str(e)}")
            raise
    
    async def summarize_article(self, db: Session, article_id: int, content: str) -> str:
        try:
            # Check cache first
            cache_key = f"summary:article:{article_id}"
            cached = redis_client.get(cache_key)
            if cached:
                logger.info(f"Returning cached summary for article {article_id}")
                return cached
            
            # Check database for existing summary
            existing_summary = db.query(ArticleSummary).filter(ArticleSummary.article_id == article_id).first()
            if existing_summary:
                redis_client.set(cache_key, existing_summary.summary, expire=86400)
                logger.info(f"Returning existing summary for article {article_id}")
                return existing_summary.summary
            
            # Validate content
            if not content or len(content.strip()) < 50:
                raise ValueError("Article content is too short or empty for summarization")
            
            # Prepare prompt
            prompt = f"""Please provide a concise summary of the following news article in 3-4 sentences. 
            Focus on the key points and main takeaways:

            {content[:5000]}
            
            Summary:"""
            
            logger.info(f"Generating new summary for article {article_id}")
            
            # Generate summary with error handling
            try:
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    raise ValueError("Gemini API returned empty response")
                
                summary = response.text.strip()
                
                if len(summary) < 20:
                    raise ValueError("Generated summary is too short")
                
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
                raise ValueError(f"AI service error: {str(gemini_error)}")
            
            # Save to database
            article_summary = ArticleSummary(article_id=article_id, summary=summary)
            db.add(article_summary)
            db.commit()
            
            # Cache the result
            redis_client.set(cache_key, summary, expire=86400)
            logger.info(f"Successfully generated and cached summary for article {article_id}")
            return summary
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error summarizing article {article_id}: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to generate summary: {str(e)}")

ai_service = AIService()
