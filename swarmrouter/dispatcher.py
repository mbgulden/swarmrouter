"""
Topological Dispatcher for SwarmRouter.
Asynchronously dispatches tasks according to conflict-free execution waves,
wrapping each task in PrismaticHypervisor transaction boundaries.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from prismatic.hypervisor import PrismaticHypervisor
from swarmrouter.analyzer import ExecutionWave, LockScopeAnalyzer, RoutedTask

logger = logging.getLogger("swarmrouter.dispatcher")


class TopologicalDispatcher:
    """
    Orchestrates wave-based parallel dispatch across worker tasks.
    """

    def __init__(self, hypervisor: Optional[PrismaticHypervisor] = None):
        self.hypervisor = hypervisor or PrismaticHypervisor()

    async def dispatch_task(
        self,
        task: RoutedTask,
        worker_fn: Callable[[Any, RoutedTask], Any]
    ) -> Dict[str, Any]:
        """Dispatches an individual task inside an isolated hypervisor transaction."""
        primary_resource = task.resources[0] if task.resources else "file:default.py"
        
        async with self.hypervisor.transaction(
            resource=primary_resource,
            agent_id=task.agent_id,
            mode=task.mode,
            task_id=task.task_id
        ) as tx:
            result = await worker_fn(tx, task) if asyncio.iscoroutinefunction(worker_fn) else worker_fn(tx, task)
            return {
                "task_id": task.task_id,
                "status": "COMPLETED",
                "result": result,
                "tx_id": tx.tx_id,
                "fence_token": tx.fence_token
            }

    async def dispatch_waves(
        self,
        tasks: List[RoutedTask],
        worker_fn: Callable[[Any, RoutedTask], Any]
    ) -> List[Dict[str, Any]]:
        """
        Computes waves and executes each wave in parallel, serializing across conflicting waves.
        """
        waves = LockScopeAnalyzer.schedule_waves(tasks)
        all_results: List[Dict[str, Any]] = []

        for wave in waves:
            logger.info("Executing Wave %d with %d tasks in parallel", wave.wave_index, len(wave.tasks))
            # Run all tasks in current wave concurrently
            tasks_coros = [self.dispatch_task(task, worker_fn) for task in wave.tasks]
            wave_results = await asyncio.gather(*tasks_coros)
            all_results.extend(wave_results)

        return all_results