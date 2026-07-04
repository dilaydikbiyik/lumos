"""
Calm news digest tests — RSS and AI mocked.
"""
from unittest.mock import patch

from backend.services.news_service import _parse_rss, get_daily_digest

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item><title>Merkez Bankası faiz kararını açıkladı</title><link>https://x/1</link></item>
  <item><title>BIST 100 günü yükselişle kapattı</title><link>https://x/2</link></item>
</channel></rss>"""

DIGEST_JSON = (
    '[{"headline": "Faiz kararı açıklandı", '
    '"why_it_matters": "Tahvil fonlarını etkileyebilir.", '
    '"calmness_note": "Panik gerektirmez."}]'
)


def test_parse_rss_extracts_titles():
    items = _parse_rss(SAMPLE_RSS)
    assert len(items) == 2
    assert items[0]["title"].startswith("Merkez Bankası")


def test_parse_rss_handles_garbage():
    assert _parse_rss("not xml at all") == []


def test_digest_flow_with_mocked_ai():
    with patch("backend.services.news_service.cache_service.get", return_value=None), \
         patch("backend.services.news_service.cache_service.set"), \
         patch("backend.services.news_service.fetch_headlines",
               return_value=[{"title": "Faiz kararı", "link": "x"}]), \
         patch("backend.services.news_service.generate_text", return_value=DIGEST_JSON):
        digest = get_daily_digest("stocks")
    assert len(digest) == 1
    assert digest[0]["calmness_note"] == "Panik gerektirmez."


def test_digest_bad_ai_output_returns_empty():
    with patch("backend.services.news_service.cache_service.get", return_value=None), \
         patch("backend.services.news_service.cache_service.set"), \
         patch("backend.services.news_service.fetch_headlines",
               return_value=[{"title": "Haber", "link": "x"}]), \
         patch("backend.services.news_service.generate_text", return_value="çöp çıktı"):
        assert get_daily_digest("stocks") == []


def test_digest_endpoint(client):
    with patch("backend.routers.news.get_daily_digest", return_value=[]):
        res = client.get("/news/digest")
    assert res.status_code == 200
    assert res.json()["items"] == []
