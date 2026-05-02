def test_normalize_name():
    from price_worker.tasks import normalize_name
    assert normalize_name("  Marianna Milk 1L  ") == "marianna milk 1l"
    assert normalize_name("YOGURT ") == "yogurt"

def test_raw_item_model():
    from scraper.base import RawItem
    from datetime import datetime
    item = RawItem(
        name="Test",
        price=100.0,
        url="http://test.com",
        store_id=1,
        scraped_at=datetime.utcnow()
    )
    assert item.name == "Test"
    assert item.price == 100.0
