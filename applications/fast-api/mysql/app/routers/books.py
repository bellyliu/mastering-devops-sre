from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db, get_redis
from ..auth import get_current_active_user

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Create a new book (requires authentication)"""
    return crud.create_book(db=db, book=book, owner_id=current_user.id, redis_client=redis_client)


@router.get("/", response_model=List[schemas.BookResponse])
def read_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """Get all books with optional filtering (no authentication required)"""
    books = crud.get_books(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price
    )
    return books


@router.get("/count")
def get_books_count(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
    db: Session = Depends(get_db)
):
    """Get total count of books matching filters"""
    count = crud.get_books_count(db=db, category=category, search=search)
    return {"total": count}


@router.get("/my-books", response_model=List[schemas.BookResponse])
def read_my_books(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all books owned by the current user"""
    return crud.get_user_books(db=db, user_id=current_user.id)


@router.get("/{book_id}", response_model=schemas.BookResponse)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Get a specific book by ID (no authentication required)"""
    db_book = crud.get_book(db=db, book_id=book_id, redis_client=redis_client)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book: schemas.BookUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Update a book (only owner can update)"""
    db_book = crud.update_book(
        db=db,
        book_id=book_id,
        book=book,
        owner_id=current_user.id,
        redis_client=redis_client
    )
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found or you don't have permission to update it"
        )
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Delete a book (only owner can delete)"""
    success = crud.delete_book(
        db=db,
        book_id=book_id,
        owner_id=current_user.id,
        redis_client=redis_client
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Book not found or you don't have permission to delete it"
        )
    return None
