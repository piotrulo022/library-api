from typing import List

import dbmodule
import schemas
import utils
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError, OperationalError

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


@app.post("/users/")
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


@app.get("/books/{serial_number}", response_model=schemas.BookResponse)
async def get_book_by_serial_number(serial_number: str):
    if not utils.is_valid_serial_number(serial_number):
        raise HTTPException(status_code=400, detail="Serial number must be 6 digits")

    with dbmodule.SessionLocal() as session:
        book_info = (
            session.query(dbmodule.Book)
            .filter(dbmodule.Book.serial_number == serial_number)
            .first()
        )

        if not book_info:
            raise HTTPException(status_code=404, detail="Book not found")
    return book_info


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
