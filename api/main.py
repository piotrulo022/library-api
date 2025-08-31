from typing import List

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
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


@app.get("/")
async def index():
    return RedirectResponse("/docs")


@app.get("/books", response_model=List[schemas.BookResponse])
async def get_books(db: Session = Depends(get_db)):
    books_repo = BookRepository(db)
    try:
        return books_repo.get_all()
    except OperationalError:
        raise HTTPException(
            status_code=503, detail="Could not fetch data from database"
        )


@app.post("/books/")
async def create_new_book(book_data: schemas.BookCreate, db: Session = Depends(get_db)):
    books_repo = BookRepository(db)
    try:
        book = books_repo.add(book_data)
        db.commit()
        return {"serial_number": book.serial_number}

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


@app.get("/books/{serial_number}", response_model=schemas.BookResponse)
async def get_book_by_serial_number(serial_number: str, db: Session = Depends(get_db)):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number is not valid")

    repo = BookRepository(db)
    book = repo.get_by_serial(serial_number)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")


@app.patch("/books/{serial_number}")
async def update_book(
    serial_number: str,
    update_book_data: schemas.BookStatusUpdate,
    db: Session = Depends(get_db),
):
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

    return {
        "message": f"Successfully updated status of Book with serial {serial_number}"
    }


@app.delete("/books/{serial_number}")
async def delete_book(serial_number: str, db: Session = Depends(get_db)):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")

    book_repo = BookRepository(db)
    book = book_repo.delete(serial_number)
    if not book:
        raise HTTPException(
            status_code=404, detail=f"Book with {serial_number} not found"
        )

    db.commit()

    return {"detail": f"Successfully deleted book with serial number {serial_number}"}


@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users_repo = UserRepository(db)
    try:
        return users_repo.get_all()
    except OperationalError:
        raise HTTPException(
            status_code=503, detail="Could not fetch data from database"
        )


@app.post("/users/")
async def create_new_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    users_repo = UserRepository(db)
    try:
        user = users_repo.add(user_data)
        db.commit()
        return {"card_number": user.card_number}
    except IntegrityError as e:
        db.rollback()
        if f"Key (card_number)=({user_data.card_number}) already exists" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail=f"User with card number {user_data.card_number} already exists",
            )
        raise HTTPException(status_code=503, detail="Database error")
    except:
        db.rollback()


@app.get("/users/{card_number}", response_model=schemas.UserResponse)
async def get_users_info(card_number: str, db: Session = Depends(get_db)):
    if not utils.is_valid_card_number(card_number):
        raise HTTPException(status_code=400, detail="Card number must be 6 digits")
    users_repo = UserRepository(db)
    user = users_repo.get_by_card_number(card_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    borrowed_books = users_repo.get_users_borrowed_books(user)

    return schemas.UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        card_number=user.card_number,
        borrowed_books=borrowed_books,
    )


@app.delete("/users/{card_number}")
async def delete_user(card_number: str, db: Session = Depends(get_db)):
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

    return {"detail": "Deleted user successfully"}
