"""Execute the functions that were written in the user message."""

from __future__ import annotations

import json
import time

from strands import Agent

from approaches.model import make_model
from domain.tools import run_evaluate_item
from domain.user_calls import parse_user_function_calls, render_user_function_calls
from metrics import metrics_from_result, silent_callback, text_from_result


def run(items: list[dict]) -> dict:
    user_prompt = render_user_function_calls(items)
    started = time.perf_counter()
    parsed = parse_user_function_calls(user_prompt)
    decisions = [run_evaluate_item(**call) for call in parsed]
    parse_ms = (time.perf_counter() - started) * 1000

    agent = Agent(
        name="user_prompt_exec",
        model=make_model(temperature=0.0, max_tokens=400),
        callback_handler=silent_callback,
    )
    wording_prompt = (
        "These function results are already decided. One line per id. "
        "Do not change a decision.\n\n"
        + json.dumps(decisions)
    )
    wording_started = time.perf_counter()
    wording = agent(wording_prompt)
    wording_ms = (time.perf_counter() - wording_started) * 1000
    wall_ms = (time.perf_counter() - started) * 1000

    metrics = metrics_from_result(wording, wording_ms, agent_executions=1)
    metrics["wall_clock_ms"] = round(wall_ms, 1)
    metrics["parse_ms"] = round(parse_ms, 1)
    metrics["tool_invocations"] = len(decisions)

    return {
        "approach": "user_prompt_exec",
        "decision_space": "user message is the program; Python executes; model only formats",
        "answer": text_from_result(wording),
        "decisions": decisions,
        "user_prompt": user_prompt,
        "items_total": len(items),
        "items_mentioned": len(decisions),
        "metrics": metrics,
    }
