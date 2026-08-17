"""examples/01_dynamic_task_router.py

Demonstrates how to use SwarmRouter to dynamically route tasks across specialized agent personas and model tiers.
"""

from swarmrouter import SwarmRouter, TaskRequest


def main() -> None:
    print("=" * 70)
    print("🧠 SwarmRouter Example: Dynamic Agent & Model Routing")
    print("=" * 70)

    router = SwarmRouter()

    sample_tasks = [
        TaskRequest(
            id="task-101",
            title="Update Landing Page Hero CTA",
            prompt="Change hero background gradient and add accessible primary button in index.html",
        ),
        TaskRequest(
            id="task-102",
            title="Implement User Auth Endpoint",
            prompt="Build a new FastAPI POST /api/v1/auth/token endpoint with PostgreSQL async session",
        ),
        TaskRequest(
            id="task-103",
            title="Setup Cloudflare Tunnel & Systemd Service",
            prompt="Configure cloudflared tunnel service unit on Ubuntu server for port 9000",
        ),
        TaskRequest(
            id="task-104",
            title="PR Review & Merge Conflict",
            prompt="Review pull request #42 diff on origin/main and resolve merge conflict in router.py",
        ),
        TaskRequest(
            id="task-105",
            title="Multi-Agent System Decomposition",
            prompt="Architectural redesign: Decompose monolithic 190KB dispatcher into decoupled microservices. Implement distributed transactional consensus and protocol fences.",
            labels=["agent:agy-opus", "priority:critical"],
        ),
    ]

    for task in sample_tasks:
        decision = router.route(task)
        print(f"\n📌 [{task.id}] {task.title}")
        print(f"   • Assigned Agent: {decision.agent_name} (`{decision.agent_id}`)")
        print(f"   • Model Tier:     {decision.model_name} (`{decision.model_tier}`)")
        print(f"   • Complexity:     {decision.complexity_score}/10")
        print(f"   • Domains:        {', '.join(decision.detected_domains)}")
        print(f"   • Est. Cost:      ${decision.cost_estimate.total_cost_usd:.5f} ({decision.cost_estimate.input_tokens} in / {decision.cost_estimate.output_tokens} out tokens)")
        print(f"   • Fallbacks:      {', '.join(decision.fallback_models[:3])}")
        print(f"   • Rationale:      {decision.rationale}")

    print("\n" + "=" * 70)
    print("✅ All tasks routed with deterministic capability and cost optimization!")
    print("=" * 70)


if __name__ == "__main__":
    main()
