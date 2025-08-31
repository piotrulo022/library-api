from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, validator
from utils import is_valid_serial_number


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
