from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator

from .utils import is_valid_card_number, is_valid_serial_number


class BookCreate(BaseModel):
    serial_number: str
    title: str
    author: str

    @field_validator("serial_number")
    @classmethod
    def validate_serial_number(cls, v: str):
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

    model_config = ConfigDict(from_attributes=True)


class BookCreateResponse(BaseModel):
    serial_number: str


class BookDeleteResponse(BaseModel):
    detail: str
    serial_number: str


class BookStatusUpdate(BaseModel):
    is_borrowed: bool
    borrowed_date: Optional[date] = None
    borrower_card_number: Optional[str] = None

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("borrower_card_number")
    @classmethod
    def validate_card_number(cls, v: Optional[str], info):
        is_borrowed = info.data.get("is_borrowed")

        if is_borrowed:
            if not v:
                raise ValueError(
                    "Borrower card number is required when borrowing a book"
                )
            if not is_valid_card_number(v):
                raise ValueError("Card number must be 6 digits")
        else:
            if v is not None:
                raise ValueError(
                    "Borrower card number must not be provided when returning a book"
                )

        return v

    @field_validator("borrowed_date")
    @classmethod
    def validate_date_consistency(cls, v: Optional[date], info):
        is_borrowed = info.data.get("is_borrowed")

        if is_borrowed and v is None:
            return v

        if not is_borrowed and v is not None:
            raise ValueError(
                "Borrowed date must be null when book is getting available"
            )
        return v


class BookStatusUpdateResponse(BaseModel):
    detail: str
    serial_number: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    card_number: str

    model_config = ConfigDict(from_attributes=True)


class UserWithBooksResponse(BaseModel):
    user: UserResponse
    borrowed_books: Union[None, List[BookResponse]]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    card_number: str
    first_name: str
    last_name: str

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str):
        if not is_valid_card_number(v):
            raise ValueError("Card number is not valid")
        return v


class UserCreateResponse(BaseModel):
    detail: str
    card_number: str


class UserDeleteResponse(BaseModel):
    detail: str
    card_number: str
