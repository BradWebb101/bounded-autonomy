"""Function calls sit in the user message. The model still has to emit them."""

from __future__ import annotations

import time

from strands import Agent

from approaches.model import make_model
from domain.items import ids_mentioned
from domain.tools import evaluate_item
from domain.user_calls import render_user_function_calls
from metrics import metrics_from_result, silent_callback, text_from_result


def run(items: list[dict]) -> dict:
    user_prompt = (
        "Execute each of these function calls with the evaluate_item tool. "
        "Do not skip a line. Do not invent records.\n\n"
        + render_user_function_calls(items)
    )
    agent = Agent(
        name="prompted_tools",
        model=make_model(temperature=0.0, max_tokens=800),
        tools=[evaluate_item],
        callback_handler=silent_callback,
    )
    started = time.perf_counter()
    result = agent(user_prompt)
    wall_ms = (time.perf_counter() - started) * 1000
    answer = text_from_result(result)
    mentioned = ids_mentioned(answer, items)
    return {
        "approach": "prompted_tools",
        "decision_space": "function calls in the user message; model still emits tool_use",
        "answer": answer,
        "user_prompt": user_prompt,
        "items_total": len(items),
        "items_mentioned": len(mentioned),
        "skipped_ids": [item["id"] for item in items if item["id"] not in mentioned],
        "metrics": metrics_from_result(result, wall_ms, agent_executions=1),
    }
