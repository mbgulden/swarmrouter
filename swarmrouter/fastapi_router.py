"""swarmrouter.fastapi_router — Drop-in FastAPI router module for SwarmRouter."""

from __future__ import annotations

from typing import Any, Dict

from .models import TaskRequest
from .router import SwarmRouter

try:
    from fastapi import APIRouter, Body, Depends, HTTPException
except ImportError:
    raise ImportError(
        "FastAPI is required for swarmrouter.fastapi_router. "
        "Install it with: pip install swarmrouter[fastapi]"
    )


def create_router(
    router_instance: SwarmRouter | None = None,
    auth_dependency: Any = None,
) -> APIRouter:
    """Create a FastAPI APIRouter exposing SwarmRouter endpoints."""
    engine = router_instance or SwarmRouter()

    dependencies = []
    if auth_dependency is not None:
        dependencies.append(Depends(auth_dependency))

    router = APIRouter(prefix="/router", tags=["SwarmRouter"], dependencies=dependencies)

    @router.get("/agents")
    def get_agents() -> Dict[str, Any]:
        """List all available agent personas."""
        return {"ok": True, "agents": [a.to_dict() for a in engine.list_agents()]}

    @router.get("/models")
    def get_models() -> Dict[str, Any]:
        """List all registered model tiers and pricing."""
        return {"ok": True, "models": [m.to_dict() for m in engine.list_models()]}

    @router.post("/route")
    def route_task(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        """Route a task to the optimal agent persona and model tier."""
        try:
            req = TaskRequest.from_dict(payload)
            decision = engine.route(req)
            return {"ok": True, "decision": decision.to_dict()}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/estimate")
    def estimate_tokens(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        """Estimate token cost for a prompt."""
        prompt = payload.get("prompt", "")
        model_id = payload.get("model_id", "gemini-flash")
        out_tokens = payload.get("expected_output_tokens", 1000)
        try:
            est = engine.estimate(prompt, model_id=model_id, expected_output_tokens=out_tokens)
            return {"ok": True, "estimate": est.to_dict()}
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Model tier not found: {model_id}")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return router


# Default router instance
router = create_router()
