"""tests/test_taxonomy.py — Tests for domain inference and complexity scoring."""

from swarmrouter.taxonomy import (
    infer_domains,
    compute_complexity_score,
    infer_capabilities,
)


def test_infer_domains_frontend() -> None:
    domains = infer_domains("Update button colors in dashboard.html and add CSS modal")
    assert "frontend_ui" in domains


def test_infer_domains_backend() -> None:
    domains = infer_domains("Add FastAPI POST /api/v1/auth endpoint with database query")
    assert "backend_api" in domains


def test_infer_domains_infrastructure() -> None:
    domains = infer_domains("Configure systemd service unit and Cloudflare tunnel on Ubuntu")
    assert "infrastructure" in domains


def test_infer_domains_explicit_label() -> None:
    domains = infer_domains("Generic task", labels=["domain:git_review"])
    assert "git_review" in domains


def test_compute_complexity_scoring() -> None:
    # 1. Simple 1-liner
    simple_score = compute_complexity_score("Fix typo in comment", labels=["agent:agy-flash-high"])
    assert simple_score <= 2

    # 2. Deep architectural refactor
    arch_prompt = """
    Refactor the monolithic dispatcher into decoupled microservices.
    Implement distributed transactional locking with cryptographic signatures.
    Eliminate race conditions and verify fault-tolerant failover protocols.
    ```python
    def migrate():
        pass
    ```
    """
    arch_score = compute_complexity_score(arch_prompt, labels=["agent:agy-opus", "priority:critical"])
    assert arch_score >= 8


def test_infer_capabilities() -> None:
    caps = infer_capabilities("Write python script to run playwright browser tests")
    assert "code_write" in caps
    assert "browser" in caps
    assert "terminal" in caps
