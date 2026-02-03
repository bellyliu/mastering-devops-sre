from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.config import get_settings
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    with tracer.start_as_current_span("auth.register") as span:
        # Add span attributes for context
        span.set_attribute("user.username", user.username)
        span.set_attribute("user.email", user.email)
        
        # Check if username exists
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user:
            span.set_attribute("error", True)
            span.set_attribute("error.type", "username_already_exists")
            span.add_event(
                "registration_failed"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            span.set_attribute("error", True)
            span.set_attribute("error.type", "email_already_exists")
            span.add_event(
                "registration_failed"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        new_user = crud.create_user(db=db, user=user)
        span.add_event(
            "registration_successful",
            attributes={
                "user.id": new_user.id,
                "user.username": new_user.username
            }
        )
        return new_user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    with tracer.start_as_current_span("auth.login") as span:
        span.set_attribute("user.username", form_data.username)
        
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            span.set_attribute("error", True)
            span.set_attribute("error.type", "authentication_failed")
            span.add_event(
                "login_failed",
                attributes={
                    "reason": "invalid_credentials",
                    "username": form_data.username
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
