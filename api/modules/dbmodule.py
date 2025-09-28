import os
from contextlib import contextmanager

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/library"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = engine
        self._SessionLocal = SessionLocal

    @contextmanager
    def session(self) -> Session:
        db = self._SessionLocal()
        try:
            yield db
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(6), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    is_borrowed = Column(Boolean, default=False)
    borrow_date = Column(Date)
    borrower_card_number = Column(String(6), ForeignKey("users.card_number"))

    borrower = relationship("User", back_populates="borrowed_books")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(), nullable=False)
    last_name = Column(String(), nullable=False)
    card_number = Column(String(6), unique=True, nullable=False)

    borrowed_books = relationship("Book", back_populates="borrower")
