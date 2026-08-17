# Changelog

All notable changes to SwarmRouter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-08-17

### Added
- Initial release of **SwarmRouter** (Linear [GRO-4773](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4773)).
- **Domain & Capability Taxonomy Engine** ([GRO-4774](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4774)):
  - Multi-domain task classification (`frontend_ui`, `backend_api`, `infrastructure`, `git_review`, `architecture`, `research`).
  - Complexity scoring engine ($1$ to $10$) evaluating prompt token density, code structures, and multi-file scopes.
  - Fail-closed tool capability matching (`AgentPersona.can_handle()`).
- **Token Budgeting & Cost Capping Policy** ([GRO-4775](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4775)):
  - Built-in pricing tables for major model tiers (Flash, Pro, Claude Sonnet/Opus, local 70B).
  - Pre-dispatch token estimation and cost calculation.
  - Strict budget expenditure ceilings and quota fallback cascades.
- **Multi-Modal Interfaces** ([GRO-4776](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4776)):
  - Zero-dependency Python API (`SwarmRouter`).
  - Full-featured CLI tool (`swarmrouter route`, `swarmrouter estimate`, `list-models`, `list-agents`).
  - Drop-in FastAPI router with pluggable authentication (`from swarmrouter.fastapi_router import create_router`).
- **Standardized Type Annotations & Packaging**:
  - PEP 561 `py.typed` marker for `mypy` and `pyright`.
  - Comprehensive unit test suite with 100% pass rate.
