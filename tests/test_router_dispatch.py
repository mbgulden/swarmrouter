"""
Tests for SwarmRouter Static Lock-Scope Analysis and Wave Dispatching.
"""

import asyncio
import tempfile
import time
from pathlib import Path
import pytest

from prismatic.hypervisor import PrismaticHypervisor
from swarmrouter.analyzer import LockScopeAnalyzer, RoutedTask
from swarmrouter.dispatcher import TopologicalDispatcher


def test_lock_scope_analyzer_disjoint_vs_conflict():
    # 5 disjoint file tasks
    disjoint_tasks = [
        RoutedTask(task_id=f"task_{i}", resources=[f"file:src/module_{i}.py"], mode="X")
        for i in range(5)
    ]
    waves = LockScopeAnalyzer.schedule_waves(disjoint_tasks)
    # All 5 disjoint tasks should fit in a single parallel wave (Wave 0)
    assert len(waves) == 1
    assert len(waves[0].tasks) == 5

    # 2 conflicting tasks targeting the same file
    conflicting_tasks = [
        RoutedTask(task_id="task_a", resources=["file:src/auth.py"], mode="X"),
        RoutedTask(task_id="task_b", resources=["file:src/auth.py"], mode="X")
    ]
    waves_conflicting = LockScopeAnalyzer.schedule_waves(conflicting_tasks)
    # Must be split into 2 sequential waves
    assert len(waves_conflicting) == 2
    assert len(waves_conflicting[0].tasks) == 1
    assert len(waves_conflicting[1].tasks) == 1


def test_topological_dispatcher_parallel_execution():
    async def _run():
        with tempfile.TemporaryDirectory() as tmpdir:
            j_db = str(Path(tmpdir) / "journal.db")
            l_db = str(Path(tmpdir) / "ledger.db")
            hypervisor = PrismaticHypervisor(journal_db_path=j_db, ledger_db_path=l_db)
            dispatcher = TopologicalDispatcher(hypervisor=hypervisor)

            tasks = [
                RoutedTask(task_id=f"t_{i}", resources=[f"file:src/service_{i}.py"], mode="X")
                for i in range(5)
            ]

            execution_timestamps = []

            async def mock_worker(tx, task):
                t_start = time.time()
                await asyncio.sleep(0.05)  # Simulate work
                t_end = time.time()
                execution_timestamps.append((task.task_id, t_start, t_end))
                return f"processed_{task.task_id}"

            results = await dispatcher.dispatch_waves(tasks, mock_worker)
            assert len(results) == 5
            for r in results:
                assert r["status"] == "COMPLETED"
                assert r["fence_token"] > 0

            # Verify that all 5 ran concurrently (total elapsed time < 0.20s instead of 0.25s+)
            starts = [t[1] for t in execution_timestamps]
            max_start_diff = max(starts) - min(starts)
            assert max_start_diff < 0.04  # Started almost simultaneously

    asyncio.run(_run())


def test_topological_dispatcher_serializes_conflicts():
    async def _run():
        with tempfile.TemporaryDirectory() as tmpdir:
            j_db = str(Path(tmpdir) / "journal.db")
            l_db = str(Path(tmpdir) / "ledger.db")
            hypervisor = PrismaticHypervisor(journal_db_path=j_db, ledger_db_path=l_db)
            dispatcher = TopologicalDispatcher(hypervisor=hypervisor)

            tasks = [
                RoutedTask(task_id="t_write_1", resources=["file:src/auth.py"], mode="X"),
                RoutedTask(task_id="t_write_2", resources=["file:src/auth.py"], mode="X")
            ]

            history = []

            async def mock_worker(tx, task):
                history.append(f"start_{task.task_id}")
                await asyncio.sleep(0.03)
                history.append(f"end_{task.task_id}")
                return "done"

            results = await dispatcher.dispatch_waves(tasks, mock_worker)
            assert len(results) == 2
            # Verify strict sequential execution
            assert history == ["start_t_write_1", "end_t_write_1", "start_t_write_2", "end_t_write_2"]

    asyncio.run(_run())