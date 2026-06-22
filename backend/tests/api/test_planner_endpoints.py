"""API contract tests — weekly planner endpoint."""
from tests.api.conftest import upload_item


def _seed_varied_wardrobe(client, image_bytes):
    tops = [
        ("t-shirt", "casual"), ("polo", "smart_casual"), ("oxford shirt", "business_casual"),
    ]
    bottoms = [
        ("jeans", "casual"), ("chinos", "smart_casual"), ("formal trousers", "business_casual"),
    ]
    shoes = [
        ("sneakers", "casual"), ("loafers", "smart_casual"),
    ]
    for subcat, style in tops:
        upload_item(client, image_bytes, category="topwear", subcategory=subcat, style=style, season="all_season")
    for subcat, style in bottoms:
        upload_item(client, image_bytes, category="bottomwear", subcategory=subcat, style=style, season="all_season")
    for subcat, style in shoes:
        upload_item(client, image_bytes, category="footwear", subcategory=subcat, style=style, season="all_season")


class TestWeeklyPlan:
    def test_generates_seven_days(self, client, sample_image_bytes):
        _seed_varied_wardrobe(client, sample_image_bytes)

        resp = client.post("/api/v1/weekly-plan", json={
            "occasion": "casual", "season": "all_season",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["days"]) == 7
        assert [d["day"] for d in body["days"]] == [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        ]

    def test_coverage_is_full_with_sufficient_wardrobe(self, client, sample_image_bytes):
        _seed_varied_wardrobe(client, sample_image_bytes)

        resp = client.post("/api/v1/weekly-plan", json={
            "occasion": "casual", "season": "all_season",
        })
        body = resp.json()
        assert body["coverage"] == 1.0
        assert all(d["outfit"] is not None for d in body["days"])

    def test_consecutive_days_avoid_repeating_top_or_bottom(self, client, sample_image_bytes):
        _seed_varied_wardrobe(client, sample_image_bytes)

        resp = client.post("/api/v1/weekly-plan", json={
            "occasion": "casual", "season": "all_season",
        })
        days = resp.json()["days"]

        for i in range(len(days) - 1):
            today_items = {item["clothing_item"]["id"]: item["position"] for item in days[i]["outfit"]["items"]}
            tomorrow_items = {item["clothing_item"]["id"]: item["position"] for item in days[i + 1]["outfit"]["items"]}

            today_top = next((iid for iid, pos in today_items.items() if pos == "top"), None)
            today_bottom = next((iid for iid, pos in today_items.items() if pos == "bottom"), None)
            tomorrow_top = next((iid for iid, pos in tomorrow_items.items() if pos == "top"), None)
            tomorrow_bottom = next((iid for iid, pos in tomorrow_items.items() if pos == "bottom"), None)

            assert today_top != tomorrow_top, f"Day {i} and {i+1} repeat top item"
            assert today_bottom != tomorrow_bottom, f"Day {i} and {i+1} repeat bottom item"

    def test_day_overrides_applied(self, client, sample_image_bytes):
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="oxford shirt",    style="formal", season="all_season")
        upload_item(client, sample_image_bytes, category="bottomwear", subcategory="formal trousers", style="formal", season="all_season")
        upload_item(client, sample_image_bytes, category="footwear",   subcategory="formal shoes",    style="formal", season="all_season")
        upload_item(client, sample_image_bytes, category="outerwear",  subcategory="blazer",          style="formal", season="all_season")
        _seed_varied_wardrobe(client, sample_image_bytes)

        resp = client.post("/api/v1/weekly-plan", json={
            "occasion": "casual", "season": "all_season",
            "day_overrides": {"Friday": "formal_event"},
        })
        body = resp.json()
        friday = next(d for d in body["days"] if d["day"] == "Friday")
        assert friday["occasion"] == "formal_event"
        positions = {item["position"] for item in friday["outfit"]["items"]}
        assert "outerwear" in positions

    def test_insufficient_wardrobe_produces_notes(self, client, sample_image_bytes):
        # Only enough for formal_event (requires outerwear) — request casual is fine,
        # but formal_event without outerwear for an override day should note failure.
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="t-shirt", style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="bottomwear", subcategory="jeans",   style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="footwear",   subcategory="sneakers", style="casual", season="all_season")

        resp = client.post("/api/v1/weekly-plan", json={
            "occasion": "casual", "season": "all_season",
            "day_overrides": {"Monday": "formal_event"},  # no outerwear in wardrobe
        })
        body = resp.json()
        monday = next(d for d in body["days"] if d["day"] == "Monday")
        assert monday["outfit"] is None
        assert monday["note"] is not None
        assert body["coverage"] < 1.0
