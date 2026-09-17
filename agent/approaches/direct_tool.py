"""Call the routing tool as a Python function. The model never chooses it."""

from __future__ import annotations

import time

from strands import Agent

from approaches.model import make_model
from domain.items import tool_args
from domain.tools import evaluate_item
from metrics import empty_metrics, silent_callback


def run(items: list[dict]) -> dict:
    agent = Agent(
        name="direct_tool",
        model=make_model(temperature=0.0, max_tokens=32),
        tools=[evaluate_item],
        callback_handler=silent_callback,
        record_direct_tool_call=False,
    )
    started = time.perf_counter()
    answers = []
    for item in items:
        answers.append(agent.tool.evaluate_item(**tool_args(item)))
    wall_ms = (time.perf_counter() - started) * 1000
    metrics = empty_metrics(wall_ms, agent_executions=0)
    metrics["tools_used"] = ["evaluate_item"]
    metrics["tool_invocations"] = len(answers)
    return {
        "approach": "direct_tool",
        "decision_space": "Python calls agent.tool.evaluate_item; no model routing",
        "answer": answers,
        "items_total": len(items),
        "items_mentioned": len(answers),
        "metrics": metrics,
    }
