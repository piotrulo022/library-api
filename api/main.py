from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from modules import dbmodule
from routers import books, users


def get_db():
    db = dbmodule.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(users.router)


@app.get("/")
async def index():
    return RedirectResponse("/docs")
