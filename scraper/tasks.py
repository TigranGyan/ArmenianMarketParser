import asyncio
from celery_app import app
from scrapers.sas_scraper import SASScraper
from celery import shared_task

SCRAPER_REGISTRY = {
    "sas": SASScraper
}

@app.task(name="scraper.run_scraper")
def run_scraper(scraper_name: str, store_id: int):
    scraper_cls = SCRAPER_REGISTRY.get(scraper_name)
    if not scraper_cls:
        return f"Scraper {scraper_name} not found"

    scraper = scraper_cls(store_id=store_id)

    # Run async code in sync celery task
    loop = asyncio.get_event_loop()
    items = loop.run_until_complete(scraper.fetch_catalog())

    # Send items to price worker
    for item in items:
        # We use a separate worker for processing to keep scrapers fast
        app.send_task(
            "price_worker.process_item",
            args=[item.dict()],
            queue="price_updates"
        )

    return f"Scraped {len(items)} items from {scraper_name}"

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule SAS scraper every 30 minutes
    sender.add_periodic_task(1800.0, run_scraper.s("sas", 1), name="sas-every-30-min")
