"""tests/test_budget.py — Tests for token estimation and cost calculation."""

from swarmrouter.budget import (
    DEFAULT_MODEL_CATALOG,
    estimate_token_count,
    estimate_cost,
    select_model_for_task,
)
from swarmrouter.models import ModelTier


def test_estimate_token_count() -> None:
    text = "Hello world! This is a test prompt for token estimation."
    tokens = estimate_token_count(text)
    assert tokens > 0
    assert abs(tokens - (len(text) // 4)) <= 2


def test_estimate_cost() -> None:
    flash_model = next(m for m in DEFAULT_MODEL_CATALOG if m.id == "gemini-flash")
    prompt = "A" * 4000  # ~1000 input tokens
    cost = estimate_cost(prompt, flash_model, expected_output_tokens=1000)
    
    assert cost.input_tokens == 1000
    assert cost.output_tokens == 1000
    assert cost.total_cost_usd > 0
    assert cost.model_id == "gemini-flash"


def test_select_model_budget_cap_enforcement() -> None:
    # High complexity (score 9) would normally select Claude Opus ($15/$75)
    # But budget cap of $0.001 should force selection of Gemini Flash or cheaper
    primary, fallbacks = select_model_for_task(
        available_models=DEFAULT_MODEL_CATALOG,
        complexity_score=9,
        max_budget_usd=0.001,
        prompt_text="A" * 4000,
    )
    assert primary.id == "gemini-flash"
    assert "claude-opus" in fallbacks
