from typing import List

from fastapi import APIRouter, Depends, HTTPException
from modules import dbmodule, schemas, utils
from modules.repositories import (
    BookAlreadyAvailable,
    BookAlreadyBorrowed,
    BookNotFoundError,
    BookRepository,
    UserNotFoundError,
    UserRepository,
)
from sqlalchemy.exc import IntegrityError, OperationalError

router = APIRouter()


@router.get("/books", response_model=List[schemas.BookResponse], tags=["BOOKS"])
async def get_books(db: dbmodule.Session = Depends(dbmodule.get_db)):
    """
    Get all books from the database.

    Returns:
        List[schemas.BookResponse]: List of books.

    Raises:
        HTTPException(503): If database connection fails.
    """
    books_repo = BookRepository(db)
    try:
        return books_repo.get_all()
    except OperationalError:
        raise HTTPException(
            status_code=503, detail="Could not fetch data from database"
        )


@router.post("/books/", response_model=schemas.BookCreateResponse, tags=["BOOKS"])
async def create_new_book(
    book_data: schemas.BookCreate, db: dbmodule.Session = Depends(dbmodule.get_db)
):
    """
    Create a new book in the database.

    Args:
        book_data (schemas.BookCreate): Book data to insert.

    Returns:
        schemas.BookCreateResponse: Confirmation with book serial number.

    Raises:
        HTTPException(400): If book already exists.
        HTTPException(503): For other database errors.
    """
    books_repo = BookRepository(db)
    try:
        book = books_repo.add(book_data)
        db.commit()
        return schemas.BookCreateResponse(serial_number=book.serial_number)

    except IntegrityError as e:
        db.rollback()
        if f"Key (serial_number)=({book_data.serial_number}) already exists" in str(
            e.orig
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Book with serial number {book_data.serial_number} already exists",
            )
        raise HTTPException(status_code=503, detail="Database error")


@router.get(
    "/books/{serial_number}", response_model=schemas.BookResponse, tags=["BOOKS"]
)
async def get_book_by_serial_number(
    serial_number: str, db: dbmodule.Session = Depends(dbmodule.get_db)
):
    """
    Retrieve a book by its serial number.

    Args:
        serial_number (str): Book serial number.

    Returns:
        schemas.BookResponse: Book details.

    Raises:
        HTTPException(400): If serial number is invalid.
        HTTPException(404): If book not found.
    """
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number is not valid")

    repo = BookRepository(db)
    try:
        book = repo.get_by_serial(serial_number)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch(
    "/books/{serial_number}",
    response_model=schemas.BookStatusUpdateResponse,
    tags=["BOOKS"],
)
async def update_book(
    serial_number: str,
    update_book_data: schemas.BookStatusUpdate,
    db: dbmodule.Session = Depends(dbmodule.get_db),
):
    """
    Update the status of a book (borrow or return).

    Args:
        serial_number (str): Book serial number.
        update_book_data (schemas.BookStatusUpdate): Update details.

    Returns:
        schemas.BookStatusUpdateResponse: Confirmation with serial number.

    Raises:
        HTTPException(400): If serial number is invalid or book is unavailable.
        HTTPException(404): If book or user not found.
        HTTPException(422): If provided wrong arguments as body request (when returning a book, date and borrower card id must be not provided)
    """
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")

    book_repo = BookRepository(db)
    user_repo = UserRepository(db)
    try:
        book_repo.update_book_status(
            serial_number, update_book_data, user_repo=user_repo
        )
    except BookAlreadyAvailable as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BookAlreadyBorrowed as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")

    db.commit()

    return schemas.BookStatusUpdateResponse(
        detail="Books status changed successfully", serial_number=serial_number
    )


@router.delete(
    "/books/{serial_number}", response_model=schemas.BookDeleteResponse, tags=["BOOKS"]
)
async def delete_book(
    serial_number: str, db: dbmodule.Session = Depends(dbmodule.get_db)
):
    """
    Delete a book by its serial number.

    Args:
        serial_number (str): Book serial number.

    Returns:
        schemas.BookDeleteResponse: Confirmation message.

    Raises:
        HTTPException(400): If serial number is invalid.
        HTTPException(404): If book not found.
    """
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")

    book_repo = BookRepository(db)
    try:
        book = book_repo.delete(serial_number)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")

    if not book:
        raise HTTPException(
            status_code=404, detail=f"Book with {serial_number} not found"
        )

    db.commit()

    return schemas.BookDeleteResponse(
        detail="Successfully deleted book", serial_number=serial_number
    )
