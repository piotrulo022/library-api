from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, validator
from utils import is_valid_card_number, is_valid_serial_number


class BookCreate(BaseModel):
    serial_number: str
    title: str
    author: str

    @validator("serial_number")
    def validate_serial_number(cls, v):
        if not is_valid_serial_number(v):
            raise ValueError("Serial number is not valid")
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


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    card_number: str

    borrowed_books: Union[None, List[BookResponse]]

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    serial_number: str
    title: str
    author: str

    @validator("serial_number")
    def validate_serial_number(cls, v):
        if not is_valid_serial_number(v):
            raise ValueError("Serial number is not valid")
        return v


class UserCreate(BaseModel):
    card_number: str
    first_name: str
    last_name: str

    @validator("card_number")
    def validate_card_number(cls, v):
        if not is_valid_card_number(v):
            raise ValueError("Card number is not valid")
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


class BookStatusUpdate(BaseModel):
    is_borrowed: bool
    borrowed_date: Optional[date] = None
    borrower_card_number: Optional[str] = None

    class Config:
        validate_assignment = True

    @validator("borrowed_date", pre=True, always=True)
    def set_borrowed_date(cls, v, values):
        if values.get("is_borrowed") and v is None:
            return date.today()
        return v

    @validator("borrower_card_number")
    def validate_card_number(cls, v, values):
        if values.get("is_borrowed") and v is None:
            raise ValueError("Borrower card number is required when borrowing a book")
        if v is not None:
            if not is_valid_card_number(v):
                raise ValueError("Card number must be 6 digits")
        return v

    @validator("borrowed_date")
    def validate_date_consistency(cls, v, values):
        is_borrowed = values.get("is_borrowed")

        if is_borrowed and v is None:
            return v

        if not is_borrowed and v is not None:
            raise ValueError(
                "Borrowed date must be null when book is getting available"
            )
        return v
