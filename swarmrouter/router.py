"""swarmrouter.router — Core SwarmRouter orchestrator."""

from __future__ import annotations

import uuid
from typing import Sequence

from .models import (
    AgentPersona,
    ModelTier,
    TaskRequest,
    RouteDecision,
    CostEstimate,
)
from .taxonomy import infer_domains, compute_complexity_score, infer_capabilities
from .budget import (
    DEFAULT_MODEL_CATALOG,
    estimate_cost,
    select_model_for_task,
)

# Standard default agent personas
DEFAULT_AGENT_PERSONAS: list[AgentPersona] = [
    AgentPersona(
        id="agy",
        name="Antigravity (AGY)",
        description="General-purpose fullstack coding, UI/UX design, research, and architecture.",
        domains=["frontend_ui", "architecture", "research", "general"],
        capabilities=["code_write", "terminal", "browser"],
        default_model_tier="gemini-flash",
    ),
    AgentPersona(
        id="ned-code",
        name="Ned Code",
        description="Python backend specialist, API endpoint design, and database services.",
        domains=["backend_api", "general"],
        capabilities=["code_write", "terminal"],
        default_model_tier="gemini-pro",
    ),
    AgentPersona(
        id="ned-infra",
        name="Ned Infra",
        description="Infrastructure, systemd units, Proxmox virtualization, and tunnels.",
        domains=["infrastructure"],
        capabilities=["terminal", "code_write"],
        default_model_tier="gemini-flash",
    ),
    AgentPersona(
        id="jules",
        name="Jules",
        description="Git operations, pull request reviews, rebases, and merge resolutions.",
        domains=["git_review"],
        capabilities=["code_write", "terminal"],
        default_model_tier="gemini-flash",
    ),
    AgentPersona(
        id="kai",
        name="Kai",
        description="Content, copywriting, SEO optimization, and user-facing docs.",
        domains=["research", "general"],
        capabilities=["code_write"],
        default_model_tier="gemini-flash",
    ),
    AgentPersona(
        id="fred",
        name="Fred",
        description="Multi-agent swarm orchestration, architecture decomposition, and planning.",
        domains=["architecture", "general"],
        capabilities=["code_write", "terminal"],
        default_model_tier="claude-sonnet",
    ),
]


class SwarmRouter:
    """Deterministic capability, token cost, and model routing engine."""

    def __init__(
        self,
        personas: Sequence[AgentPersona] | None = None,
        models: Sequence[ModelTier] | None = None,
    ) -> None:
        self.personas: dict[str, AgentPersona] = {
            p.id: p for p in (personas or DEFAULT_AGENT_PERSONAS)
        }
        self.models: dict[str, ModelTier] = {
            m.id: m for m in (models or DEFAULT_MODEL_CATALOG)
        }

    def register_agent(self, persona: AgentPersona) -> None:
        """Register a new persona or update an existing one."""
        self.personas[persona.id] = persona

    def register_model(self, model: ModelTier) -> None:
        """Register a new model tier or update pricing."""
        self.models[model.id] = model

    def list_agents(self) -> list[AgentPersona]:
        """Return all registered agent personas."""
        return list(self.personas.values())

    def list_models(self) -> list[ModelTier]:
        """Return all registered model tiers."""
        return list(self.models.values())

    def route(self, task_or_prompt: str | TaskRequest) -> RouteDecision:
        """Deterministically route a task or prompt to the optimal agent persona and model tier."""
        if isinstance(task_or_prompt, str):
            task = TaskRequest(
                id=f"task-{uuid.uuid4().hex[:8]}",
                prompt=task_or_prompt,
            )
        else:
            task = task_or_prompt

        # 1. Infer taxonomy & complexity
        domains = infer_domains(f"{task.title} {task.prompt}", task.labels)
        primary_domain = domains[0] if domains else "general"
        complexity = compute_complexity_score(task.prompt, task.title, task.labels)
        required_caps = list(set(task.required_capabilities) | set(infer_capabilities(task.prompt, task.labels)))

        # 2. Select matching agent persona
        suitable_agents: list[AgentPersona] = []
        for persona in self.personas.values():
            if not persona.is_available:
                continue
            if persona.can_handle(primary_domain, required_caps):
                suitable_agents.append(persona)

        if not suitable_agents:
            # Fallback to agy (general default) or first available persona
            chosen_agent = self.personas.get("agy") or list(self.personas.values())[0]
        else:
            # Prefer agent specialized in primary domain
            specialized = [a for a in suitable_agents if primary_domain in a.domains]
            chosen_agent = specialized[0] if specialized else suitable_agents[0]

        # 3. Model selection & cost optimization
        available_models = list(self.models.values())
        chosen_model, fallbacks = select_model_for_task(
            available_models=available_models,
            complexity_score=complexity,
            max_budget_usd=task.max_budget_usd,
            preferred_latency=task.preferred_latency,
            requires_gpu=task.requires_gpu,
            prompt_text=task.prompt,
        )

        cost_est = estimate_cost(task.prompt, chosen_model)

        # 4. Synthesize rationale
        rationale = (
            f"Mapped to agent '{chosen_agent.name}' for domain '{primary_domain}'. "
            f"Assigned '{chosen_model.name}' (complexity score {complexity}/10, est ${cost_est.total_cost_usd:.4f})."
        )

        return RouteDecision(
            task_id=task.id,
            agent_id=chosen_agent.id,
            agent_name=chosen_agent.name,
            model_tier=chosen_model.id,
            model_name=chosen_model.name,
            fallback_models=fallbacks,
            complexity_score=complexity,
            detected_domains=domains,
            cost_estimate=cost_est,
            rationale=rationale,
        )

    def estimate(
        self,
        prompt: str,
        model_id: str | None = None,
        expected_output_tokens: int = 1000,
    ) -> CostEstimate:
        """Estimate token count and cost for a given prompt and model."""
        target_model = self.models.get(model_id or "gemini-flash")
        if not target_model:
            raise KeyError(f"Unknown model tier: {model_id}")
        return estimate_cost(prompt, target_model, expected_output_tokens)
