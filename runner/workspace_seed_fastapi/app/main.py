from fastapi import FastAPI, HTTPException
from .models import Item, ItemCreate

app = FastAPI(title="Inventory API", version="0.1.0")

items: dict[int, Item] = {}
_next_id = 1


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/items", response_model=list[Item])
def list_items():
    return list(items.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/items", response_model=Item, status_code=201)
def create_item(body: ItemCreate):
    global _next_id
    item = Item(id=_next_id, **body.model_dump())
    items[_next_id] = item
    _next_id += 1
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
