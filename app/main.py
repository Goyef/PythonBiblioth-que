from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.database import create_db_and_tables 
from app.error_handlers import (
    generic_exception_handler,
    library_exception_handler,
    validation_exception_handler,
)
from app.exceptions import LibraryException
from app.routers.book import router as livres_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gérer le cycle de vie de l'application"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass
from app.routers.book import router as livres_router
from app.routers.author import router as auteurs_router

app = FastAPI(
    title="Bibliothèque API",
    description="API pour gérer une bibliothèque de livres.",
    version="1.0.0",
     docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer les handlers d'erreurs
app.add_exception_handler(LibraryException, library_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(livres_router)
app.include_router(auteurs_router)

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue à l'API de la Bibliothèque"}


