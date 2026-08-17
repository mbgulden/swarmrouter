"""swarmrouter.models — Data contracts for SwarmRouter."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal


@dataclass
class ModelTier:
    """Specification and pricing for an LLM model tier."""
    id: str
    name: str
    provider: str  # e.g. "google", "anthropic", "openai", "local"
    input_cost_per_1m: float  # in USD
    output_cost_per_1m: float  # in USD
    max_context_tokens: int = 1_000_000
    latency_tier: Literal["low", "medium", "high"] = "low"
    reasoning_score: int = 5  # 1 to 10 scale
    supports_tools: bool = True
    supports_vision: bool = True
    supports_gpu: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelTier:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AgentPersona:
    """Specification for an AI agent persona and its specialization."""
    id: str
    name: str
    description: str
    domains: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    default_model_tier: str = "gemini-flash"
    max_concurrent: int = 4
    current_load: int = 0
    requires_gpu: bool = False

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.max_concurrent - self.current_load)

    @property
    def is_available(self) -> bool:
        return self.remaining_capacity > 0

    def can_handle(self, domain: str, capabilities: list[str]) -> bool:
        """Verify persona matches requested domain and capabilities."""
        if domain and self.domains and domain not in self.domains and "general" not in self.domains:
            return False
        for cap in capabilities:
            if cap not in self.capabilities:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["remaining_capacity"] = self.remaining_capacity
        d["is_available"] = self.is_available
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentPersona:
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


@dataclass
class TaskRequest:
    """Normalized request for routing a prompt or Linear issue."""
    id: str
    prompt: str
    title: str = ""
    labels: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    max_budget_usd: float | None = None
    preferred_latency: Literal["low", "medium", "high"] = "low"
    requires_gpu: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskRequest:
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


@dataclass
class CostEstimate:
    """Pre-dispatch token cost estimation."""
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    model_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CostEstimate:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RouteDecision:
    """Deterministic routing decision output."""
    task_id: str
    agent_id: str
    agent_name: str
    model_tier: str
    model_name: str
    fallback_models: list[str]
    complexity_score: int
    detected_domains: list[str]
    cost_estimate: CostEstimate
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cost_estimate"] = self.cost_estimate.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RouteDecision:
        cost_data = data.get("cost_estimate", {})
        cost_est = CostEstimate.from_dict(cost_data) if isinstance(cost_data, dict) else cost_data
        return cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            model_tier=data["model_tier"],
            model_name=data["model_name"],
            fallback_models=data.get("fallback_models", []),
            complexity_score=data.get("complexity_score", 1),
            detected_domains=data.get("detected_domains", []),
            cost_estimate=cost_est,
            rationale=data.get("rationale", ""),
        )
