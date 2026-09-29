"""SwarmRouter — Deterministic capability, token cost, and model routing kernel for AI agent swarms."""

from .budget import (
    DEFAULT_MODEL_CATALOG,
    estimate_cost,
    estimate_token_count,
    select_model_for_task,
)
from .models import (
    AgentPersona,
    CostEstimate,
    ModelTier,
    RouteDecision,
    TaskRequest,
)
from .router import (
    DEFAULT_AGENT_PERSONAS,
    SwarmRouter,
)
from .taxonomy import (
    compute_complexity_score,
    infer_capabilities,
    infer_domains,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_AGENT_PERSONAS",
    "DEFAULT_MODEL_CATALOG",
    "AgentPersona",
    "CostEstimate",
    "ModelTier",
    "RouteDecision",
    "SwarmRouter",
    "TaskRequest",
    "compute_complexity_score",
    "estimate_cost",
    "estimate_token_count",
    "infer_capabilities",
    "infer_domains",
    "select_model_for_task",
]
