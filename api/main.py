from typing import List

import dbmodule
import schemas
import utils
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

app = FastAPI()


@app.get("/")
async def index():
    return RedirectResponse("/docs")


@app.get("/books", response_model=List[schemas.BookResponse])
async def get_books():
    session = dbmodule.SessionLocal()

    with dbmodule.SessionLocal() as session:
        try:
            all_books = session.query(dbmodule.Book).all()
            return all_books
        except OperationalError:
            raise HTTPException(
                status_code=503, detail="Could not fetch data from database"
            )


@app.post("/books/")
async def create_new_book(book_data: schemas.BookCreate):
    try:
        with dbmodule.SessionLocal.begin() as session:
            book_orm = dbmodule.Book(**book_data.dict())
            session.add(book_orm)
            response_detils = {"serial_number": book_orm.serial_number}
        return response_detils
    except IntegrityError as e:
        if f"Key (serial_number)=({book_data.serial_number}) already exists" in str(
            e.orig
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Book with serial number {book_data.serial_number} already exists",
            )
        raise HTTPException(status_code=503, detail="Database error")


@app.get("/books/{serial_number}", response_model=schemas.BookResponse)
async def get_book_by_serial_number(serial_number: str):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number is not valid")

    with dbmodule.SessionLocal() as session:
        book_info = (
            session.query(dbmodule.Book)
            .filter(dbmodule.Book.serial_number == serial_number)
            .first()
        )

        if not book_info:
            raise HTTPException(status_code=404, detail="Book not found")
    return book_info


@app.patch("/books/{serial_number}")
async def update_book(serial_number: str, update_book_data: schemas.BookStatusUpdate):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")

    try:
        with dbmodule.SessionLocal.begin() as session:
            book = (
                session.query(dbmodule.Book)
                .filter(dbmodule.Book.serial_number == serial_number)
                .first()
            )
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            user_exists: bool = session.scalar(
                exists()
                .where(
                    dbmodule.User.card_number == update_book_data.borrower_card_number
                )
                .select()
            )
            if not user_exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"User with card number {update_book_data.borrower_card_number} does not exist",
                )

            if book.is_borrowed == update_book_data.is_borrowed:
                book_status = "borrowed" if book.is_borrowed else "available"
                raise HTTPException(
                    status_code=400,
                    detail=f"Book with serial number {serial_number} is already {book_status}",
                )

            book.is_borrowed = update_book_data.is_borrowed
            if book.is_borrowed:
                book.borrow_date = update_book_data.borrowed_date
                book.borrower_card_number = update_book_data.borrower_card_number
            else:
                book.borrow_date = None
                book.borrower_card_number = None
            return {
                "message": f"Successfuly updated status of Book with serial number {book.serial_number}"
            }
    except Exception:
        raise


@app.delete("/books/{serial_number}")
async def delete_book(serial_number: str):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")
    try:
        with dbmodule.SessionLocal.begin() as session:
            book = (
                session.query(dbmodule.Book)
                .filter(dbmodule.Book.serial_number == serial_number)
                .first()
            )
            if not book:
                raise HTTPException(
                    status_code=404,
                    detail="Could not find book with provided serial number",
                )
            session.delete(book)
        return {"details": f"Book with serial {serial_number} deleted successfully"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database error")


@app.get("/users/")
async def get_users():
    session = dbmodule.SessionLocal()

    with dbmodule.SessionLocal() as session:
        try:
            all_users = session.query(dbmodule.User).all()
            return all_users
        except OperationalError:
            raise HTTPException(
                status_code=503, detail="Could not fetch data from database"
            )


@app.post("/users/")
async def create_new_user(user_data: schemas.UserCreate):
    try:
        with dbmodule.SessionLocal.begin() as session:
            # book_orm = dbmodule.Book(**b.dict())
            user_orm = dbmodule.User(**user_data.dict())
            session.add(user_orm)
            response_detils = {"card_number": user_orm.card_number}
        return response_detils
    except IntegrityError as e:
        if f"Key (card_number)=({user_data.card_number}) already exists" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail=f"User with card number {user_data.card_number} already exists",
            )
        raise HTTPException(status_code=503, detail="Database error")


@app.get("/users/{card_number}", response_model=schemas.UserResponse)
async def get_users_info(card_number: str):
    if not utils.is_valid_card_number(card_number):
        raise HTTPException(status_code=400, detail="Card number must be 6 digits")

    with dbmodule.SessionLocal() as session:
        user_info = (
            session.query(dbmodule.User)
            .filter(dbmodule.User.card_number == card_number)
            .first()
        )
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")

        borrowed_books = (
            session.query(dbmodule.Book)
            .filter(dbmodule.Book.borrower_card_number == user_info.card_number)
            .all()
        )

    return schemas.UserResponse(
        id=user_info.id,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        card_number=user_info.card_number,
        borrowed_books=borrowed_books,
    )
