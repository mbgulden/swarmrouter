"""SwarmRouter — Deterministic capability, token cost, and model routing kernel for AI agent swarms."""

from .models import (
    ModelTier,
    AgentPersona,
    TaskRequest,
    RouteDecision,
    CostEstimate,
)
from .taxonomy import (
    infer_domains,
    compute_complexity_score,
    infer_capabilities,
)
from .budget import (
    DEFAULT_MODEL_CATALOG,
    estimate_token_count,
    estimate_cost,
    select_model_for_task,
)
from .router import (
    SwarmRouter,
    DEFAULT_AGENT_PERSONAS,
)

__version__ = "0.1.0"

__all__ = [
    "ModelTier",
    "AgentPersona",
    "TaskRequest",
    "RouteDecision",
    "CostEstimate",
    "SwarmRouter",
    "DEFAULT_MODEL_CATALOG",
    "DEFAULT_AGENT_PERSONAS",
    "infer_domains",
    "compute_complexity_score",
    "infer_capabilities",
    "estimate_token_count",
    "estimate_cost",
    "select_model_for_task",
]
