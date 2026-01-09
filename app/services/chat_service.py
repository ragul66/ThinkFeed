import google.generativeai as genai
from app.config import settings
from app.utils.redis_client import redis_client
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            if not settings.chat_api_key or settings.chat_api_key == "your_gemini_api_key_here":
                logger.error("Gemini Chat API key not configured")
                raise ValueError("Gemini Chat API key not configured")
            
            genai.configure(api_key=settings.chat_api_key)
            
            # System instruction for news-only responses
            self.system_instruction = """You are ThinkFeed AI, a specialized news assistant. Your role is to:

1. ONLY answer questions about news, current events, and world affairs
2. Provide accurate, unbiased information about recent news stories
3. Discuss news from various categories: politics, technology, business, sports, entertainment, health, science
4. Explain news context and background when asked
5. Compare different news perspectives when relevant

STRICT RULES:
- If asked about anything NOT related to news or current events, politely decline and redirect to news topics
- Do NOT provide personal advice, medical advice, legal advice, or financial advice
- Do NOT engage in conversations about personal matters, relationships, or non-news topics
- Always maintain a professional, journalistic tone
- If you don't have current information, acknowledge it and suggest checking recent news sources

Example responses for non-news questions:
- "I'm ThinkFeed AI, specialized in news and current events. I can't help with that, but I'd be happy to discuss recent news stories!"
- "That's outside my expertise as a news assistant. Would you like to know about today's top headlines instead?"

Stay focused on news and current events at all times."""

            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Chat Service initialized successfully with gemini-2.5-flash model")
        except Exception as e:
            logger.error(f"Failed to initialize Chat Service: {str(e)}")
            raise
    
    async def chat(self, user_id: int, message: str, conversation_history: list = None) -> dict:
        """
        Process a chat message and return AI response
        
        Args:
            user_id: User ID for tracking conversations
            message: User's message
            conversation_history: List of previous messages [{"role": "user/model", "parts": ["text"]}]
        
        Returns:
            dict with response and updated conversation history
        """
        try:
            # Validate message
            if not message or len(message.strip()) < 1:
                raise ValueError("Message cannot be empty")
            
            if len(message) > 2000:
                raise ValueError("Message is too long. Please keep it under 2000 characters.")
            
            # Start or continue chat session
            if conversation_history and len(conversation_history) > 0:
                chat = self.model.start_chat(history=conversation_history)
            else:
                # For first message, prepend system instruction
                chat = self.model.start_chat(history=[])
                message = f"{self.system_instruction}\n\nUser question: {message}"
            
            logger.info(f"Processing chat message for user {user_id}")
            
            # Send message and get response
            try:
                response = chat.send_message(message)
                
                if not response or not response.text:
                    raise ValueError("AI returned empty response")
                
                response_text = response.text.strip()
                
            except Exception as gemini_error:
                error_msg = str(gemini_error)
                logger.error(f"Gemini Chat API error: {error_msg}")
                
                # Check for specific error types
                if "429" in error_msg or "quota" in error_msg.lower():
                    raise ValueError("Chat service is temporarily unavailable due to high demand. Please try again in a few moments.")
                elif "404" in error_msg or "not found" in error_msg.lower():
                    raise ValueError("Chat service is currently unavailable. Please try again later.")
                elif "403" in error_msg or "permission" in error_msg.lower():
                    raise ValueError("Chat service access error. Please contact support.")
                else:
                    raise ValueError(f"Chat service error: {error_msg}")
            
            # Get updated conversation history
            updated_history = chat.history
            
            # Cache conversation for user (keep last 10 messages)
            cache_key = f"chat:history:{user_id}"
            history_to_cache = updated_history[-20:] if len(updated_history) > 20 else updated_history
            
            # Convert history to serializable format
            serializable_history = [
                {
                    "role": msg.role,
                    "parts": [part.text for part in msg.parts]
                }
                for msg in history_to_cache
            ]
            
            redis_client.set(cache_key, json.dumps(serializable_history), expire=3600)  # Cache for 1 hour
            
            logger.info(f"Chat response generated for user {user_id}")
            
            return {
                "response": response_text,
                "conversation_history": serializable_history,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process chat message: {str(e)}")
    
    def get_conversation_history(self, user_id: int) -> list:
        """Get cached conversation history for a user"""
        try:
            cache_key = f"chat:history:{user_id}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def clear_conversation_history(self, user_id: int) -> bool:
        """Clear conversation history for a user"""
        try:
            cache_key = f"chat:history:{user_id}"
            redis_client.delete(cache_key)
            logger.info(f"Cleared conversation history for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing conversation history: {str(e)}")
            return False

chat_service = ChatService()
