from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import RegEx, And, Or
from . import models, schemas
from .auth import get_password_hash
import json


# User CRUD operations
async def get_user(user_id: str):
    """Get a user by ID"""
    return await models.User.get(user_id)


async def get_user_by_username(username: str):
    """Get a user by username"""
    return await models.User.find_one(models.User.username == username)


async def get_user_by_email(email: str):
    """Get a user by email"""
    return await models.User.find_one(models.User.email == email)


async def create_user(user: schemas.UserCreate):
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    await db_user.insert()
    return db_user


async def update_user(user_id: str, user: schemas.UserUpdate):
    """Update a user"""
    db_user = await get_user(user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db_user.save()
    return db_user


async def delete_user(user_id: str):
    """Delete a user and all their books"""
    db_user = await get_user(user_id)
    if db_user:
        # Delete all books owned by this user
        await models.Book.find(models.Book.owner_id == user_id).delete()
        await db_user.delete()
        return True
    return False


# Book CRUD operations
async def get_book(book_id: str, redis_client=None):
    """Get a book by ID with Redis caching"""
    cache_key = f"mongodb:book:{book_id}"
    
    # Try to get from cache
    if redis_client:
        cached_book = redis_client.get(cache_key)
        if cached_book:
            return json.loads(cached_book)
    
    # Get from database
    db_book = await models.Book.get(book_id)
    
    # Cache the result
    if redis_client and db_book:
        book_dict = {
            "_id": str(db_book.id),
            "title": db_book.title,
            "author": db_book.author,
            "isbn": db_book.isbn,
            "description": db_book.description,
            "price": db_book.price,
            "quantity": db_book.quantity,
            "category": db_book.category,
            "published_year": db_book.published_year,
            "owner_id": db_book.owner_id,
            "created_at": db_book.created_at.isoformat() if db_book.created_at else None,
            "updated_at": db_book.updated_at.isoformat() if db_book.updated_at else None,
        }
        redis_client.setex(cache_key, 3600, json.dumps(book_dict))
    
    return db_book


async def get_books(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: int = -1,  # -1 for descending, 1 for ascending
):
    """Get all books with optional filtering, sorting and pagination"""
    query_conditions = []
    
    if category:
        query_conditions.append(models.Book.category == category)
    
    if search:
        # MongoDB regex search (case-insensitive)
        query_conditions.append(
            Or(
                RegEx(models.Book.title, search, "i"),
                RegEx(models.Book.author, search, "i")
            )
        )
    
    if min_price is not None:
        query_conditions.append(models.Book.price >= min_price)
    
    if max_price is not None:
        query_conditions.append(models.Book.price <= max_price)
    
    # Build query
    if query_conditions:
        query = models.Book.find(*query_conditions)
    else:
        query = models.Book.find_all()
    
    # Apply sorting
    if sort_order == 1:
        query = query.sort(f"+{sort_by}")
    else:
        query = query.sort(f"-{sort_by}")
    
    # Apply pagination
    books = await query.skip(skip).limit(limit).to_list()
    
    return books


async def get_books_count(
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get total count of books with filters"""
    query_conditions = []
    
    if category:
        query_conditions.append(models.Book.category == category)
    
    if search:
        query_conditions.append(
            Or(
                RegEx(models.Book.title, search, "i"),
                RegEx(models.Book.author, search, "i")
            )
        )
    
    if query_conditions:
        count = await models.Book.find(*query_conditions).count()
    else:
        count = await models.Book.find_all().count()
    
    return count


async def create_book(book: schemas.BookCreate, owner_id: str, redis_client=None):
    """Create a new book"""
    db_book = models.Book(
        **book.model_dump(),
        owner_id=owner_id,
        created_at=datetime.utcnow()
    )
    await db_book.insert()
    
    # Invalidate cache
    if redis_client:
        # Delete all cached book lists
        for key in redis_client.scan_iter("mongodb:books:*"):
            redis_client.delete(key)
    
    return db_book


async def update_book(
    book_id: str,
    book: schemas.BookUpdate,
    owner_id: str,
    redis_client=None
):
    """Update a book"""
    db_book = await models.Book.find_one(
        And(
            models.Book.id == PydanticObjectId(book_id),
            models.Book.owner_id == owner_id
        )
    )
    
    if not db_book:
        return None
    
    update_data = book.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    await db_book.save()
    
    # Invalidate cache
    if redis_client:
        redis_client.delete(f"mongodb:book:{book_id}")
        for key in redis_client.scan_iter("mongodb:books:*"):
            redis_client.delete(key)
    
    return db_book


async def delete_book(book_id: str, owner_id: str, redis_client=None):
    """Delete a book"""
    db_book = await models.Book.find_one(
        And(
            models.Book.id == PydanticObjectId(book_id),
            models.Book.owner_id == owner_id
        )
    )
    
    if db_book:
        await db_book.delete()
        
        # Invalidate cache
        if redis_client:
            redis_client.delete(f"mongodb:book:{book_id}")
            for key in redis_client.scan_iter("mongodb:books:*"):
                redis_client.delete(key)
        
        return True
    return False


async def get_user_books(user_id: str):
    """Get all books owned by a user"""
    return await models.Book.find(models.Book.owner_id == user_id).to_list()


async def get_books_by_category():
    """Get book count grouped by category using aggregation"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = await models.Book.aggregate(pipeline).to_list()
    return result


async def get_price_statistics():
    """Get price statistics using aggregation"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_price": {"$avg": "$price"},
                "min_price": {"$min": "$price"},
                "max_price": {"$max": "$price"},
                "total_books": {"$sum": 1}
            }
        }
    ]
    result = await models.Book.aggregate(pipeline).to_list()
    return result[0] if result else {}
