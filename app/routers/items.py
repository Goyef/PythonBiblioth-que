from fastapi import APIRouter, HTTPException
from models import Item

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/")
def list_items():
    return {"items": []}

@router.post("/")
def create_item(item: Item):
    return item

@router.get("/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}