"""Python for-loop: one new Strands agent per dictionary, sequential."""

from __future__ import annotations

import time

from approaches.workers import make_worker
from domain.items import render_item
from metrics import merge_metrics, metrics_from_result, text_from_result

TASK = 'JSON only: {"id":"...","expected_total_eur":0,"decision":"...","reason":"..."}'


def run(items: list[dict]) -> dict:
    started = time.perf_counter()
    answers = []
    parts = []
    for item in items:
        agent = make_worker(name=f"loop_{item['id']}", item=item)
        item_started = time.perf_counter()
        result = agent(TASK)
        item_ms = (time.perf_counter() - item_started) * 1000
        answers.append(
            {
                "id": item["id"],
                "item": render_item(item),
                "answer": text_from_result(result),
            }
        )
        parts.append(metrics_from_result(result, item_ms, agent_executions=1))
    wall_ms = (time.perf_counter() - started) * 1000
    return {
        "approach": "for_loop",
        "decision_space": "Python for-loop creates N sequential agents from a list of dicts",
        "answer": answers,
        "items_total": len(items),
        "items_mentioned": len(answers),
        "metrics": merge_metrics(parts, wall_ms),
    }
