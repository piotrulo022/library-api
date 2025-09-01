from typing import List

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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
from sqlalchemy.orm import Session


def get_db():
    db = dbmodule.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return RedirectResponse("/docs")


@app.get("/books", response_model=List[schemas.BookResponse], tags=["BOOKS"])
async def get_books(db: Session = Depends(get_db)):
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


@app.post("/books/", response_model=schemas.BookCreateResponse, tags=["BOOKS"])
async def create_new_book(book_data: schemas.BookCreate, db: Session = Depends(get_db)):
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


@app.get("/books/{serial_number}", response_model=schemas.BookResponse, tags=["BOOKS"])
async def get_book_by_serial_number(serial_number: str, db: Session = Depends(get_db)):
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
    book = repo.get_by_serial(serial_number)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.patch(
    "/books/{serial_number}",
    response_model=schemas.BookStatusUpdateResponse,
    tags=["BOOKS"],
)
async def update_book(
    serial_number: str,
    update_book_data: schemas.BookStatusUpdate,
    db: Session = Depends(get_db),
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

    db.commit()

    return schemas.BookStatusUpdateResponse(
        detail="Books status changed successfully", serial_number=serial_number
    )


@app.delete(
    "/books/{serial_number}", response_model=schemas.BookDeleteResponse, tags=["BOOKS"]
)
async def delete_book(serial_number: str, db: Session = Depends(get_db)):
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
    book = book_repo.delete(serial_number)
    if not book:
        raise HTTPException(
            status_code=404, detail=f"Book with {serial_number} not found"
        )

    db.commit()

    return schemas.BookDeleteResponse(
        detail="Successfully deleted book", serial_number=serial_number
    )


@app.get("/users/", response_model=List[schemas.UserResponse], tags=["USERS"])
async def get_users(db: Session = Depends(get_db)):
    """
    Get all users.

    Returns:
        List[schemas.UserResponse]: List of users.

    Raises:
        HTTPException(503): If database connection fails.
    """
    users_repo = UserRepository(db)
    try:
        return users_repo.get_all()
    except OperationalError:
        raise HTTPException(
            status_code=503, detail="Could not fetch data from database"
        )


@app.post("/users/", response_model=schemas.UserCreateResponse, tags=["USERS"])
async def create_new_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user_data (schemas.UserCreate): User details.

    Returns:
        schemas.UserCreateResponse: Confirmation with card number.

    Raises:
        HTTPException(400): If user already exists.
        HTTPException(503): For other database errors.
    """
    users_repo = UserRepository(db)
    try:
        user = users_repo.add(user_data)
        db.commit()

        return schemas.UserCreateResponse(
            detail="Created new user successfully", card_number=user.card_number
        )
    except IntegrityError as e:
        db.rollback()
        if f"Key (card_number)=({user_data.card_number}) already exists" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail=f"User with card number {user_data.card_number} already exists",
            )
        raise HTTPException(status_code=503, detail="Database error")


@app.get(
    "/users/{card_number}", response_model=schemas.UserWithBooksResponse, tags=["USERS"]
)
async def get_users_info(card_number: str, db: Session = Depends(get_db)):
    if not utils.is_valid_card_number(card_number):
        raise HTTPException(status_code=400, detail="Card number must be 6 digits")
    users_repo = UserRepository(db)
    user = users_repo.get_by_card_number(card_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    borrowed_books = users_repo.get_users_borrowed_books(user)

    return schemas.UserWithBooksResponse(
        user=user,
        borrowed_books=borrowed_books,
    )


@app.delete(
    "/users/{card_number}", response_model=schemas.UserDeleteResponse, tags=["USERS"]
)
async def delete_user(card_number: str, db: Session = Depends(get_db)):
    """
    Delete a user and return borrowed books if any.

    Args:
        card_number (str): User's card number.

    Returns:
        schemas.UserDeleteResponse: Confirmation message.

    Raises:
        HTTPException(400): If card number is invalid.
        HTTPException(404): If user not found.
        HTTPException(500): If returning borrowed books fails.
    """
    if not utils.is_valid_card_number(card_number):
        raise HTTPException(status_code=400, detail="Card number must be 6 digits")
    users_repo = UserRepository(db)
    books_repo = BookRepository(db)

    user = users_repo.get_by_card_number(card_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    books = users_repo.get_users_borrowed_books(user)
    for book in books:
        try:
            books_repo.return_book(book)
        except BookAlreadyAvailable:
            continue
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    user = users_repo.delete(user.card_number)

    db.commit()

    return schemas.UserDeleteResponse(
        detail="Deleted user successfully", card_number=card_number
    )
