# 🧭 SwarmRouter

**Deterministic capability, token cost, and model routing kernel for AI agent swarms and microservices.**

[![PyPI](https://img.shields.io/pypi/v/swarmrouter.svg)](https://pypi.org/project/swarmrouter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Typing: Typed](https://img.shields.io/badge/Typing-Typed-blue.svg)](https://peps.python.org/pep-0561/)

---

## 🌟 What Sets SwarmRouter Apart

In multi-agent systems and microservices, dispatching every prompt to an over-powered reasoning model wastes immense budget, while sending complex architectural tasks to small models causes hallucination and task failures.

**SwarmRouter** provides a **zero-dependency, deterministic routing primitive** that analyzes task taxonomy, scores complexity (1–10), and enforces strict token budget ceilings before dispatch.

```
                   ┌──────────────────────────────────────┐
                   │             Incoming Task            │
                   │  Prompt / Description / Linear Issue │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │          Taxonomy Classifier         │
                   │  • Domain Detection (Code, UI, Infra)│
                   │  • Complexity Scoring (1-10)         │
                   │  • Capability Matching (GPU, Tools)  │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │          Cost & Budget Guard         │
                   │  • Token Budget Cap per Dispatch     │
                   │  • Pricing Table & Cost Estimation   │
                   │  • Quota & Latency Fallback Cascade  │
                   └──────────────────┬───────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │            RouteDecision             │
                   │  • Selected Agent (agy, ned, jules)  │
                   │  • Model Tier (flash, pro, opus)     │
                   │  • Estimated Cost & Token Allocation │
                   │  • Fallback Model Sequence           │
                   └──────────────────────────────────────┘
```

### Core Capabilities:
- 🚀 **Zero External Dependencies**: Pure Python 3.10+ standard library.
- 🎯 **Deterministic Complexity Scoring**: Analyzes token density, structural code markers, and architectural keywords to assign a 1–10 score.
- 💰 **Pre-Dispatch Cost Capping**: Enforces maximum budget ceilings (`max_budget_usd`), automatically downgrading or rejecting dispatches that exceed quotas.
- 🔄 **Automatic Fallback Cascades**: Pre-calculates an ordered fallback model sequence if the primary provider experiences quota exhaustion or latency degradation.
- 🌐 **Unified Interfaces**: Python API, command-line tool (`swarmrouter`), and drop-in FastAPI router.

---

## 💻 Installation

```bash
# Core package (zero dependencies)
pip install swarmrouter

# With optional FastAPI support
pip install swarmrouter[fastapi]
```

---

## ⚡ Quickstart

```python
from swarmrouter import SwarmRouter, TaskRequest

# 1. Initialize router
router = SwarmRouter()

# 2. Route a task
decision = router.route(TaskRequest(
    id="task-001",
    title="Build User Authentication Service",
    prompt="Create a new FastAPI router endpoint with async PostgreSQL database queries",
    max_budget_usd=0.01,
))

# 3. Inspect deterministic routing decision
print(f"Assigned Agent: {decision.agent_name} (`{decision.agent_id}`)")
print(f"Model Tier:     {decision.model_name} (`{decision.model_tier}`)")
print(f"Complexity:     {decision.complexity_score}/10")
print(f"Estimated Cost: ${decision.cost_estimate.total_cost_usd:.5f}")
print(f"Fallbacks:      {', '.join(decision.fallback_models)}")
```

---

## 🤖 Built-In Agent Personas

SwarmRouter includes standardized persona profiles calibrated for AI agent swarms:

| Agent Persona | Identifier | Specialization Domain | Required Capabilities | Default Model Tier |
|---|---|---|---|---|
| **Antigravity (AGY)** | `agy` | Frontend UI, Fullstack, Design | `code_write`, `terminal`, `browser` | Gemini 2.0 Flash |
| **Ned Code** | `ned-code` | Python Backend, APIs, Databases | `code_write`, `terminal` | Gemini 2.0 Pro |
| **Ned Infra** | `ned-infra` | Systemd, Virtualization, Tunnels | `terminal`, `code_write` | Gemini 2.0 Flash |
| **Jules** | `jules` | Git Reviews, Merges, Rebases | `code_write`, `terminal` | Gemini 2.0 Flash |
| **Kai** | `kai` | Copywriting, Content, SEO | `code_write` | Gemini 2.0 Flash |
| **Fred** | `fred` | Multi-Agent Swarm Orchestration | `code_write`, `terminal` | Claude 3.5 Sonnet |

---

## 📊 Default Model Pricing Catalog

| Model Tier | Provider | Input Cost / 1M | Output Cost / 1M | Max Context | Latency Tier |
|---|---|---|---|---|---|
| **Gemini 2.0 Flash** | Google | $0.075 | $0.30 | 1,000,000 | Low |
| **Gemini 2.0 Pro** | Google | $1.250 | $5.00 | 2,000,000 | Medium |
| **Claude 3.5 Sonnet** | Anthropic | $3.000 | $15.00 | 200,000 | Medium |
| **Claude 3.7 Opus** | Anthropic | $15.000 | $75.00 | 200,000 | High |
| **Llama 3.3 70B** | Local GPU | $0.000 | $0.00 | 128,000 | Medium |

---

## 🛠️ CLI Reference

SwarmRouter includes a terminal CLI:

```bash
# Route a prompt from the shell
swarmrouter route "Build a PostgreSQL database migration for users table" \
  --title "Database Migration" \
  --budget 0.05

# Calculate token count and estimated cost
swarmrouter estimate "Write a complete distributed consensus protocol" \
  --model claude-opus \
  --output-tokens 2000

# List all registered model tiers and pricing
swarmrouter list-models

# List all available agent personas
swarmrouter list-agents
```

---

## 🌐 FastAPI Integration

Mount the router to any FastAPI app with optional authentication:

```python
from fastapi import FastAPI, Header, HTTPException
from swarmrouter.fastapi_router import create_router

app = FastAPI(title="Agent Gateway")

def verify_token(x_token: str = Header(...)):
    if x_token != "secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")

app.include_router(
    create_router(auth_dependency=verify_token),
    prefix="/api",
)
```

Exposes:
- `GET /api/router/agents` — List available agent personas.
- `GET /api/router/models` — List registered model pricing and context limits.
- `POST /api/router/route` — Route a task to optimal agent & model tier.
- `POST /api/router/estimate` — Calculate token costs for a prompt.

---

## 📁 Repository Examples

Explore runnable examples in the [`examples/`](file:///c:/Users/Michael%20Gulden/Github/swarmrouter/examples) directory:

- [`01_dynamic_task_router.py`](file:///c:/Users/Michael%20Gulden/Github/swarmrouter/examples/01_dynamic_task_router.py) — Dynamic multi-agent routing across domains.
- [`02_cost_capped_dispatch.py`](file:///c:/Users/Michael%20Gulden/Github/swarmrouter/examples/02_cost_capped_dispatch.py) — Budget ceiling enforcement and fallback cascades.

---

## 📄 License

MIT License © 2026 Michael Gulden
