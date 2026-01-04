from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings

class AuthService:
    def register_user(self, db: Session, user_data: UserCreate) -> User:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_google_user=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate_user(self, db: Session, login_data: UserLogin) -> User:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated. Please contact support."
            )
        
        # Check if user registered with Google
        if user.is_google_user and not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses Google Sign-In. Please use 'Continue with Google' to login."
            )
        
        # Verify password
        if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        return user
    
    def create_token(self, user_id: int) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        return access_token
    
    async def verify_google_token(self, token: str) -> dict:
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return idinfo
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    
    def get_or_create_google_user(self, db: Session, google_data: dict) -> User:
        user = db.query(User).filter(User.google_id == google_data["sub"]).first()
        if user:
            return user
        
        user = db.query(User).filter(User.email == google_data["email"]).first()
        if user:
            user.google_id = google_data["sub"]
            user.is_google_user = True
            db.commit()
            db.refresh(user)
            return user
        
        username = google_data["email"].split("@")[0]
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            email=google_data["email"],
            username=username,
            full_name=google_data.get("name"),
            is_google_user=True,
            google_id=google_data["sub"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

auth_service = AuthService()
