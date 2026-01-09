from fastapi import APIRouter
from app.api import auth, news, ai, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
