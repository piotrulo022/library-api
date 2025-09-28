from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from middlewares import add_cors_middleware
from routers import books, users

app = FastAPI()
add_cors_middleware(app)


app.include_router(books.router)
app.include_router(users.router)


@app.get("/")
async def index():
    return RedirectResponse("/docs")
