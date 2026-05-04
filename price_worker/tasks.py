import os
from datetime import datetime

from celery_app import app
from elasticsearch import Elasticsearch
from models import Price, Product, Store
from sqlalchemy import and_

from database import SessionLocal

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

def normalize_name(name: str) -> str:
    # Simple normalization: lowercase and strip
    # In production, this would be more complex (ML or fuzzy matching)
    return name.strip().lower()

@app.task(name="price_worker.process_item")
def process_item(item_data: dict):
    db = SessionLocal()
    try:
        raw_name = item_data["name"]
        normalized_name = normalize_name(raw_name)

        # 1. Find or create product
        product = db.query(Product).filter(Product.canonical_name == normalized_name).first()
        if not product:
            product = Product(
                canonical_name=normalized_name,
                brand=item_data.get("brand"),
                image_url=item_data.get("image_url"),
                attributes=item_data.get("attributes", {})
            )
            db.add(product)
            db.flush() # Get product.id

        # 2. Update price history
        # Close old price record if exists
        db.query(Price).filter(
            and_(
                Price.product_id == product.id,
                Price.store_id == item_data["store_id"],
                Price.valid_to == None
            )
        ).update({"valid_to": datetime.utcnow()})

        new_price = Price(
            product_id=product.id,
            store_id=item_data["store_id"],
            price=item_data["price"],
            old_price=item_data.get("old_price"),
            currency=item_data.get("currency", "AMD"),
            url=item_data["url"],
            scraped_at=item_data["scraped_at"],
            valid_from=datetime.utcnow()
        )
        db.add(new_price)
        db.commit()

        # 3. Update Elasticsearch index
        update_elasticsearch(db, product.id)

    except Exception as e:
        db.rollback()
        print(f"Error processing item: {e}")
    finally:
        db.close()

def update_elasticsearch(db, product_id):
    product = db.query(Product).get(product_id)
    if not product:
        return

    # Get all current prices for this product
    current_prices = db.query(Price, Store).join(Store).filter(
        and_(Price.product_id == product_id, Price.valid_to == None)
    ).all()

    prices_data = []
    min_price = None
    max_price = None

    for price, store in current_prices:
        p_val = float(price.price)
        if min_price is None or p_val < min_price:
            min_price = p_val
        if max_price is None or p_val > max_price:
            max_price = p_val

        prices_data.append({
            "store_id": store.id,
            "store_name": store.name,
            "price": p_val,
            "old_price": float(price.old_price) if price.old_price else None,
            "url": price.url,
            "scraped_at": price.scraped_at.isoformat()
        })

    doc = {
        "product_id": product.id,
        "canonical_name": product.canonical_name,
        "brand": product.brand,
        "attributes": product.attributes,
        "prices": prices_data,
        "min_price": min_price,
        "max_price": max_price,
        "stores_count": len(prices_data)
    }

    try:
        es.index(index="products_search", id=str(product.id), document=doc)
    except Exception as e:
        print(f"ES indexing error: {e}")
