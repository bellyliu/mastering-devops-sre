from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, books

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Store API - MySQL",
    description="A comprehensive Book Store API built with FastAPI and MySQL",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Book Store API with MySQL",
        "database": "MySQL",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "MySQL"}


@app.get("/stats")
def get_stats(db = Depends(get_db)):
    """Get database statistics"""
    from sqlalchemy import func
    from .models import User, Book
    
    total_users = db.query(func.count(User.id)).scalar()
    total_books = db.query(func.count(Book.id)).scalar()
    
    return {
        "total_users": total_users,
        "total_books": total_books
    }


# Import for stats endpoint
from fastapi import Depends
from .database import get_db
