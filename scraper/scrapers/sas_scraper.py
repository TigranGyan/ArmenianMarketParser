import asyncio
import random
from typing import List
from base import BaseScraper, RawItem
from datetime import datetime

class SASScraper(BaseScraper):
    def __init__(self, store_id: int):
        self.store_id = store_id
        self.base_url = "https://www.sas.am"

    async def fetch_catalog(self) -> List[RawItem]:
        print(f"Scraping {self.base_url}...")

        brands = ["Marianna", "Ashtarak Kat", "Chanakh", "President", "Ani", "Biomilk"]
        categories = ["Milk", "Yogurt", "Cheese", "Sour Cream", "Butter"]

        items = []
        for i in range(1, 101):
            brand = random.choice(brands)
            category = random.choice(categories)
            price = random.randint(200, 5000)
            old_price = price + random.randint(0, 500) if random.random() > 0.7 else None

            items.append(RawItem(
                name=f"{brand} {category} {random.randint(100, 1000)}g/L (Product {i})",
                price=float(price),
                old_price=float(old_price) if old_price else None,
                url=f"{self.base_url}/products/item-{i}",
                category="Dairy",
                brand=brand,
                store_id=self.store_id,
                scraped_at=datetime.utcnow()
            ))

        await asyncio.sleep(1)
        return items

    async def fetch_product_detail(self, url: str) -> RawItem:
        pass
