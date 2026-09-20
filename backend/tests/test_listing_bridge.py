

def test_a_neighbourhood_never_costs_the_user_their_district():
    """
    Reported from the app: choosing Kırklareli + Lüleburgaz + Emirali came
    back filtered to Kırklareli alone.

    The cause was `?query_text=`, which searches listing TITLES rather than
    filtering by location — so the district and village, not being words in
    the titles, simply vanished. Dropping a district the user explicitly
    chose is worse than not applying a village.
    """
    from backend.services.listing_bridge import build_listing_links

    links = build_listing_links("Kırklareli", "Lüleburgaz", "arsa", detail="Emirali")

    assert links, "a micro-location must still produce links"
    for link in links:
        assert "kirklareli-luleburgaz" in link["url"], link
        # Never a title search, which is what lost the district.
        assert "query_text" not in link["url"], link
        # The finer location travels beside the link so the UI can say it
        # still has to be applied on the site.
        assert link["manual_filter"] == "Emirali"


def test_the_district_survives_whatever_the_micro_location_is():
    from backend.services.listing_bridge import build_listing_links

    for detail in ("Emirali", "Ceribaşı Köyü", "Cumhuriyet Mahallesi", "  spaced  "):
        for link in build_listing_links("Edirne", "Keşan", "arsa", detail=detail):
            assert "edirne-kesan" in link["url"], (detail, link)


def test_without_a_micro_location_nothing_claims_one():
    from backend.services.listing_bridge import build_listing_links

    for link in build_listing_links("Edirne", "Keşan", "arsa"):
        assert "manual_filter" not in link
