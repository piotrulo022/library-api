from typing import List

from fastapi import APIRouter, Depends, HTTPException
from modules import dbmodule, schemas, utils
from modules.repositories import (
    BookAlreadyAvailable,
    BookRepository,
    UserRepository,
)
from sqlalchemy.exc import IntegrityError, OperationalError

router = APIRouter()


@router.get("/users/", response_model=List[schemas.UserResponse], tags=["USERS"])
async def get_users(db: dbmodule.Session = Depends(dbmodule.get_db)):
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


@router.post("/users/", response_model=schemas.UserCreateResponse, tags=["USERS"])
async def create_new_user(
    user_data: schemas.UserCreate, db: dbmodule.Session = Depends(dbmodule.get_db)
):
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
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")


@router.get(
    "/users/{card_number}", response_model=schemas.UserWithBooksResponse, tags=["USERS"]
)
async def get_users_info(
    card_number: str, db: dbmodule.Session = Depends(dbmodule.get_db)
):
    if not utils.is_valid_card_number(card_number):
        raise HTTPException(status_code=400, detail="Card number must be 6 digits")
    users_repo = UserRepository(db)
    try:
        user = users_repo.get_by_card_number(card_number)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    borrowed_books = users_repo.get_users_borrowed_books(user)

    return schemas.UserWithBooksResponse(
        user=user,
        borrowed_books=borrowed_books,
    )


@router.delete(
    "/users/{card_number}", response_model=schemas.UserDeleteResponse, tags=["USERS"]
)
async def delete_user(
    card_number: str, db: dbmodule.Session = Depends(dbmodule.get_db)
):
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
    try:
        user = users_repo.get_by_card_number(card_number)
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database error")

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
