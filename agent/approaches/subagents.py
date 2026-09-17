"""Strands Graph: one subagent node per dictionary, run as a parallel batch."""

from __future__ import annotations

import time

from strands.multiagent import GraphBuilder

from approaches.workers import make_worker
from domain.items import render_item
from metrics import metrics_from_graph, text_from_result

TASK = 'JSON only: {"id":"...","expected_total_eur":0,"decision":"...","reason":"..."}'


def run(items: list[dict]) -> dict:
    builder = GraphBuilder()
    node_ids = []
    for item in items:
        node_id = f"item_{item['id']}"
        worker = make_worker(name=node_id, item=item)
        builder.add_node(worker, node_id)
        node_ids.append(node_id)
    builder.set_execution_timeout(180)
    graph = builder.build()

    started = time.perf_counter()
    result = graph(TASK)
    wall_ms = (time.perf_counter() - started) * 1000

    answers = []
    for node_id, item in zip(node_ids, items):
        node = (getattr(result, "results", None) or {}).get(node_id)
        inner = getattr(node, "result", None) if node is not None else None
        answers.append(
            {
                "id": item["id"],
                "node": node_id,
                "item": render_item(item),
                "answer": text_from_result(inner) if inner is not None else None,
            }
        )

    metrics = metrics_from_graph(result, wall_ms)
    return {
        "approach": "subagents",
        "decision_space": "Strands Graph fans out one subagent per dictionary in the list",
        "answer": answers,
        "items_total": len(items),
        "items_mentioned": len(answers),
        "graph_status": str(getattr(result, "status", "")),
        "metrics": metrics,
    }
