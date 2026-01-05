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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all books with optional filtering (no authentication required)"""
    books = crud.get_books(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        search=search
    )
    return books


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
