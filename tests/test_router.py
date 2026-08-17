"""tests/test_router.py — Tests for core SwarmRouter dispatch decisions."""

from swarmrouter.models import TaskRequest
from swarmrouter.router import SwarmRouter


def test_swarmrouter_routes_backend_task() -> None:
    router = SwarmRouter()
    
    decision = router.route(
        "Build a new FastAPI router endpoint with PostgreSQL async database query"
    )
    assert decision.agent_id == "ned-code"
    assert "backend_api" in decision.detected_domains
    assert decision.cost_estimate.total_cost_usd >= 0


def test_swarmrouter_routes_infra_task() -> None:
    router = SwarmRouter()
    
    decision = router.route(
        "Configure systemd service unit on Ubuntu server with Cloudflare tunnel"
    )
    assert decision.agent_id == "ned-infra"
    assert "infrastructure" in decision.detected_domains


def test_swarmrouter_routes_git_task() -> None:
    router = SwarmRouter()
    
    decision = router.route(
        "Review pull request diff and resolve merge conflict on origin/main"
    )
    assert decision.agent_id == "jules"
    assert "git_review" in decision.detected_domains


def test_swarmrouter_routes_deep_architecture_task() -> None:
    router = SwarmRouter()
    
    prompt = """
    Architectural redesign: Decompose monolithic 190KB dispatcher into decoupled microservices.
    Implement distributed transactional consensus and protocol fences.
    """
    req = TaskRequest(
        id="task-arch-1",
        prompt=prompt,
        labels=["agent:agy-opus", "priority:critical"],
    )
    decision = router.route(req)
    assert decision.complexity_score >= 8
    assert decision.model_tier in ["claude-opus", "gemini-pro"]
