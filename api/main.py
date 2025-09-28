from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from middlewares import add_cors_middleware
from modules import dbmodule
from routers import books, users


def get_db():
    db = dbmodule.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
add_cors_middleware(app)


app.include_router(books.router)
app.include_router(users.router)


@app.get("/")
async def index():
    return RedirectResponse("/docs")
