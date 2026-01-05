from fastapi import APIRouter, HTTPException
from typing import List
from app.models.item import ItemCreate, ItemUpdate, ItemInDB

router = APIRouter()

# Mock database
fake_items_db = {}
item_id_counter = 1


@router.get("/", response_model=List[ItemInDB])
def get_items(skip: int = 0, limit: int = 10):
    items = list(fake_items_db.values())
    return items[skip : skip + limit]


@router.get("/{item_id}", response_model=ItemInDB)
def get_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]


@router.post("/", response_model=ItemInDB, status_code=201)
def create_item(item: ItemCreate):
    global item_id_counter
    item_in_db = ItemInDB(id=item_id_counter, **item.model_dump())
    fake_items_db[item_id_counter] = item_in_db
    item_id_counter += 1
    return item_in_db


@router.put("/{item_id}", response_model=ItemInDB)
def update_item(item_id: int, item: ItemUpdate):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    stored_item = fake_items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item.model_copy(update=update_data)
    fake_items_db[item_id] = updated_item
    return updated_item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_items_db[item_id]
