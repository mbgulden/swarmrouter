"""swarmrouter.cli — Command-line interface for SwarmRouter."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .models import TaskRequest
from .router import SwarmRouter


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="swarmrouter",
        description="SwarmRouter — Capability, Cost & Model Routing Engine",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # route
    route_cmd = sub.add_parser("route", help="Route a prompt or task to the optimal agent and model")
    route_cmd.add_argument("prompt", help="Prompt text or task description to evaluate")
    route_cmd.add_argument("--title", default="", help="Task or Linear issue title")
    route_cmd.add_argument("--id", default="cli-task", dest="task_id", help="Task identifier")
    route_cmd.add_argument("--budget", type=float, default=None, dest="max_budget", help="Maximum budget ceiling in USD")
    route_cmd.add_argument("--labels", default="", help="Comma-separated labels (e.g. 'domain:infra,complexity:high')")
    route_cmd.add_argument("--latency", choices=["low", "medium", "high"], default="low", help="Preferred latency tier")

    # estimate
    est_cmd = sub.add_parser("estimate", help="Calculate token count and estimated cost for a prompt")
    est_cmd.add_argument("prompt", help="Prompt text to calculate")
    est_cmd.add_argument("--model", default="gemini-flash", help="Target model tier ID (default: gemini-flash)")
    est_cmd.add_argument("--output-tokens", type=int, default=1000, help="Projected output token length (default: 1000)")

    # list-models
    sub.add_parser("list-models", help="List all registered model tiers and pricing")

    # list-agents
    sub.add_parser("list-agents", help="List all registered agent personas and capabilities")

    args = parser.parse_args(argv)
    router = SwarmRouter()

    if args.cmd == "route":
        labels = [lbl.strip() for lbl in args.labels.split(",") if lbl.strip()]
        req = TaskRequest(
            id=args.task_id,
            prompt=args.prompt,
            title=args.title,
            labels=labels,
            max_budget_usd=args.max_budget,
            preferred_latency=args.latency,
        )
        decision = router.route(req)
        print(json.dumps(decision.to_dict(), indent=2, sort_keys=True))
        return 0

    if args.cmd == "estimate":
        try:
            est = router.estimate(args.prompt, model_id=args.model, expected_output_tokens=args.output_tokens)
            print(json.dumps(est.to_dict(), indent=2, sort_keys=True))
            return 0
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if args.cmd == "list-models":
        models = [m.to_dict() for m in router.list_models()]
        print(json.dumps(models, indent=2, sort_keys=True))
        return 0

    if args.cmd == "list-agents":
        agents = [a.to_dict() for a in router.list_agents()]
        print(json.dumps(agents, indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
