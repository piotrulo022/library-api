
# 📚 Library Management API

A simple REST API for managing a library system.  
This project provides functionality for library staff to track and update the status of books in the library’s collection.

---

## ✨ Features

The API allows staff to:

-  **add a new book**  
-  **remove a book**  
-  **retrieve a list of all books**  
-  **update book status** (mark as borrowed/available)

---

## 📖 Data Model

Each book has the following attributes:

- `serial_number` – unique six-digit number entered by staff (e.g., `123456`)  
- `title` – book title  
- `author` – book author  
- `is_borrowed` – whether the book is currently borrowed  - `borrowed_by` – library card number of the borrower (six-digit number); `None` when  `is_borrowed = false`
- `borrowed_by` – library card number of the borrower (six-digit number); `None` when  `is_borrowed = false`

---

## 🚀 Tech Stack
- **uv**
- **Python 3.12**  
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Docker & docker-compose**
- **Pytest** 

---

## 🛠️ Installation & Running
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
