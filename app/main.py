from fastapi import FastAPI
from pydantic import BaseModel
from app.routers.livre import router as livres_router

app = FastAPI(
    title="Bibliothèque API",
    description="API pour gérer une bibliothèque de livres.",
    version="1.0.0"
)

app.include_router(livres_router)

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
def read_root():
    return {"message": "Bienvenue à l'API de la Bibliothèque"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.post("/items/")
# def create_item(item: Item):
#     return {"item": item, "message": "Item créé avec succès"}

