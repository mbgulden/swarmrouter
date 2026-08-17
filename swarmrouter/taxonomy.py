"""swarmrouter.taxonomy — Domain classification, complexity scoring, and capability matching."""

from __future__ import annotations

import re
from typing import Sequence

# Domain keyword markers
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "frontend_ui": [
        "html", "css", "ui", "ux", "tailwind", "component", "react", "dashboard",
        "layout", "frontend", "dom", "modal", "animation", "responsive", "navbar",
    ],
    "backend_api": [
        "fastapi", "endpoint", "server", "router", "route", "database", "sql",
        "orm", "async", "backend", "api", "rest", "json", "handler", "payload",
    ],
    "infrastructure": [
        "systemd", "proxmox", "pve", "tunnel", "cloudflare", "docker", "vm",
        "container", "port", "nginx", "caddy", "linux", "ubuntu", "server",
    ],
    "git_review": [
        "pr", "pull request", "review", "rebase", "merge", "git", "conflict",
        "diff", "patch", "cherry-pick",
    ],
    "architecture": [
        "refactor", "system design", "decomposition", "monolith", "decoupling",
        "contract", "kernel", "protocol", "architecture", "modularize",
    ],
    "research": [
        "benchmark", "audit", "report", "evaluation", "survey", "trajectory",
        "investigate", "compare", "analysis",
    ],
}

ARCHITECTURAL_KEYWORDS = [
    "refactor", "migrate", "security", "adversarial", "decompose", "protocol",
    "locking", "concurrency", "distributed", "race condition", "cryptographic",
    "deadlock", "transactional", "fault-tolerant",
]

LOW_COMPLEXITY_KEYWORDS = [
    "typo", "alias", "css class", "rename", "1-line", "quick fix", "docstring",
    "comment", "bump version", "minor",
]


def infer_domains(text: str, labels: Sequence[str] = ()) -> list[str]:
    """Detect functional domains from prompt text and labels, ranked by match density."""
    normalized_text = text.lower()
    explicit_domains: list[str] = []

    # 1. Explicit label tags take highest priority
    for label in labels:
        lbl_lower = label.lower()
        if lbl_lower.startswith("domain:"):
            explicit_domains.append(lbl_lower.split(":", 1)[1].strip())

    if explicit_domains:
        return explicit_domains

    # 2. Count keyword hits per domain
    domain_scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", normalized_text))
        if score > 0:
            domain_scores[domain] = score

    if not domain_scores:
        return ["general"]

    # Sort domains by hit count descending
    ranked = sorted(domain_scores.keys(), key=lambda d: domain_scores[d], reverse=True)
    return ranked


def compute_complexity_score(prompt: str, title: str = "", labels: Sequence[str] = ()) -> int:
    """Compute a deterministic complexity score from 1 (simple) to 10 (architectural)."""
    full_text = f"{title}\n{prompt}".lower()
    score = 2  # base standard score

    # 1. Text length heuristic
    length = len(prompt)
    if length > 5000:
        score += 3
    elif length > 1500:
        score += 2
    elif length > 400:
        score += 1

    # 2. Structural density (code blocks, bullet lists, JSON snippets)
    if "```" in prompt:
        score += 1
    if "{" in prompt and "}" in prompt:
        score += 1

    # 3. Architectural / Hard problem keywords
    if any(re.search(rf"\b{re.escape(kw)}\b", full_text) for kw in ARCHITECTURAL_KEYWORDS):
        score += 2

    # 4. Low complexity keywords deduction
    if any(re.search(rf"\b{re.escape(kw)}\b", full_text) for kw in LOW_COMPLEXITY_KEYWORDS):
        score -= 2

    # 5. Explicit label influences
    for label in labels:
        lbl = label.lower()
        if "opus" in lbl or "deep" in lbl or "complex" in lbl or "priority:critical" in lbl:
            score += 3
        elif "thinking" in lbl or "pro" in lbl:
            score += 2
        elif "flash-high" in lbl or "trivial" in lbl or "low" in lbl:
            score -= 2

    # Clamp between 1 and 10
    return max(1, min(10, score))


def infer_capabilities(text: str, labels: Sequence[str] = ()) -> list[str]:
    """Extract required tool capabilities for a task."""
    full_text = f"{' '.join(labels)} {text}".lower()
    caps: set[str] = set()

    if any(k in full_text for k in ["code", "script", "file", "implement", "python", "bug", "write", "function", "class", "module"]):
        caps.add("code_write")
    if any(k in full_text for k in ["run", "command", "bash", "terminal", "wsl", "exec", "test", "build", "systemd", "server", "tunnel"]):
        caps.add("terminal")
    if any(k in full_text for k in ["browser", "web", "dom", "playwright", "puppeteer", "scrape"]):
        caps.add("browser")
    if any(k in full_text for k in ["cuda", "ollama", "vllm", "gpu", "vram"]):
        caps.add("gpu")

    return sorted(list(caps))
