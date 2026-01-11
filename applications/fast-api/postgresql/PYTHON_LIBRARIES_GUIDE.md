# Python Libraries Guide - FastAPI Book Store

A comprehensive guide to the Python libraries used in this FastAPI Book Store application with direct code examples from the project.

---

## Table of Contents
1. [FastAPI](#1-fastapi)
2. [Pydantic & Pydantic Settings](#2-pydantic--pydantic-settings)
3. [SQLAlchemy](#3-sqlalchemy)
4. [Passlib & Bcrypt](#4-passlib--bcrypt)
5. [Python-JOSE](#5-python-jose)
6. [Redis](#6-redis)
7. [Uvicorn](#7-uvicorn)
8. [Supporting Libraries](#8-supporting-libraries)

---

## 1. FastAPI

**Purpose:** Modern, fast web framework for building APIs with Python 3.8+ based on standard Python type hints.

**Version:** `fastapi==0.109.0`

### Key Features Used

#### 1.1 Application Instance
```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Book Store API - PostgreSQL",
    description="A comprehensive Book Store API built with FastAPI and PostgreSQL",
    version="1.0.0"
)
```

#### 1.2 Dependency Injection
```python
# app/routers/books.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user

@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,
    current_user = Depends(get_current_active_user),  # Auth dependency
    db: Session = Depends(get_db),                    # Database dependency
    redis_client = Depends(get_redis)                 # Redis dependency
):
    return crud.create_book(db=db, book=book, owner_id=current_user.id)
```

**What it does:** `Depends()` tells FastAPI to call the function and inject its return value as a parameter.

#### 1.3 Path Parameters & Query Parameters
```python
# app/routers/books.py
from fastapi import Query

@router.get("/{book_id}")  # Path parameter
def read_book(
    book_id: int,  # Automatically converted to int
    db: Session = Depends(get_db)
):
    db_book = crud.get_book(db=db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/")
def read_books(
    skip: int = Query(0, ge=0),              # Query param with default and validation
    limit: int = Query(100, ge=1, le=100),   # Min and max constraints
    category: Optional[str] = None,           # Optional query param
    search: Optional[str] = None
):
    return crud.get_books(db=db, skip=skip, limit=limit, category=category, search=search)
```

#### 1.4 HTTP Status Codes
```python
# app/routers/auth.py
from fastapi import status

@router.post("/register", response_model=schemas.UserResponse, 
             status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return crud.create_user(db=db, user=user)
```

#### 1.5 APIRouter for Route Organization
```python
# app/routers/books.py
from fastapi import APIRouter

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/")      # Becomes /books/
@router.get("/")       # Becomes /books/
@router.get("/{id}")   # Becomes /books/{id}

# app/main.py
app.include_router(books.router)
```

#### 1.6 CORS Middleware
```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 2. Pydantic & Pydantic Settings

**Purpose:** Data validation and settings management using Python type annotations.

**Version:** `pydantic==2.5.3`, `pydantic-settings==2.1.0`

### Key Features Used

#### 2.1 Data Validation with BaseModel
```python
# app/schemas.py
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)  # Required, 3-50 chars
    email: EmailStr                                           # Email validation
    full_name: Optional[str] = None                          # Optional field

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)  # Min 6, max 72 chars
```

**What it does:**
- Validates data types automatically
- `Field(...)` means required field
- `min_length`, `max_length` validate string length
- `EmailStr` validates email format
- Raises validation errors if data doesn't match

#### 2.2 Field Constraints
```python
# app/schemas.py
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    price: float = Field(..., gt=0)                    # Greater than 0
    quantity: int = Field(default=0, ge=0)             # Greater than or equal to 0
    published_year: Optional[int] = Field(None, ge=1000, le=9999)
```

**Validation Examples:**
- `gt=0` → Must be greater than 0
- `ge=0` → Must be greater than or equal to 0
- `le=9999` → Must be less than or equal to 9999

#### 2.3 Model Configuration
```python
# app/schemas.py
class UserResponse(UserBase):
    id: int
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows creation from ORM models
```

**What it does:** Enables creating Pydantic models from SQLAlchemy ORM objects:
```python
db_user = User(username="john", email="john@example.com")  # SQLAlchemy model
user_response = UserResponse.from_orm(db_user)             # Pydantic model
```

#### 2.4 Settings Management
```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"  # Load from .env file

@lru_cache()  # Cache the settings instance
def get_settings():
    return Settings()

# Usage
settings = get_settings()
print(settings.DATABASE_URL)
```

**What it does:**
- Reads environment variables automatically
- Loads from `.env` file
- Type validation for config values
- `@lru_cache()` ensures only one instance is created

#### 2.5 Partial Updates
```python
# app/crud.py
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    
    # Only include fields that were actually provided
    update_data = user.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    return db_user
```

**What it does:** `model_dump(exclude_unset=True)` returns only fields that were explicitly set, ignoring defaults.

---

## 3. SQLAlchemy

**Purpose:** SQL toolkit and Object-Relational Mapping (ORM) for database operations.

**Version:** `sqlalchemy==2.0.25`

### Key Features Used

#### 3.1 Database Engine & Session
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = get_settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What it does:**
- `create_engine()` creates connection to database
- `SessionLocal()` creates new database session
- `yield` ensures session is closed after request

#### 3.2 Declarative Base
```python
# app/database.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# app/models.py
from app.database import Base

class User(Base):
    __tablename__ = "users"
    # ... columns
```

**What it does:** Base class for all ORM models.

#### 3.3 Column Definitions
```python
# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Column Options:**
- `primary_key=True` → Primary key
- `index=True` → Create index for faster lookups
- `unique=True` → Enforce uniqueness
- `nullable=False` → NOT NULL constraint
- `default=1` → Default value
- `server_default=func.now()` → Database-level default (CURRENT_TIMESTAMP)
- `onupdate=func.now()` → Auto-update on changes

#### 3.4 Relationships
```python
# app/models.py
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    
    # One-to-Many: One user can have many books
    books = relationship("Book", back_populates="owner")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Many-to-One: Many books belong to one user
    owner = relationship("User", back_populates="books")
```

**What it does:**
- Defines relationship between tables
- `ForeignKey()` creates foreign key constraint
- `relationship()` enables navigation: `book.owner.username`

#### 3.5 Querying
```python
# app/crud.py
from sqlalchemy import or_

# Simple query
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Query with OR condition
def get_books(db: Session, search: Optional[str] = None):
    query = db.query(models.Book)
    
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),  # Case-insensitive LIKE
                models.Book.author.ilike(f"%{search}%")
            )
        )
    
    return query.all()
```

**Query Methods:**
- `.filter()` → WHERE clause
- `.first()` → Get first result or None
- `.all()` → Get all results as list
- `.offset()` → Skip N records
- `.limit()` → Return max N records
- `ilike()` → Case-insensitive LIKE

#### 3.6 Create, Update, Delete
```python
# app/crud.py

# CREATE
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get auto-generated fields
    return db_user

# UPDATE
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    
    for field, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
```

---

## 4. Bcrypt (Direct)

**Purpose:** Secure password hashing using the bcrypt algorithm.

**Version:** `bcrypt==5.0.0`

### Why Direct Bcrypt Instead of Passlib?

This project uses bcrypt **directly** rather than through passlib because:
- **Compatibility**: passlib 1.7.4 is incompatible with bcrypt 5.0.0+
- **Simplicity**: Direct bcrypt API is cleaner and more straightforward
- **Modern**: Bcrypt 5.0.0 has improved security and performance
- **No Bloat**: Removes unnecessary abstraction layer

### Key Features Used

#### 4.1 SHA256 Pre-Hashing Strategy

Bcrypt has a **72-byte limit** on passwords. To handle this while allowing any password length, we use SHA256 pre-hashing:

```python
# app/auth.py
import hashlib
import bcrypt

def _prepare_password(password: str) -> bytes:
    """
    Pre-hash password with SHA256 to handle bcrypt's 72-byte limit.
    
    This is a recommended security practice that:
    - Allows passwords of any length
    - Produces a fixed-length input for bcrypt (64 hex characters = 64 bytes)
    - Maintains security through the combination of SHA256 + bcrypt
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')
```

**Why this is secure:**
- SHA256 is one-way and collision-resistant
- The combination of SHA256 + bcrypt provides double hashing
- Output is always 64 bytes (within bcrypt's limit)
- Users can have passwords of any length

#### 4.2 Password Hashing
```python
# app/auth.py
def get_password_hash(password: str) -> str:
    """
    Hash a password using SHA256 + bcrypt.
    
    Pre-hashing with SHA256 ensures we never exceed bcrypt's 72-byte limit
    while allowing users to have passwords of any length.
    """
    prepared_password = _prepare_password(password)
    # Generate salt and hash with bcrypt directly
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prepared_password, salt)
    return hashed.decode('utf-8')

# Usage in registration
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password  # Store hashed, not plain text
    )
```

**Important:**
- **Never** store plain text passwords
- SHA256 pre-hashing handles bcrypt's 72-byte limit
- Each hash is unique (bcrypt includes random salt)
- Salt is automatically generated by `bcrypt.gensalt()`

#### 4.3 Password Verification
```python
# app/auth.py
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt directly"""
    prepared_password = _prepare_password(plain_password)
    return bcrypt.checkpw(prepared_password, hashed_password.encode('utf-8'))

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
```

**What it does:**
- Pre-hashes the password with SHA256 (same as during registration)
- Compares with stored hash using `bcrypt.checkpw()`
- Returns True if match, False otherwise
- Timing-safe comparison (prevents timing attacks)

#### 4.4 Migration Notes

**⚠️ Important for Upgrading:**

If you're upgrading from an older version that used passlib:

1. **Existing passwords won't work** - The hashing method changed
2. **Options:**
   - Force all users to reset passwords (recommended for production)
   - Keep old auth.py for existing users, use new one for new registrations
   - Cannot convert old hashes to new format (one-way hashing)

3. **For fresh installations:**
   - No migration needed
   - All new users will use SHA256+bcrypt automatically

---

## 5. Python-JOSE

**Purpose:** JavaScript Object Signing and Encryption for JWT tokens.

**Version:** `python-jose[cryptography]==3.3.0`

### Key Features Used

#### 5.1 Creating JWT Tokens
```python
# app/auth.py
from datetime import datetime, timedelta
from jose import jwt
from app.config import get_settings

settings = get_settings()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# Usage in login
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

**JWT Payload:**
- `sub` → Subject (username)
- `exp` → Expiration timestamp

#### 5.2 Verifying JWT Tokens
```python
# app/auth.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

**What it does:**
- `OAuth2PasswordBearer` extracts token from `Authorization: Bearer <token>` header
- `jwt.decode()` verifies signature and expiration
- Returns user object if valid
- Raises 401 error if invalid

#### 5.3 Using Authentication
```python
# app/routers/books.py
@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,
    current_user = Depends(get_current_active_user),  # Requires authentication
    db: Session = Depends(get_db)
):
    # current_user is automatically populated from JWT token
    return crud.create_book(db=db, book=book, owner_id=current_user.id)
```

---

## 6. Redis

**Purpose:** In-memory data store for caching.

**Version:** `redis==7.1.0`

### Key Features Used

#### 6.1 Redis Connection
```python
# app/database.py
import redis
from app.config import get_settings

settings = get_settings()

# Create Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    """Dependency for getting Redis client"""
    return redis_client
```

**What it does:**
- `decode_responses=True` automatically decodes bytes to strings

#### 6.2 Caching Pattern
```python
# app/crud.py
import json

def get_book(db: Session, book_id: int, redis_client=None):
    """Get a book by ID with Redis caching"""
    cache_key = f"book:{book_id}"
    
    # Try to get from cache
    if redis_client:
        cached_book = redis_client.get(cache_key)
        if cached_book:
            return json.loads(cached_book)
    
    # Get from database if not in cache
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # Store in cache for future requests
    if redis_client and db_book:
        book_dict = {
            "id": db_book.id,
            "title": db_book.title,
            "price": db_book.price,
            # ... other fields
        }
        redis_client.setex(cache_key, 3600, json.dumps(book_dict))  # 1 hour TTL
    
    return db_book
```

**Redis Operations:**
- `get(key)` → Retrieve value
- `setex(key, ttl, value)` → Set with expiration (TTL in seconds)
- `delete(key)` → Remove key

#### 6.3 Cache Invalidation
```python
# app/crud.py
def update_book(db: Session, book_id: int, book: schemas.BookUpdate, redis_client=None):
    """Update a book"""
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # Update fields
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    
    # Invalidate cache after update
    if redis_client:
        redis_client.delete(f"book:{book_id}")
    
    return db_book
```

**Why invalidate?** Ensures cache doesn't serve stale data after updates.

---

## 7. Uvicorn

**Purpose:** ASGI server for running FastAPI applications.

**Version:** `uvicorn[standard]==0.27.0`

### Usage

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Parameters:**
- `app.main:app` → Module path to FastAPI instance
- `--reload` → Auto-restart on code changes
- `--host 0.0.0.0` → Listen on all interfaces
- `--port 8000` → Port number
- `--workers 4` → Number of worker processes (production)

---

## 8. Supporting Libraries

### 8.1 python-multipart
**Purpose:** Parse `multipart/form-data` (file uploads, form data).

**Usage:**
```python
# app/routers/auth.py
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username and form_data.password are automatically parsed
    user = authenticate_user(db, form_data.username, form_data.password)
```

### 8.2 python-dotenv
**Purpose:** Load environment variables from `.env` file.

**Usage:**
```python
# Automatically loaded by pydantic-settings
class Settings(BaseSettings):
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
```

### 8.3 email-validator
**Purpose:** Validate email addresses.

**Usage:**
```python
# app/schemas.py
from pydantic import EmailStr

class UserBase(BaseModel):
    email: EmailStr  # Automatically validates email format
```

### 8.4 psycopg2-binary
**Purpose:** PostgreSQL adapter for Python.

**Usage:** Used internally by SQLAlchemy for PostgreSQL connections.

---

## Complete Request Flow Example

Let's trace a complete request to create a book:

```python
# 1. Client sends POST request to /books/
# Headers: Authorization: Bearer eyJhbGc...
# Body: {"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "price": 39.99}

# 2. FastAPI receives request
@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,                      # 3. Pydantic validates JSON body
    current_user = Depends(get_current_active_user),  # 4. JWT token verified
    db: Session = Depends(get_db),                 # 5. Database session created
    redis_client = Depends(get_redis)              # 6. Redis client injected
):
    # 7. CRUD operation
    return crud.create_book(db=db, book=book, owner_id=current_user.id, redis_client=redis_client)

# 8. crud.create_book()
def create_book(db: Session, book: schemas.BookCreate, owner_id: int, redis_client=None):
    # 9. SQLAlchemy creates model instance
    db_book = models.Book(**book.model_dump(), owner_id=owner_id)
    
    # 10. Add to session and commit to database
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # 11. Invalidate cache
    if redis_client:
        redis_client.delete("books:all")
    
    # 12. Return created book
    return db_book

# 13. FastAPI serializes response using BookResponse schema
# 14. Returns JSON response with 201 Created status
```

---

## Common Patterns Summary

### Pattern 1: Dependency Injection
```python
def endpoint(
    param: Type = Depends(dependency_function),
    db: Session = Depends(get_db)
):
    # dependency_function() is called automatically
    # Its return value is passed as param
```

### Pattern 2: Request Validation
```python
class CreateSchema(BaseModel):
    field: str = Field(..., min_length=3, max_length=50)

@router.post("/")
def create(data: CreateSchema):
    # If validation fails, automatic 422 error response
    # If valid, data.field is guaranteed to be 3-50 chars
```

### Pattern 3: Error Handling
```python
from fastapi import HTTPException, status

@router.get("/{id}")
def get_item(id: int):
    item = crud.get_item(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

### Pattern 4: Cache-Aside
```python
def get_item(id: int, redis_client):
    # Try cache first
    cached = redis_client.get(f"item:{id}")
    if cached:
        return json.loads(cached)
    
    # Get from database
    item = db.query(Item).get(id)
    
    # Cache for next time
    redis_client.setex(f"item:{id}", 3600, json.dumps(item))
    return item
```

### Pattern 5: Password Security
```python
# Registration
hashed = get_password_hash(plain_password)  # Hash before storing
user.hashed_password = hashed

# Login
if verify_password(plain_password, user.hashed_password):  # Verify on login
    # Create JWT token
    token = create_access_token({"sub": user.username})
```

---

## Library Versions Compatibility

```
Python: 3.11+
fastapi==0.109.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
passlib[bcrypt]==1.7.4
bcrypt==4.0.1          # Pinned for passlib compatibility
python-jose[cryptography]==3.3.0
redis==7.1.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-dotenv==1.0.0
email-validator==2.3.0
```

**Note:** `bcrypt==4.0.1` is specifically pinned because newer versions (4.1.0+) break compatibility with `passlib==1.7.4`.

---

This guide covers all the major Python libraries used in the Book Store API with real code examples from the project.
