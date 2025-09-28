from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_CORS_ORIGINS = ["*"]


def add_cors_middleware(app: FastAPI):
    cors_origins = _CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_middlewares(app: FastAPI):
    add_cors_middleware(app)
