"""API contract tests — outfit endpoints."""
from tests.api.conftest import upload_item


def _seed_casual_wardrobe(client, image_bytes):
    upload_item(client, image_bytes, category="topwear",    subcategory="t-shirt", style="casual", season="all_season")
    upload_item(client, image_bytes, category="bottomwear", subcategory="jeans",   style="casual", season="all_season")
    upload_item(client, image_bytes, category="footwear",   subcategory="sneakers", style="casual", season="all_season")


class TestGenerateOutfit:
    def test_generate_returns_outfits(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)

        resp = client.post("/api/v1/generate-outfit", json={
            "occasion": "casual", "season": "all_season", "count": 1,
        })
        assert resp.status_code == 201
        body = resp.json()
        assert len(body) == 1
        outfit = body[0]
        assert "scores" in outfit
        assert set(outfit["scores"].keys()) == {
            "total_score", "color_score", "style_score",
            "occasion_score", "season_score", "repetition_score",
        }
        positions = {item["position"] for item in outfit["items"]}
        assert {"top", "bottom", "shoes"}.issubset(positions)

    def test_generate_with_empty_wardrobe_422(self, client):
        resp = client.post("/api/v1/generate-outfit", json={
            "occasion": "casual", "season": "all_season", "count": 1,
        })
        assert resp.status_code == 422

    def test_generate_unknown_occasion_422(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)
        resp = client.post("/api/v1/generate-outfit", json={
            "occasion": "not_a_real_occasion", "season": "all_season", "count": 1,
        })
        assert resp.status_code == 422

    def test_generate_formal_event_requires_outerwear(self, client, sample_image_bytes):
        upload_item(client, sample_image_bytes, category="topwear",    subcategory="oxford shirt",    style="formal", season="all_season")
        upload_item(client, sample_image_bytes, category="bottomwear", subcategory="formal trousers", style="formal", season="all_season")
        upload_item(client, sample_image_bytes, category="footwear",   subcategory="formal shoes",    style="formal", season="all_season")

        resp = client.post("/api/v1/generate-outfit", json={
            "occasion": "formal_event", "season": "all_season", "count": 1,
        })
        assert resp.status_code == 422
        assert "outerwear" in resp.json()["detail"]


class TestOutfitLifecycle:
    def test_list_outfits(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)
        client.post("/api/v1/generate-outfit", json={"occasion": "casual", "season": "all_season", "count": 2})

        resp = client.get("/api/v1/outfits")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_outfit_by_id(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)
        gen = client.post("/api/v1/generate-outfit", json={"occasion": "casual", "season": "all_season", "count": 1})
        outfit_id = gen.json()[0]["id"]

        resp = client.get(f"/api/v1/outfits/{outfit_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == outfit_id

    def test_get_outfit_404(self, client):
        resp = client.get("/api/v1/outfits/99999")
        assert resp.status_code == 404

    def test_mark_outfit_worn(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)
        gen = client.post("/api/v1/generate-outfit", json={"occasion": "casual", "season": "all_season", "count": 1})
        outfit_id = gen.json()[0]["id"]

        resp = client.post(f"/api/v1/outfits/{outfit_id}/worn", json={"outfit_id": outfit_id, "notes": "Felt great"})
        assert resp.status_code == 204

        # wear_count should increment on the underlying items
        item_ids = [oi["clothing_item"]["id"] for oi in gen.json()[0]["items"]]
        for item_id in item_ids:
            item = client.get(f"/api/v1/wardrobe/{item_id}").json()
            assert item["wear_count"] == 1

    def test_delete_outfit(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)
        gen = client.post("/api/v1/generate-outfit", json={"occasion": "casual", "season": "all_season", "count": 1})
        outfit_id = gen.json()[0]["id"]

        resp = client.delete(f"/api/v1/outfits/{outfit_id}")
        assert resp.status_code == 204

        resp = client.get(f"/api/v1/outfits/{outfit_id}")
        assert resp.status_code == 404

    def test_delete_outfit_404(self, client):
        resp = client.delete("/api/v1/outfits/99999")
        assert resp.status_code == 404


class TestRecommendations:
    def test_recommendations_returns_outfits(self, client, sample_image_bytes):
        _seed_casual_wardrobe(client, sample_image_bytes)

        resp = client.get("/api/v1/recommendations", params={
            "occasion": "casual", "season": "all_season", "count": 2,
        })
        assert resp.status_code == 200
        assert len(resp.json()) <= 2

    def test_recommendations_missing_required_params_422(self, client):
        resp = client.get("/api/v1/recommendations")
        assert resp.status_code == 422
