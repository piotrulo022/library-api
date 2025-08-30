import re
from datetime import date
from typing import List, Optional

import dbmodule
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, validator

cn_regex = r"^[0-9]{6}"


class BookCreate(BaseModel):
    serial_number: str
    title: str
    author: str

    @validator("serial_number")
    def validate_serial_number(cls, v):
        if not re.fullmatch(r"^[0-9]{6}$", v):
            raise ValueError("Serial number must be 6 digits")
        return v


class BookResponse(BaseModel):
    id: int
    serial_number: str
    author: str
    title: str
    is_borrowed: bool
    borrow_date: Optional[date] = None
    borrower_card_number: Optional[str]

    class Config:
        from_attributes = True  # enables conversion from ORM


app = FastAPI()


@app.get("/")
async def index():
    return RedirectResponse("/docs")


@app.get("/books", response_model=List[BookResponse])
async def get_books():
    session = dbmodule.SessionLocal()

    with dbmodule.SessionLocal() as session:
        all_books = session.query(dbmodule.Book).all()
        return all_books


@app.post("/users/")
async def get_users():
    session = dbmodule.SessionLocal()

    with dbmodule.SessionLocal() as session:
        all_users = session.query(dbmodule.User).all()
        return all_users


@app.get("/books/{serial_number}", response_model=BookResponse)
async def get_book_by_serial_number(serial_number: str):
    if not re.fullmatch(pattern=cn_regex, string=serial_number):
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


@app.post("/books/", response_model=BookCreate)
async def create_new_book(book_data: BookCreate):
    raise NotImplementedError
