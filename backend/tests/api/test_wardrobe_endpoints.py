"""API contract tests — health, upload, and wardrobe endpoints."""
from tests.api.conftest import upload_item


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["service"] == "Vestia"


class TestUpload:
    def test_upload_returns_analysis(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes)
        assert "clothing_item_id" in body
        assert body["category"] in ["topwear", "bottomwear", "footwear", "accessory", "outerwear"]
        assert "confidence" in body
        assert "needs_review" in body

    def test_upload_with_overrides(self, client, sample_image_bytes):
        body = upload_item(
            client, sample_image_bytes,
            category="topwear", subcategory="oxford shirt",
            style="formal", season="winter",
        )
        assert body["category"] == "topwear"
        assert body["subcategory"] == "oxford shirt"
        assert body["style"] == "formal"
        assert body["season"] == "winter"

    def test_upload_rejects_bad_mime_type(self, client):
        files = {"file": ("note.txt", b"not an image", "text/plain")}
        resp = client.post("/api/v1/upload", files=files)
        assert resp.status_code == 415

    def test_uploaded_item_appears_in_wardrobe(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", style="casual")
        resp = client.get("/api/v1/wardrobe")
        assert resp.status_code == 200
        ids = [item["id"] for item in resp.json()]
        assert body["clothing_item_id"] in ids


class TestWardrobeCRUD:
    def test_list_empty_wardrobe(self, client):
        resp = client.get("/api/v1/wardrobe")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_filters_by_category(self, client, sample_image_bytes):
        upload_item(client, sample_image_bytes, category="topwear", style="casual")
        upload_item(client, sample_image_bytes, category="footwear", style="casual")

        resp = client.get("/api/v1/wardrobe", params={"category": "topwear"})
        assert resp.status_code == 200
        assert all(item["category"] == "topwear" for item in resp.json())

    def test_get_single_item(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", style="casual")
        item_id = body["clothing_item_id"]

        resp = client.get(f"/api/v1/wardrobe/{item_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == item_id

    def test_get_nonexistent_item_404(self, client):
        resp = client.get("/api/v1/wardrobe/99999")
        assert resp.status_code == 404

    def test_patch_item_updates_fields(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", style="casual")
        item_id = body["clothing_item_id"]

        resp = client.patch(f"/api/v1/wardrobe/{item_id}", json={"style": "formal"})
        assert resp.status_code == 200
        assert resp.json()["style"] == "formal"

    def test_patch_nonexistent_item_404(self, client):
        resp = client.patch("/api/v1/wardrobe/99999", json={"style": "formal"})
        assert resp.status_code == 404

    def test_delete_item_soft_deletes(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", style="casual")
        item_id = body["clothing_item_id"]

        resp = client.delete(f"/api/v1/wardrobe/{item_id}")
        assert resp.status_code == 204

        # Soft-deleted items don't appear in the default (active) listing
        resp = client.get("/api/v1/wardrobe")
        ids = [item["id"] for item in resp.json()]
        assert item_id not in ids

    def test_delete_nonexistent_item_404(self, client):
        resp = client.delete("/api/v1/wardrobe/99999")
        assert resp.status_code == 404


class TestWardrobeSimilarity:
    def test_similar_endpoint_returns_list(self, client, sample_image_bytes):
        body = upload_item(client, sample_image_bytes, category="topwear", style="casual")
        item_id = body["clothing_item_id"]

        resp = client.get(f"/api/v1/wardrobe/{item_id}/similar")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_clusters_endpoint_returns_dict(self, client, sample_image_bytes):
        for _ in range(3):
            upload_item(client, sample_image_bytes, category="topwear", style="casual")

        resp = client.get("/api/v1/wardrobe/clusters")
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)
