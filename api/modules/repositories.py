from datetime import date
from typing import Optional

from sqlalchemy import exists
from sqlalchemy.orm import Session

from . import dbmodule, schemas


class UserNotFoundError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class BookAlreadyBorrowed(Exception):
    pass


class BookAlreadyAvailable(Exception):
    pass


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(dbmodule.User).all()

    def get_by_card_number(self, card_number: str):
        return (
            self.session.query(dbmodule.User)
            .filter(dbmodule.User.card_number == card_number)
            .first()
        )

    def add(self, user_data: schemas.UserCreate):
        user = dbmodule.User(**user_data.dict())
        self.session.add(user)
        return user

    def get_users_borrowed_books(self, user: dbmodule.User):
        borrowed_books = (
            self.session.query(dbmodule.Book)
            .filter(dbmodule.Book.borrower_card_number == user.card_number)
            .all()
        )
        return borrowed_books

    def exists(self, card_number: str) -> bool:
        return bool(
            self.session.scalar(
                exists().where(dbmodule.User.card_number == card_number).select()
            )
        )

    def delete(self, card_number: str) -> bool:
        user = self.get_by_card_number(card_number)
        if user:
            self.session.delete(user)
        return user


class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.query(dbmodule.Book).all()

    def get_by_serial(self, serial: str):
        return (
            self.session.query(dbmodule.Book)
            .filter(dbmodule.Book.serial_number == serial)
            .first()
        )

    def add(self, book_data: schemas.BookCreate):
        book = dbmodule.Book(**book_data.dict())
        self.session.add(book)
        return book

    def delete(self, serial: str):
        book = self.get_by_serial(serial)
        if book:
            self.session.delete(book)
        return book

    def update_book_status(
        self,
        serial: str,
        update_data: schemas.BookStatusUpdate,
        user_repo: Optional[
            UserRepository
        ] = None,  # used to check if provided user with card_number exists
    ):
        book = self.get_by_serial(serial)
        if not book:
            raise BookNotFoundError(f"Could not find book with serial {serial}")

        if update_data.is_borrowed is True:
            self.borrow_book(
                book,
                card_number=update_data.borrower_card_number,
                borrow_date=update_data.borrowed_date,
                user_repo=user_repo,
            )
        elif update_data.is_borrowed is False:
            self.return_book(book)

    def borrow_book(
        self,
        book: dbmodule.Book,
        card_number: str,
        borrow_date: date,
        user_repo: UserRepository,
    ):
        if book.is_borrowed is True:
            raise BookAlreadyBorrowed(
                f"Book with serial number {book.serial_number} is already borrowed"
            )
        if not user_repo.exists(card_number):
            raise UserNotFoundError(
                f"User with card_number {card_number} does not exist"
            )

        book.is_borrowed = True
        book.borrower_card_number = card_number
        book.borrow_date = borrow_date

    def return_book(self, book: dbmodule.Book):
        if not book.is_borrowed:
            raise BookAlreadyAvailable(
                f"Book with serial number {book.serial_number} is already available"
            )
        book.is_borrowed = False
        book.borrower_card_number = None
        book.borrow_date = None
