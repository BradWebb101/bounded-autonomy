"""Tools on the agent. The user prompt is the JSON list. The model chooses."""

from __future__ import annotations

import time

from strands import Agent

from approaches.model import make_model
from domain.items import ids_mentioned, render_batch
from domain.tools import evaluate_item
from metrics import metrics_from_result, silent_callback, text_from_result


def run(items: list[dict]) -> dict:
    agent = Agent(
        name="agent_tools",
        model=make_model(temperature=0.0, max_tokens=800),
        tools=[evaluate_item],
        callback_handler=silent_callback,
    )
    user_prompt = render_batch(items)
    started = time.perf_counter()
    result = agent(user_prompt)
    wall_ms = (time.perf_counter() - started) * 1000
    answer = text_from_result(result)
    mentioned = ids_mentioned(answer, items)
    return {
        "approach": "agent_tools",
        "decision_space": "tools registered on the agent; model decides what to call",
        "answer": answer,
        "user_prompt": user_prompt,
        "items_total": len(items),
        "items_mentioned": len(mentioned),
        "skipped_ids": [item["id"] for item in items if item["id"] not in mentioned],
        "metrics": metrics_from_result(result, wall_ms, agent_executions=1),
    }
