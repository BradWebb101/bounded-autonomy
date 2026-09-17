from __future__ import annotations

from approaches.agent_tools import run as run_agent_tools
from approaches.direct_tool import run as run_direct_tool
from approaches.for_loop import run as run_for_loop
from approaches.prompted_tools import run as run_prompted_tools
from approaches.raw_batch import run as run_raw_batch
from approaches.subagents import run as run_subagents
from approaches.user_prompt_exec import run as run_user_prompt_exec

BENCH_APPROACHES = ("raw_batch", "for_loop", "subagents")

APPROACHES = {
    "raw_batch": run_raw_batch,
    "for_loop": run_for_loop,
    "subagents": run_subagents,
    "direct_tool": run_direct_tool,
    "agent_tools": run_agent_tools,
    "prompted_tools": run_prompted_tools,
    "user_prompt_exec": run_user_prompt_exec,
}


def run_approach(name: str, items: list[dict]) -> dict:
    handler = APPROACHES.get(name)
    if handler is None:
        raise ValueError(
            f"unknown approach {name!r}; expected one of {sorted(APPROACHES)}"
        )
    return handler(items)


def run_compare(items: list[dict], names: tuple[str, ...] = BENCH_APPROACHES) -> dict:
    results = [run_approach(name, items) for name in names]
    comparison = [
        {
            "approach": item["approach"],
            "decision_space": item["decision_space"],
            "wall_clock_ms": item["metrics"]["wall_clock_ms"],
            "total_tokens": item["metrics"]["total_tokens"],
            "input_tokens": item["metrics"]["input_tokens"],
            "output_tokens": item["metrics"]["output_tokens"],
            "agent_executions": item["metrics"].get("agent_executions"),
            "items_total": item.get("items_total"),
            "items_mentioned": item.get("items_mentioned"),
        }
        for item in results
    ]
    return {
        "approach": "compare",
        "items_total": len(items),
        "results": results,
        "comparison": comparison,
    }
