"""tests/test_fastapi.py — Tests for SwarmRouter FastAPI router endpoints."""

import pytest
from swarmrouter.router import SwarmRouter

try:
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.testclient import TestClient
    from swarmrouter.fastapi_router import create_router
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
def test_fastapi_router_endpoints() -> None:
    engine = SwarmRouter()
    app = FastAPI()
    app.include_router(create_router(engine))

    client = TestClient(app)

    # 1. GET /router/agents
    res_agents = client.get("/router/agents")
    assert res_agents.status_code == 200
    assert len(res_agents.json()["agents"]) >= 5

    # 2. GET /router/models
    res_models = client.get("/router/models")
    assert res_models.status_code == 200
    assert len(res_models.json()["models"]) >= 4

    # 3. POST /router/route
    res_route = client.post("/router/route", json={
        "id": "task-api-1",
        "prompt": "Fix styling in dashboard.html navbar",
    })
    assert res_route.status_code == 200
    decision = res_route.json()["decision"]
    assert decision["agent_id"] == "agy"
    assert "frontend_ui" in decision["detected_domains"]

    # 4. POST /router/estimate
    res_est = client.post("/router/estimate", json={
        "prompt": "Some text for estimation",
        "model_id": "gemini-flash",
    })
    assert res_est.status_code == 200
    assert res_est.json()["estimate"]["total_cost_usd"] >= 0


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
def test_fastapi_router_auth_dependency() -> None:
    def verify_token(x_token: str = Header(...)):
        if x_token != "valid-secret":
            raise HTTPException(status_code=401, detail="Unauthorized")

    app = FastAPI()
    app.include_router(create_router(auth_dependency=verify_token))
    client = TestClient(app)

    # Unauthorized
    assert client.get("/router/agents").status_code in [401, 422]

    # Authorized
    res = client.get("/router/agents", headers={"x-token": "valid-secret"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
