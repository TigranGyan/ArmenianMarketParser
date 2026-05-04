import os
from typing import List, Optional

import auth
import models
from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

import database

app = FastAPI(title="Price Aggregator API")

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user_data.password)
    new_user = models.User(email=user_data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Elasticsearch client
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

@app.get("/api/v1/search")
async def search_products(
    q: str = Query(..., min_length=1),
    store_id: Optional[int] = None,
    category: Optional[str] = None,
    sort: str = "price_asc",
    page: int = 1
):
    # This is a simplified search implementation
    # In a real production app, this would build a complex ES query
    size = 20
    from_ = (page - 1) * size

    query = {
        "bool": {
            "must": [
                {"multi_match": {"query": q, "fields": ["canonical_name", "brand"]}}
            ]
        }
    }

    if store_id:
        query["bool"]["filter"] = query.get("bool", {}).get("filter", []) + [
            {"nested": {"path": "prices", "query": {"term": {"prices.store_id": store_id}}}}
        ]

    sort_config = []
    if sort == "price_asc":
        sort_config.append({"min_price": {"order": "asc"}})
    elif sort == "price_desc":
        sort_config.append({"min_price": {"order": "desc"}})

    try:
        res = es.search(
            index="products_search",
            query=query,
            sort=sort_config,
            from_=from_,
            size=size
        )
        return {
            "total": res["hits"]["total"]["value"],
            "page": page,
            "items": [hit["_source"] for hit in res["hits"]["hits"]]
        }
    except Exception as e:
        # Fallback or error handling
        return {"error": str(e), "items": []}

@app.get("/api/v1/stores")
async def get_stores(db: Session = Depends(database.get_db)):
    return db.query(models.Store).filter(models.Store.is_active == True).all()

@app.get("/api/v1/products/{product_id}/history")
async def get_product_history(product_id: int, db: Session = Depends(database.get_db)):
    history = db.query(models.Price).filter(
        models.Price.product_id == product_id
    ).order_by(models.Price.scraped_at.desc()).all()

    if not history:
        raise HTTPException(status_code=404, detail="Product history not found")

    return history

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class ShoppingListCreate(BaseModel):
    name: str
    items: List[dict]

@app.post("/api/v1/lists")
async def create_shopping_list(
    list_data: ShoppingListCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_list = models.ShoppingList(
        user_id=current_user.id,
        name=list_data.name,
        items=list_data.items
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list

@app.get("/api/v1/lists")
async def get_shopping_lists(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.ShoppingList).filter(models.ShoppingList.user_id == current_user.id).all()
