"""
Lock Scope Analyzer for SwarmRouter.
Performs static analysis on task lists and required resource keys to group tasks into
maximally parallel disjoint execution waves vs serialized dependency chains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from swarmlock.hierarchy import LockMode, ResourceKey


@dataclass
class RoutedTask:
    task_id: str
    resources: List[str]
    mode: str = "X"  # "X" (Exclusive write) or "S" (Shared read)
    agent_id: str = "agent"
    payload: Dict[str, Any] = field(default_factory=dict)

    def get_resource_keys(self) -> List[ResourceKey]:
        return [ResourceKey.parse(r) for r in self.resources]


@dataclass
class ExecutionWave:
    wave_index: int
    tasks: List[RoutedTask] = field(default_factory=list)


class LockScopeAnalyzer:
    """
    Analyzes task resource contention and computes dependency waves.
    """

    @staticmethod
    def tasks_conflict(task_a: RoutedTask, task_b: RoutedTask) -> bool:
        """Determines if two tasks compete for overlapping exclusive lock scopes."""
        keys_a = task_a.get_resource_keys()
        keys_b = task_b.get_resource_keys()

        for ka in keys_a:
            for kb in keys_b:
                # Same resource or parent/child relationship
                is_overlap = (
                    ka.path == kb.path or
                    kb.path.startswith(ka.path.rstrip("/") + "/") or
                    ka.path.startswith(kb.path.rstrip("/") + "/")
                )
                if is_overlap:
                    # If either task requires Exclusive (X) lock, they conflict
                    if task_a.mode == "X" or task_b.mode == "X":
                        return True
        return False

    @classmethod
    def schedule_waves(cls, tasks: List[RoutedTask]) -> List[ExecutionWave]:
        """
        Greedily groups tasks into conflict-free parallel execution waves.
        Tasks in the same wave can be dispatched concurrently without lock contention.
        """
        waves: List[ExecutionWave] = []
        remaining_tasks = list(tasks)

        wave_idx = 0
        while remaining_tasks:
            current_wave_tasks: List[RoutedTask] = []
            next_remaining: List[RoutedTask] = []

            for task in remaining_tasks:
                # Check if this task conflicts with any task already placed in current wave
                has_conflict = any(cls.tasks_conflict(task, existing) for existing in current_wave_tasks)
                if not has_conflict:
                    current_wave_tasks.append(task)
                else:
                    next_remaining.append(task)

            waves.append(ExecutionWave(wave_index=wave_idx, tasks=current_wave_tasks))
            wave_idx += 1
            remaining_tasks = next_remaining

        return waves