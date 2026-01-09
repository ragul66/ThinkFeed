from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.chat_service import chat_service
from app.utils.security import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to ThinkFeed AI Chat
    """
    try:
        # Get conversation history if continuing conversation
        conversation_history = None
        if request.conversation_history:
            conversation_history = request.conversation_history
        else:
            # Try to get from cache
            conversation_history = chat_service.get_conversation_history(current_user.id)
        
        # Process chat message
        result = await chat_service.chat(
            user_id=current_user.id,
            message=request.message,
            conversation_history=conversation_history
        )
        
        return {
            "response": result["response"],
            "conversation_history": result["conversation_history"],
            "timestamp": result["timestamp"]
        }
    except ValueError as e:
        logger.error(f"Validation error in chat: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for current user
    """
    try:
        history = chat_service.get_conversation_history(current_user.id)
        return {
            "conversation_history": history,
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    Clear conversation history for current user
    """
    try:
        success = chat_service.clear_conversation_history(current_user.id)
        if success:
            return {"message": "Chat history cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear chat history")
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")
