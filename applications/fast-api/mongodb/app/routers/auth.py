from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import crud, schemas
from ..auth import authenticate_user, create_access_token, get_current_active_user
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserCreate):
    """Register a new user"""
    # Check if username exists
    db_user = await crud.get_user_by_username(username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    db_user = await crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = await crud.create_user(user=user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
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
    current_user = Depends(get_current_active_user)
):
    """Update current user information"""
    updated_user = await crud.update_user(str(current_user.id), user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(current_user = Depends(get_current_active_user)):
    """Delete current user account"""
    success = await crud.delete_user(str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
