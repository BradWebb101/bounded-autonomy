"""Dump the whole list of dictionaries into one model call and hope."""

from __future__ import annotations

import time

from strands import Agent

from approaches.model import make_model
from domain.items import ids_mentioned, render_batch
from metrics import metrics_from_result, silent_callback, text_from_result

SYSTEM_PROMPT = """
Reconcile every order in the JSON list. For each id recompute qty*unit_eur,
apply discount_pct, compare to claimed_total_eur.
Reject invalid lines or a mismatch > 0.05 EUR. Hold if discount_pct > 25.
Review if expected total >= 500. Else accept.
One compact line per id: id, expected_total_eur, decision.
""".strip()


def run(items: list[dict]) -> dict:
    agent = Agent(
        name="raw_batch",
        model=make_model(temperature=0.2, max_tokens=700),
        system_prompt=SYSTEM_PROMPT,
        callback_handler=silent_callback,
    )
    started = time.perf_counter()
    result = agent(render_batch(items))
    wall_ms = (time.perf_counter() - started) * 1000
    answer = text_from_result(result)
    mentioned = ids_mentioned(answer, items)
    return {
        "approach": "raw_batch",
        "decision_space": "one prompt, whole job list, model may skip items",
        "answer": answer,
        "items_total": len(items),
        "items_mentioned": len(mentioned),
        "skipped_ids": [item["id"] for item in items if item["id"] not in mentioned],
        "metrics": metrics_from_result(result, wall_ms, agent_executions=1),
    }
