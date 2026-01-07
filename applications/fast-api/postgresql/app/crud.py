from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app import models, schemas
from app.auth import get_password_hash
import json


# User CRUD operations
def get_user(db: Session, user_id: int):
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """Get a user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    """Delete a user"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Book CRUD operations
def get_book(db: Session, book_id: int, redis_client=None):
    """Get a book by ID with Redis caching"""
    cache_key = f"book:{book_id}"
    
    # Try to get from cache
    if redis_client:
        cached_book = redis_client.get(cache_key)
        if cached_book:
            return json.loads(cached_book)
    
    # Get from database
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # Cache the result
    if redis_client and db_book:
        book_dict = {
            "id": db_book.id,
            "title": db_book.title,
            "author": db_book.author,
            "isbn": db_book.isbn,
            "description": db_book.description,
            "price": db_book.price,
            "quantity": db_book.quantity,
            "category": db_book.category,
            "published_year": db_book.published_year,
            "owner_id": db_book.owner_id
        }
        redis_client.setex(cache_key, 3600, json.dumps(book_dict))  # Cache for 1 hour
    
    return db_book


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all books with optional filtering"""
    query = db.query(models.Book)
    
    if category:
        query = query.filter(models.Book.category == category)
    
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()


def create_book(db: Session, book: schemas.BookCreate, owner_id: int, redis_client=None):
    """Create a new book"""
    db_book = models.Book(**book.model_dump(), owner_id=owner_id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Invalidate cache
    if redis_client:
        redis_client.delete("books:all")
    
    return db_book


def update_book(
    db: Session,
    book_id: int,
    book: schemas.BookUpdate,
    owner_id: int,
    redis_client=None
):
    """Update a book"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.owner_id == owner_id
    ).first()
    
    if not db_book:
        return None
    
    update_data = book.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    
    # Invalidate cache
    if redis_client:
        redis_client.delete(f"book:{book_id}")
    
    return db_book


def delete_book(db: Session, book_id: int, owner_id: int, redis_client=None):
    """Delete a book"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.owner_id == owner_id
    ).first()
    
    if db_book:
        db.delete(db_book)
        db.commit()
        
        # Invalidate cache
        if redis_client:
            redis_client.delete(f"book:{book_id}")
            redis_client.delete("books:all")
        
        return True
    return False
