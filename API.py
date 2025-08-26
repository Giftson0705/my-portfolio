from fastapi import FastAPI, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY", "default123")

app = FastAPI(title="Portfolio Backend")

# CORS setup (allow frontend on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
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

# In-memory database (demo only)
items = {}

# Pydantic model
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# Authentication dependency (simple API key check)
def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# --- CRUD Routes ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Portfolio Backend!"}

@app.post("/items", dependencies=[Depends(verify_api_key)])
def create_item(item: Item):
    item_id = len(items) + 1
    items[item_id] = item.dict()
    return {"id": item_id, "item": items[item_id]}

@app.get("/items/{item_id}")
def get_item(item_id: int, include_desc: bool = False):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    item = items[item_id]
    if not include_desc:
        item = {k: v for k, v in item.items() if k != "description"}
    return item

@app.put("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def update_item(item_id: int, new_item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = new_item.dict()
    return {"id": item_id, "item": items[item_id]}

@app.patch("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def patch_item(item_id: int, updates: dict):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id].update(updates)
    return {"id": item_id, "item": items[item_id]}

@app.delete("/items/{item_id}", dependencies=[Depends(verify_api_key)])
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = items.pop(item_id)
    return {"deleted": deleted}

# --- Contact Form Route ---
from fastapi import Body

@app.post("/api/contact")
async def contact(data: dict = Body(...)):
    print(" Contact form data:", data)
    return {"message": "Message received successfully!", "data": data}

