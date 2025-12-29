from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Hello World API", version="1.0.0")


# Simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Path parameters
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# Request body example
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.post("/items/")
def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
