import asyncio
import json
import logging
import re
from datetime import datetime
from typing import List

import httpx
from base import BaseScraper, RawItem
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SASScraper(BaseScraper):
    def __init__(self, store_id: int):
        self.store_id = store_id
        self.base_url = "https://www.sas.am"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": self.base_url
        }
        self.categories = [
            "/en/catalog/moloko/",
            "/en/catalog/syr/",
            "/en/catalog/smetana/",
            "/en/catalog/yogurty_i_slivki/",
            "/en/catalog/tvorozhnye_izdeliya/",
            "/en/catalog/yaytso/",
            "/en/catalog/slivochnoe_maslo/",
            "/en/catalog/myasnye_produkty/",
            "/en/catalog/frukty/",
            "/en/catalog/ovoshchi/"
        ]

    async def fetch_catalog(self) -> List[RawItem]:
        all_items = []
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0) as client:
            for cat_path in self.categories:
                url = f"{self.base_url}{cat_path}"
                try:
                    logger.info(f"Fetching category: {url}")
                    response = await client.get(url)
                    if response.status_code != 200:
                        logger.error(f"Failed to fetch {url}: {response.status_code}")
                        continue

                    items = self._parse_page(response.text, cat_path)
                    all_items.extend(items)
                    logger.info(f"Extracted {len(items)} items from {cat_path}")

                    # Be nice to the server
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")

        return all_items

    def _parse_page(self, html: str, category_name: str) -> List[RawItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []

        product_divs = soup.find_all("div", class_=re.compile(r"product js-product"))
        for div in product_divs:
            try:
                # Name
                name_div = div.find("div", class_="product__name")
                if not name_div:
                    continue
                name = name_div.get_text(strip=True)

                # URL
                link_tag = div.find("a", class_="product__images")
                if not link_tag or not link_tag.get("href"):
                    continue
                product_url = f"{self.base_url}{link_tag.get('href')}"

                # Price
                price_text_tag = div.find("span", class_="price__text")
                if not price_text_tag:
                    continue

                # Extract numeric price, handle things like "1 650 AMD"
                price_str = price_text_tag.get_text(strip=True)
                # Remove currency and non-breaking spaces
                price_val_str = re.sub(r"[^0-9]", "", price_str)
                if not price_val_str:
                    continue
                price = float(price_val_str)

                # Old Price (if exists)
                old_price = None
                old_price_tag = div.find("div", class_="price__old")
                if old_price_tag:
                    old_price_str = old_price_tag.get_text(strip=True)
                    old_price_val_str = re.sub(r"[^0-9]", "", old_price_str)
                    if old_price_val_str:
                        old_price = float(old_price_val_str)

                # Image
                image_url = None
                v_picture = div.find("v-picture")
                if v_picture and v_picture.get(":sources"):
                    try:
                        sources = json.loads(v_picture.get(":sources"))
                        image_path = sources.get("big") or sources.get("middle") or sources.get("small")
                        if image_path:
                            image_url = f"{self.base_url}{image_path}"
                    except json.JSONDecodeError:
                        pass

                # Category and Brand from name (simple heuristic)
                brand = None
                if '"' in name:
                    brand = name.split('"')[1]
                elif "''" in name:
                    brand = name.split("''")[1]

                items.append(RawItem(
                    name=name,
                    price=price,
                    old_price=old_price,
                    url=product_url,
                    image_url=image_url,
                    category=category_name.strip("/").split("/")[-1],
                    brand=brand,
                    store_id=self.store_id,
                    scraped_at=datetime.utcnow()
                ))
            except Exception as e:
                logger.error(f"Error parsing product div: {e}")
                continue

        return items

    async def fetch_product_detail(self, url: str) -> RawItem:
        # For now, we get everything from the catalog
        pass
