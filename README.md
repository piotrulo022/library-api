
# 📚 Library Management API

A simple REST API for managing a library system.  
This project provides functionality for library staff to track and update the status of books in the library’s collection.

---

## Features

The API allows staff to:

-  **add a new book**  
-  **remove a book**  
-  **retrieve a list of all books**  
-  **update book status** (mark as borrowed/available)

---

## Tech Stack
- **uv**
- **Python 3.12**  
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Docker & docker-compose**
- **Pytest** 

---

## Installation & Running
Make sure you have **docker** and **docker compose** installed.

```bash
git clone https://github.com/your-username/library-api.git
cd library-api
docker compose up --build
```

For configuration inspect `docker-compose.yml`. By default port **5432** is mapped for database, **8000** for API. 

The database tables will be created automatically on first run and populated with sample data (see `database/init.sql`).


Access the API documentation:
You can use swagger  to do requests or use curl:

```bash
# get all books from database
curl -X GET http://localhost:8000/books
```

## Endpoints Overview

### Root

- **GET /**  
  Redirects to Swagger UI at `/docs`.

---

### Books Endpoints

#### 1. Get all books
- **Endpoint:** `GET /books`  
- **Description:** Retrieves a list of all books in the library.  
- **Response:** List of books with serial number, title, author, and borrow status.  
- **Example:**
```bash
curl -X GET http://localhost:8000/books -H "accept: application/json"
````

---

#### 2. Add a new book

* **Endpoint:** `POST /books/`
* **Description:** Adds a new book to the library database.
* **Request Body:**

```json
{
  "serial_number": "123456",
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald"
}
```

* **Response:**

```json
{
  "serial_number": "123456"
}
```

---

#### 3. Get a book by serial number

* **Endpoint:** `GET /books/{serial_number}`
* **Description:** Retrieves details of a single book.
* **Path Parameter:**

  * `serial_number` – 6-digit book serial number
* **Response:** Book details including borrow status.
* **Example:**

```bash
curl -X GET http://localhost:8000/books/123456 -H "accept: application/json"
```

---

#### 4. Update book status

* **Endpoint:** `PATCH /books/{serial_number}`
* **Description:** Marks a book as borrowed or returned.
* **Path Parameter:**

  * `serial_number` – 6-digit book serial number
* **Request Body Example (borrow a book):**

```json
{
  "is_borrowed": true,
  "borrowed_by": "654321"
}
```

* **Request Body Example (return a book):**

```json
{
  "is_borrowed": false
}
```

* **Response:**

```json
{
  "detail": "Books status changed successfully",
  "serial_number": "123456"
}
```
---

#### 5. Delete a book

* **Endpoint:** `DELETE /books/{serial_number}`
* **Description:** Deletes a book from the library.
* **Path Parameter:**

  * `serial_number` – 6-digit book serial number
* **Response:**

```json
{
  "detail": "Successfully deleted book",
  "serial_number": "123456"
}
```

---

### Users Endpoints

#### 1. Get all users

* **Endpoint:** `GET /users/`
* **Description:** Retrieves a list of all library users.
* **Response:** List of users with card number, name, etc.
* **Example:**

```bash
curl -X GET http://localhost:8000/users/ -H "accept: application/json"
```

---

#### 2. Add a new user

* **Endpoint:** `POST /users/`
* **Description:** Adds a new user to the library database.
* **Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "card_number": "654321"
}
```

* **Response:**

```json
{
  "detail": "Created new user successfully",
  "card_number": "654321"
}
```
---

#### 3. Get user info with borrowed books

* **Endpoint:** `GET /users/{card_number}`
* **Description:** Retrieves user details along with borrowed books.
* **Path Parameter:**

  * `card_number` – 6-digit library card number
* **Response Example:**

```json
{
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "card_number": "654321"
  },
  "borrowed_books": [
    {
      "serial_number": "123456",
      "title": "The Great Gatsby",
      "author": "F. Scott Fitzgerald",
      "is_borrowed": true,
      "borrowed_by": "654321",
      "borrowed_at": "2025-09-01T10:15:00"
    }
  ]
}
```

---

#### 4. Delete a user

* **Endpoint:** `DELETE /users/{card_number}`
* **Description:** Deletes a user and returns any borrowed books to the library.
* **Path Parameter:**

  * `card_number` – 6-digit library card number
* **Response:**

```json
{
  "detail": "Deleted user successfully",
  "card_number": "654321"
}
```

