"""
Integration tests for Experience Vault CRUD endpoints and Resume template switching.
"""

from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_vault_get():
    response = client.get("/api/v1/ingest/vault")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "nodes" in data
    assert "skills" in data
    assert "projects" in data


def test_vault_experience_node_crud():
    # 1. Create
    create_payload = {
        "company": "Test Innovators Inc",
        "role": "Staff Platform Engineer",
        "duration": "2025 - Present",
        "raw_text": "Architected low-latency microservices handling 250k RPS.",
        "tags": ["Kubernetes", "gRPC", "Go"],
    }
    create_res = client.post("/api/v1/ingest/nodes", json=create_payload)
    assert create_res.status_code == 200
    node = create_res.json()
    node_id = node["id"]
    assert node["company"] == "Test Innovators Inc"
    assert node["role"] == "Staff Platform Engineer"

    # 2. Update
    update_payload = {
        "raw_text": "Architected distributed low-latency microservices handling 500k RPS.",
        "tags": ["Kubernetes", "gRPC", "Go", "Kafka"],
    }
    update_res = client.put(f"/api/v1/ingest/nodes/{node_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_node = update_res.json()
    assert "500k RPS" in updated_node["raw_text"]
    assert "Kafka" in updated_node["tags"]

    # 3. Delete
    delete_res = client.delete(f"/api/v1/ingest/nodes/{node_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"


def test_vault_skill_crud():
    # 1. Create skill
    create_res = client.post(
        "/api/v1/ingest/skills",
        json={"skill_name": "Distributed Consensus", "category": "Core Architecture"},
    )
    assert create_res.status_code == 200
    skill = create_res.json()
    skill_id = skill["id"]
    assert skill["skill_name"] == "Distributed Consensus"

    # 2. Delete skill
    delete_res = client.delete(f"/api/v1/ingest/skills/{skill_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"


def test_vault_project_crud():
    # 1. Create project
    create_res = client.post(
        "/api/v1/ingest/projects",
        json={
            "name": "Global Vector Cache",
            "description": "Multi-region tiered cache for dense vector embeddings.",
            "tags": ["Redis", "Rust", "VectorDB"],
        },
    )
    assert create_res.status_code == 200
    proj = create_res.json()
    proj_id = proj["id"]
    assert proj["name"] == "Global Vector Cache"

    # 2. Update project
    update_res = client.put(
        f"/api/v1/ingest/projects/{proj_id}",
        json={"name": "Global Distributed Vector Cache"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Global Distributed Vector Cache"

    # 3. Delete project
    delete_res = client.delete(f"/api/v1/ingest/projects/{proj_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"
