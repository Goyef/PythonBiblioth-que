from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.error_handlers import (
    generic_exception_handler,
    library_exception_handler,
    validation_exception_handler,
)
from app.exceptions import LibraryException
#from app.routers import author, book, loan, stats

from fastapi import FastAPI
from pydantic import BaseModel
from app.routers.livre import router as livres_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gérer le cycle de vie de l'application"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


# Créer l'application FastAPI
app = FastAPI(
    title="API Gestion de Bibliothèque",
    description="API REST complète pour gérer une bibliothèque moderne",
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

# Inclure les routers
#app.include_router(author.router)
app.include_router(livres_router)
#app.include_router(loan.router)
#app.include_router(stats.router)


@app.get("/", tags=["Root"])
def read_root():
    """Endpoint racine de l'API"""
    return {
        "message": "Bienvenue sur l'API de gestion de bibliothèque",
        "version": "1.0.0",
        "documentation": "/docs",
    }
