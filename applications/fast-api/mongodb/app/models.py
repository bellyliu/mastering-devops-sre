from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId


class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "email",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        }


class Book(Document):
    title: Indexed(str)
    author: Indexed(str)
    isbn: Indexed(str, unique=True)
    description: Optional[str] = None
    price: float
    quantity: int = 0
    category: Optional[Indexed(str)] = None
    published_year: Optional[int] = None
    owner_id: str  # Reference to User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "books"
        indexes = [
            "title",
            "author",
            "isbn",
            "category",
            "owner_id",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "isbn": "9780132350884",
                "description": "A Handbook of Agile Software Craftsmanship",
                "price": 39.99,
                "quantity": 10,
                "category": "Programming",
                "published_year": 2008
            }
        }
