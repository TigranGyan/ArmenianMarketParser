from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RawItem(BaseModel):
    name: str
    price: float
    old_price: Optional[float] = None
    currency: str = "AMD"
    url: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    store_id: int
    scraped_at: datetime = datetime.utcnow()

class BaseScraper(ABC):
    @abstractmethod
    async def fetch_catalog(self) -> List[RawItem]:
        pass

    @abstractmethod
    async def fetch_product_detail(self, url: str) -> RawItem:
        pass
