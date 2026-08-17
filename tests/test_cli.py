"""tests/test_cli.py — Tests for SwarmRouter CLI commands."""

import json
from swarmrouter.cli import main


def test_cli_route(capsys) -> None:
    ret = main(["route", "Build backend FastAPI router endpoint", "--title", "API Endpoint"])
    assert ret == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["agent_id"] == "ned-code"
    assert "backend_api" in data["detected_domains"]


def test_cli_estimate(capsys) -> None:
    ret = main(["estimate", "Write a large python module", "--model", "gemini-flash"])
    assert ret == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["model_id"] == "gemini-flash"
    assert data["total_cost_usd"] >= 0


def test_cli_list_models(capsys) -> None:
    ret = main(["list-models"])
    assert ret == 0
    out = capsys.readouterr().out
    models = json.loads(out)
    assert len(models) >= 4
    assert any(m["id"] == "gemini-flash" for m in models)


def test_cli_list_agents(capsys) -> None:
    ret = main(["list-agents"])
    assert ret == 0
    out = capsys.readouterr().out
    agents = json.loads(out)
    assert len(agents) >= 5
    assert any(a["id"] == "agy" for a in agents)
