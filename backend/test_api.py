"""
test_api.py — Backend tests for Asana Studio.
Run: python -m pytest backend/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, db_is_seeded, get_connection
from seed_poses import seed_database

# Initialize + seed DB before importing app (so lifespan isn't needed for tests)
init_db()
if not db_is_seeded():
    seed_database()

from main import app

client = TestClient(app)


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["poses_count"] >= 300


class TestPoses:
    def test_list_poses(self):
        r = client.get("/api/poses")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 300
        assert len(data["poses"]) > 0

    def test_search_pigeon(self):
        r = client.get("/api/poses?q=pigeon")
        data = r.json()
        assert data["total"] >= 5  # multiple pigeon variations
        names = [p["english_name"] for p in data["poses"]]
        assert any("Pigeon" in n for n in names)

    def test_filter_category(self):
        r = client.get("/api/poses?category=Inversion")
        data = r.json()
        assert all(p["category"] == "Inversion" for p in data["poses"])

    def test_filter_difficulty(self):
        r = client.get("/api/poses?difficulty=5")
        data = r.json()
        assert all(p["difficulty"] == 5 for p in data["poses"])

    def test_filter_tag(self):
        r = client.get("/api/poses?tag=backbend")
        data = r.json()
        assert data["total"] > 0

    def test_get_pose_detail(self):
        r = client.get("/api/poses/1")
        assert r.status_code == 200
        data = r.json()
        assert "english_name" in data
        assert "tags" in data

    def test_categories(self):
        r = client.get("/api/poses/categories")
        data = r.json()
        cats = [c["category"] for c in data]
        assert "Standing" in cats
        assert "Inversion" in cats

    def test_tags(self):
        r = client.get("/api/poses/tags")
        data = r.json()
        tags = [t["tag"] for t in data]
        assert "hip-opener" in tags
        assert "backbend" in tags


class TestSequences:
    def test_styles(self):
        r = client.get("/api/sequences/styles")
        data = r.json()
        assert len(data) >= 8
        style_ids = [s["id"] for s in data]
        assert "morning_flow" in style_ids

    def test_generate_sequence(self):
        r = client.post("/api/sequences/generate", json={
            "style": "morning_flow",
            "duration_minutes": 15,
            "difficulty": 3,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["total_poses"] >= 5
        assert len(data["poses"]) >= 5
        # Verify the sequence has poses with phase structure
        phases = set(p["phase"] for p in data["poses"])
        assert "warmup" in phases
        assert "peak" in phases or "cooldown" in phases

    def test_generate_all_styles(self):
        r = client.get("/api/sequences/styles")
        styles = r.json()
        for s in styles:
            r = client.post("/api/sequences/generate", json={
                "style": s["id"], "duration_minutes": 10, "difficulty": 3
            })
            assert r.status_code == 200

    def test_save_and_load(self):
        # Generate
        r = client.post("/api/sequences/generate", json={
            "style": "full_body", "duration_minutes": 10, "difficulty": 2
        })
        seq = r.json()

        # Save
        r = client.post("/api/sequences", json={
            "name": "Test Sequence",
            "style": "full_body",
            "difficulty": 2,
            "poses": [{"pose_id": p["pose_id"], "position": p["position"],
                       "side": p["side"], "hold_seconds": p["hold_seconds"]}
                      for p in seq["poses"]],
        })
        assert r.status_code == 200
        seq_id = r.json()["id"]

        # Load
        r = client.get(f"/api/sequences/{seq_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Test Sequence"
        assert len(data["poses"]) > 0


class TestPractices:
    def test_crud(self):
        # Create
        r = client.post("/api/practices", json={
            "name": "My Test Practice",
            "poses": [
                {"pose_id": 1, "position": 1, "side": "both", "hold_seconds": 30},
                {"pose_id": 2, "position": 2, "side": "both", "hold_seconds": 20},
            ],
        })
        assert r.status_code == 200
        pid = r.json()["id"]

        # Read
        r = client.get(f"/api/practices/{pid}")
        assert r.status_code == 200
        assert r.json()["name"] == "My Test Practice"
        assert len(r.json()["poses"]) == 2

        # Update
        r = client.put(f"/api/practices/{pid}", json={
            "name": "Updated Practice",
            "poses": [{"pose_id": 1, "position": 1, "side": "left", "hold_seconds": 45}],
        })
        assert r.status_code == 200

        # Verify update
        r = client.get(f"/api/practices/{pid}")
        assert r.json()["name"] == "Updated Practice"
        assert len(r.json()["poses"]) == 1

        # Delete
        r = client.delete(f"/api/practices/{pid}")
        assert r.status_code == 200

        # Verify delete
        r = client.get(f"/api/practices/{pid}")
        assert r.status_code == 404
