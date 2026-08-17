"""swarmrouter.budget — Model pricing catalog, token estimation, and cost capping policies."""

from __future__ import annotations

from typing import Sequence
from .models import ModelTier, CostEstimate

# Standard default model tier catalog
DEFAULT_MODEL_CATALOG: list[ModelTier] = [
    ModelTier(
        id="gemini-flash",
        name="Gemini 2.0 Flash",
        provider="google",
        input_cost_per_1m=0.075,
        output_cost_per_1m=0.30,
        max_context_tokens=1_000_000,
        latency_tier="low",
        reasoning_score=4,
    ),
    ModelTier(
        id="gemini-pro",
        name="Gemini 2.0 Pro",
        provider="google",
        input_cost_per_1m=1.25,
        output_cost_per_1m=5.00,
        max_context_tokens=2_000_000,
        latency_tier="medium",
        reasoning_score=8,
    ),
    ModelTier(
        id="claude-sonnet",
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        max_context_tokens=200_000,
        latency_tier="medium",
        reasoning_score=8,
    ),
    ModelTier(
        id="claude-opus",
        name="Claude 3.7 Opus",
        provider="anthropic",
        input_cost_per_1m=15.00,
        output_cost_per_1m=75.00,
        max_context_tokens=200_000,
        latency_tier="high",
        reasoning_score=10,
    ),
    ModelTier(
        id="local-70b",
        name="Llama 3.3 70B (Local GPU)",
        provider="local",
        input_cost_per_1m=0.0,
        output_cost_per_1m=0.0,
        max_context_tokens=128_000,
        latency_tier="medium",
        reasoning_score=7,
        supports_gpu=True,
    ),
]


def estimate_token_count(text: str) -> int:
    """Estimate token count from character length using standard 4 chars/token heuristic."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_cost(
    prompt: str,
    model: ModelTier,
    expected_output_tokens: int = 1000,
) -> CostEstimate:
    """Calculate projected token count and cost in USD for a dispatch."""
    in_tokens = estimate_token_count(prompt)
    out_tokens = expected_output_tokens

    in_cost = (in_tokens / 1_000_000) * model.input_cost_per_1m
    out_cost = (out_tokens / 1_000_000) * model.output_cost_per_1m
    total_cost = in_cost + out_cost

    return CostEstimate(
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        input_cost_usd=round(in_cost, 6),
        output_cost_usd=round(out_cost, 6),
        total_cost_usd=round(total_cost, 6),
        model_id=model.id,
    )


def select_model_for_task(
    available_models: Sequence[ModelTier],
    complexity_score: int,
    max_budget_usd: float | None = None,
    preferred_latency: str = "low",
    requires_gpu: bool = False,
    prompt_text: str = "",
) -> tuple[ModelTier, list[str]]:
    """Select the optimal primary model and fallback cascade based on complexity and cost budget."""
    # 1. Filter models by hardware requirements
    candidates = list(available_models)
    if requires_gpu:
        candidates = [m for m in candidates if m.supports_gpu] or candidates

    # 2. Match complexity to model reasoning capabilities:
    #    Score 1-3 -> Flash tier
    #    Score 4-7 -> Pro / Sonnet tier
    #    Score 8-10 -> Opus tier
    if complexity_score <= 3:
        target_reasoning_min = 1
        target_reasoning_max = 6
    elif complexity_score <= 7:
        target_reasoning_min = 6
        target_reasoning_max = 9
    else:
        target_reasoning_min = 9
        target_reasoning_max = 10

    suitable = [m for m in candidates if target_reasoning_min <= m.reasoning_score <= target_reasoning_max]
    if not suitable:
        suitable = sorted(candidates, key=lambda m: abs(m.reasoning_score - complexity_score))

    # 3. Apply budget cap fence
    if max_budget_usd is not None and max_budget_usd > 0:
        within_budget = []
        for m in suitable:
            est = estimate_cost(prompt_text, m)
            if est.total_cost_usd <= max_budget_usd:
                within_budget.append(m)
        if within_budget:
            suitable = within_budget
        else:
            # Fallback to the cheapest candidate overall
            suitable = sorted(candidates, key=lambda m: estimate_cost(prompt_text, m).total_cost_usd)

    # 4. Latency preference sorting
    if preferred_latency == "low":
        suitable.sort(key=lambda m: (0 if m.latency_tier == "low" else (1 if m.latency_tier == "medium" else 2)))

    primary = suitable[0] if suitable else candidates[0]
    
    # 5. Build fallback sequence (excluding primary)
    fallbacks = [m.id for m in candidates if m.id != primary.id]

    return primary, fallbacks
