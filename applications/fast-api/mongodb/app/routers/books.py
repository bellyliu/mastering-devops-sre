from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from .. import crud, schemas
from ..database import get_redis
from ..auth import get_current_active_user

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: schemas.BookCreate,
    current_user = Depends(get_current_active_user),
    redis_client = Depends(get_redis)
):
    """Create a new book (requires authentication)"""
    new_book = await crud.create_book(
        book=book,
        owner_id=str(current_user.id),
        redis_client=redis_client
    )
    return new_book


@router.get("/", response_model=List[schemas.BookResponse])
async def read_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: int = Query(-1, description="Sort order: 1 for ascending, -1 for descending"),
):
    """Get all books with optional filtering and sorting (no authentication required)"""
    books = await crud.get_books(
        skip=skip,
        limit=limit,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return books


@router.get("/paginated", response_model=schemas.PaginatedBooksResponse)
async def read_books_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
):
    """Get paginated books with total count"""
    skip = (page - 1) * page_size
    
    books = await crud.get_books(
        skip=skip,
        limit=page_size,
        category=category,
        search=search
    )
    
    total = await crud.get_books_count(category=category, search=search)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "books": books
    }


@router.get("/count")
async def get_books_count(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and author"),
):
    """Get total count of books matching filters"""
    count = await crud.get_books_count(category=category, search=search)
    return {"total": count}


@router.get("/stats/by-category")
async def get_books_by_category():
    """Get book count grouped by category"""
    stats = await crud.get_books_by_category()
    return {"categories": stats}


@router.get("/stats/price")
async def get_price_statistics():
    """Get price statistics"""
    stats = await crud.get_price_statistics()
    return stats


@router.get("/my-books", response_model=List[schemas.BookResponse])
async def read_my_books(current_user = Depends(get_current_active_user)):
    """Get all books owned by the current user"""
    books = await crud.get_user_books(user_id=str(current_user.id))
    return books


@router.get("/{book_id}", response_model=schemas.BookResponse)
async def read_book(
    book_id: str,
    redis_client = Depends(get_redis)
):
    """Get a specific book by ID (no authentication required)"""
    db_book = await crud.get_book(book_id=book_id, redis_client=redis_client)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.put("/{book_id}", response_model=schemas.BookResponse)
async def update_book(
    book_id: str,
    book: schemas.BookUpdate,
    current_user = Depends(get_current_active_user),
    redis_client = Depends(get_redis)
):
    """Update a book (only owner can update)"""
    db_book = await crud.update_book(
        book_id=book_id,
        book=book,
        owner_id=str(current_user.id),
        redis_client=redis_client
    )
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found or you don't have permission to update it"
        )
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    current_user = Depends(get_current_active_user),
    redis_client = Depends(get_redis)
):
    """Delete a book (only owner can delete)"""
    success = await crud.delete_book(
        book_id=book_id,
        owner_id=str(current_user.id),
        redis_client=redis_client
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Book not found or you don't have permission to delete it"
        )
    return None
