"""API contract tests — statistics endpoint."""
from tests.api.conftest import upload_item


class TestStatistics:
    def test_empty_wardrobe_stats(self, client):
        resp = client.get("/api/v1/statistics")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_items"] == 0
        assert body["active_items"] == 0
        assert body["category_breakdown"] == {}
        assert body["total_outfits_generated"] == 0
        assert body["total_outfits_worn"] == 0

    def test_stats_reflect_uploaded_items(self, client, sample_image_bytes):
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="t-shirt", style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="bottomwear", subcategory="jeans",   style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="polo",    style="smart_casual", season="all_season")

        resp = client.get("/api/v1/statistics")
        body = resp.json()
        assert body["active_items"] == 3
        assert body["category_breakdown"]["topwear"] == 2
        assert body["category_breakdown"]["bottomwear"] == 1
        assert body["style_breakdown"]["casual"] == 2
        assert body["style_breakdown"]["smart_casual"] == 1

    def test_stats_reflect_generated_and_worn_outfits(self, client, sample_image_bytes):
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="t-shirt", style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="polo",    style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="bottomwear", subcategory="jeans",   style="casual", season="all_season")
        upload_item(client, sample_image_bytes, category="footwear",   subcategory="sneakers", style="casual", season="all_season")

        gen = client.post("/api/v1/generate-outfit", json={"occasion": "casual", "season": "all_season", "count": 2})
        outfit_id = gen.json()[0]["id"]
        client.post(f"/api/v1/outfits/{outfit_id}/worn", json={"outfit_id": outfit_id})

        resp = client.get("/api/v1/statistics")
        body = resp.json()
        assert body["total_outfits_generated"] == 2
        assert body["total_outfits_worn"] == 1

    def test_soft_deleted_items_excluded_from_active_count(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", subcategory="t-shirt", style="casual", season="all_season")
        item_id = body["clothing_item_id"]
        client.delete(f"/api/v1/wardrobe/{item_id}")

        resp = client.get("/api/v1/statistics")
        stats = resp.json()
        assert stats["active_items"] == 0
        assert stats["total_items"] == 1   # inactive items still counted in total
