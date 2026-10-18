"""
The serving layer, not the tables.

test_content_language_coverage.py holds the CATALOGUES: every market has
every language, and each block reads as the language it is filed under.
Nothing held the path from an HTTP request to those tables — and that path
is exactly where the reported bug lived. A reader on the German market with
a Turkish device was shown German prose, and every table-level test passed
while it happened, because the tables were never the problem: the market
was being used to pick the language.

So this file asks the question the user asked, through the API:

    user.market = DE, device says tr  ->  is the answer Turkish?

for all three markets, all three languages, every content endpoint. Market
and language are independent axes; this is the test that makes the SERVER
agree with that, not just the data.
"""
import pytest

from backend.tests.test_content_language_coverage import LANGS, MARKETS, _looks_like

ENDPOINTS = (
    "/planning/fund-facts",
    "/planning/gold-facts",
    "/planning/crypto-facts",
    "/planning/home-routes",
)


def _set_market(client, market: str) -> None:
    """Put the user on a market the way the app does, through its own API."""
    res = client.patch("/users/me/market", json={"market": market},
                       headers={"X-Lumos-Lang": "tr"})
    assert res.status_code in (200, 204), res.text


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("market", MARKETS)
@pytest.mark.parametrize("lang", LANGS)
def test_content_is_served_in_the_device_language_whatever_the_market(
    client, endpoint, market, lang
):
    _set_market(client, market)
    res = client.get(endpoint, headers={"X-Lumos-Lang": lang})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["market"] == market, (
        f"{endpoint} reported market {body['market']!r}, user is on {market!r}"
    )
    assert body["available"] is True, f"{endpoint} has nothing for {market}"

    items = body.get("facts") or body.get("routes")
    assert items, f"{endpoint} returned an empty list for {market}/{lang}"

    text = " ".join(f"{i['title']} {i['body']}" for i in items)
    assert _looks_like(text, lang), (
        f"{endpoint} on market {market} with device language {lang} served "
        f"prose that does not read as {lang}: {text[:140]!r}"
    )


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_an_unknown_device_language_falls_back_without_failing(client, endpoint):
    """
    An old client, or a language the backend does not speak, must still get
    a readable answer rather than an error or an empty card. The middleware
    falls back to Turkish; this proves the content path honours that instead
    of returning nothing.
    """
    _set_market(client, "TR")
    res = client.get(endpoint, headers={"X-Lumos-Lang": "fr"})
    assert res.status_code == 200, res.text
    items = res.json().get("facts") or res.json().get("routes")
    assert items, f"{endpoint} served nothing for an unsupported language"
    text = " ".join(f"{i['title']} {i['body']}" for i in items)
    assert _looks_like(text, "tr"), "unsupported language did not fall back to Turkish"
