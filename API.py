from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY", "default123")

app = FastAPI(title="Simple FastAPI Demo")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware example
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# In-memory database (just for demo)
items = {}

# Pydantic model for request body
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# Authentication dependency
def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# --- CRUD Routes ---

# Create (POST with request body)
@app.post("/items", dependencies=[Depends(verify_api_key)])
def create_item(item: Item):
    item_id = len(items) + 1
    items[item_id] = item.dict()
    return {"id": item_id, "item": items[item_id]}

# Read (GET with query + path param)
@app.get("/items/{item_id}")
def get_item(item_id: int, include_desc: bool = False):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    item = items[item_id]
    if not include_desc:
        item = {k: v for k, v in item.items() if k != "description"}
    return item

# Update (PUT replaces full item)
@app.put("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def update_item(item_id: int, new_item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = new_item.dict()
    return {"id": item_id, "item": items[item_id]}

# Partial Update (PATCH updates only some fields)
@app.patch("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def patch_item(item_id: int, updates: dict):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id].update(updates)
    return {"id": item_id, "item": items[item_id]}

# Delete
@app.delete("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = items.pop(item_id)
    return {"deleted": deleted}
