import sys
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError

api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))


from main import app, get_db
from modules import schemas
from modules.repositories import BookNotFoundError

client = TestClient(app)

mock_book = schemas.BookResponse(
    id=1,
    serial_number="123456",
    author="Test Author",
    title="Test Title",
    is_borrowed=False,
    borrow_date=None,
    borrower_card_number=None,
)

mock_user = schemas.UserResponse(
    id=1, first_name="John", last_name="Doe", card_number="654321"
)


mock_db = Mock()

app.dependency_overrides[get_db] = lambda: mock_db


def test_get_books_success():
    with patch("main.BookRepository") as mock_repo:
        mock_repo.return_value.get_all.return_value = [mock_book]
        response = client.get("/books")
        assert response.status_code == 200
        assert response.json()[0]["serial_number"] == "123456"


def test_get_books_database_error():
    with patch("main.BookRepository") as mock_repo:
        mock_repo.return_value.get_all.side_effect = OperationalError("", "", "")
        response = client.get("/books")
        assert response.status_code == 503


def test_create_book_success():
    with patch("main.BookRepository") as mock_repo:
        mock_repo.return_value.add.return_value = Mock(serial_number="123456")
        response = client.post(
            "/books/",
            json={"serial_number": "123456", "title": "Test", "author": "Author"},
        )
        assert response.status_code == 200
        assert response.json()["serial_number"] == "123456"


def test_create_book_duplicate():
    with patch("main.BookRepository") as mock_repo:
        mock_repo.return_value.add.side_effect = IntegrityError("", "", "")
        response = client.post(
            "/books/",
            json={"serial_number": "123456", "title": "Test", "author": "Author"},
        )
        assert response.status_code == 503


def test_update_book_not_found():
    with (
        patch("main.BookRepository") as mock_book_repo,
        patch("main.UserRepository") as mock_user_repo,
    ):
        mock_book_repo.return_value.update_book_status.side_effect = BookNotFoundError(
            ""
        )
        response = client.patch(
            "/books/123456",
            json={
                "is_borrowed": True,
                "borrower_card_number": "654321",
                "borrowed_date": "2023-01-01",
            },
        )
        assert response.status_code == 404


def test_delete_user_success():
    with (
        patch("main.UserRepository") as mock_user_repo,
        patch("main.BookRepository") as mock_book_repo,
    ):
        mock_user_repo.return_value.get_by_card_number.return_value = Mock()
        mock_user_repo.return_value.get_users_borrowed_books.return_value = []
        mock_user_repo.return_value.delete.return_value = Mock()
        response = client.delete("/users/654321")
        assert response.status_code == 200
        assert "654321" in response.json()["card_number"]
