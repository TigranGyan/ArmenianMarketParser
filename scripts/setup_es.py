import os
import time
import subprocess
from elasticsearch import Elasticsearch

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

def setup_index():
    es = Elasticsearch(ES_URL)

    # Wait for ES to be ready
    for i in range(30):
        try:
            if es.ping():
                print("Elasticsearch is ready!")
                break
        except Exception as e:
            print(f"Waiting for Elasticsearch... ({e})")
            pass
        time.sleep(2)
    else:
        print("Elasticsearch not available")
        return

    mapping = {
        "mappings": {
            "properties": {
                "product_id": {"type": "integer"},
                "canonical_name": {
                    "type": "text",
                    "analyzer": "russian",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "brand": {"type": "text"},
                "category_name": {"type": "keyword"},
                "attributes": {"type": "object"},
                "ean": {"type": "keyword"},
                "prices": {
                    "type": "nested",
                    "properties": {
                        "store_id": {"type": "integer"},
                        "store_name": {"type": "keyword"},
                        "price": {"type": "scaled_float", "scaling_factor": 100},
                        "old_price": {"type": "scaled_float", "scaling_factor": 100},
                        "url": {"type": "keyword"},
                        "scraped_at": {"type": "date"}
                    }
                },
                "min_price": {"type": "float"},
                "max_price": {"type": "float"},
                "stores_count": {"type": "integer"}
            }
        }
    }

    if es.indices.exists(index="products_search"):
        print("Index products_search already exists")
    else:
        es.indices.create(index="products_search", body=mapping)
        print("Created index products_search")

if __name__ == "__main__":
    setup_index()
