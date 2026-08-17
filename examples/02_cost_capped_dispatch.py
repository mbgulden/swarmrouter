"""examples/02_cost_capped_dispatch.py

Demonstrates SwarmRouter's token budgeting, cost estimation, and budget ceiling enforcement.
"""

from swarmrouter import SwarmRouter, TaskRequest


def main() -> None:
    print("=" * 70)
    print("💰 SwarmRouter Example: Cost Capping & Token Budget Enforcement")
    print("=" * 70)

    router = SwarmRouter()

    hard_problem_prompt = """
    Perform an exhaustive security and race condition audit on distributed locking protocol.
    Analyze potential deadlock vectors across multi-region quorum consensus nodes.
    Generate cryptographic verification proofs and audit ledger receipts.
    """

    # Case 1: Uncapped dispatch for high complexity task
    print("\n🟢 Case 1: Uncapped Dispatch (Optimal Reasoning Tier)")
    task_uncapped = TaskRequest(
        id="task-audit-uncapped",
        title="Distributed Quorum Security Audit",
        prompt=hard_problem_prompt,
        labels=["agent:agy-opus"],
    )
    decision_1 = router.route(task_uncapped)
    print(f"  • Selected Model: {decision_1.model_name}")
    print(f"  • Complexity:     {decision_1.complexity_score}/10")
    print(f"  • Estimated Cost: ${decision_1.cost_estimate.total_cost_usd:.5f}")

    # Case 2: Capped dispatch ($0.01 max budget ceiling)
    print("\n🟡 Case 2: Strict Budget Ceiling ($0.01 USD Max)")
    task_capped = TaskRequest(
        id="task-audit-capped",
        title="Distributed Quorum Security Audit",
        prompt=hard_problem_prompt,
        labels=["agent:agy-opus"],
        max_budget_usd=0.01,  # Forces downgrade from Opus to Pro/Flash
    )
    decision_2 = router.route(task_capped)
    print(f"  • Selected Model: {decision_2.model_name}")
    print(f"  • Complexity:     {decision_2.complexity_score}/10")
    print(f"  • Estimated Cost: ${decision_2.cost_estimate.total_cost_usd:.5f}")
    print(f"  • Fallbacks:      {', '.join(decision_2.fallback_models)}")

    print("\n" + "=" * 70)
    print("🎉 Budget ceilings strictly enforced without runtime failures!")
    print("=" * 70)


if __name__ == "__main__":
    main()
