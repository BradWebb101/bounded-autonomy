#!/usr/bin/env python3
"""Run the talk approaches against the same list of dictionaries."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import invoke_runtime  # noqa: E402

APPROACHES = ("raw_batch", "for_loop", "subagents")
EXTRA = ("agent_tools", "prompted_tools", "user_prompt_exec")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--items",
        default=str(Path(__file__).resolve().parents[1] / "samples" / "items.json"),
        help="JSON file with a list of dictionaries",
    )
    parser.add_argument("--arn", default=os.environ.get("AGENT_RUNTIME_ARN"))
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", "eu-west-1"))
    parser.add_argument("--out", default="bench-results.json")
    parser.add_argument(
        "--extra",
        action="store_true",
        help="Also run agent_tools, prompted_tools, and user_prompt_exec",
    )
    args = parser.parse_args()

    if not args.arn:
        print("Pass --arn or set AGENT_RUNTIME_ARN", file=sys.stderr)
        return 2

    items = _load_items(args.items)
    names = APPROACHES + (EXTRA if args.extra else ())
    payload = {"items": items}

    print("Warmup (direct_tool on 1 item, discarded)...", file=sys.stderr)
    warmup = invoke_runtime(
        args.arn,
        {"approach": "direct_tool", "items": items[:1]},
        args.region,
    )
    if "error" in warmup and "metrics" not in warmup:
        print(json.dumps(warmup, indent=2), file=sys.stderr)
        return 1

    rows = []
    for approach in names:
        print(f"Running {approach} on {len(items)} items...", file=sys.stderr)
        result = invoke_runtime(
            args.arn,
            {**payload, "approach": approach},
            args.region,
        )
        if "error" in result and "metrics" not in result:
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 1
        metrics = result.get("metrics") or {}
        rows.append(
            {
                "approach": approach,
                "decision_space": result.get("decision_space"),
                "wall_clock_ms": metrics.get("wall_clock_ms"),
                "total_tokens": metrics.get("total_tokens"),
                "input_tokens": metrics.get("input_tokens"),
                "output_tokens": metrics.get("output_tokens"),
                "agent_executions": metrics.get("agent_executions"),
                "items_total": result.get("items_total"),
                "items_mentioned": result.get("items_mentioned"),
                "skipped_ids": result.get("skipped_ids"),
                "answer": result.get("answer"),
            }
        )

    Path(args.out).write_text(json.dumps({"items": items, "runs": rows}, indent=2))
    _print_table(rows)
    print(f"\nWrote {args.out}")
    return 0


def _load_items(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        data = data.get("items") or data.get("claims")
    if not isinstance(data, list):
        raise SystemExit("items file must be a JSON list of dictionaries")
    return data


def _print_table(rows: list[dict]) -> None:
    headers = ("approach", "ms", "tokens", "executions", "items")
    table = [headers]
    for row in rows:
        mentioned = row.get("items_mentioned")
        total = row.get("items_total")
        items = f"{mentioned}/{total}" if mentioned is not None else "—"
        table.append(
            (
                str(row["approach"]),
                str(row["wall_clock_ms"]),
                str(row["total_tokens"]),
                str(row.get("agent_executions")),
                items,
            )
        )

    widths = [max(len(row[i]) for row in table) for i in range(len(headers))]
    for index, row in enumerate(table):
        line = "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))
        print(line)
        if index == 0:
            print("  ".join("-" * widths[i] for i in range(len(headers))))

    by_name = {row["approach"]: row for row in rows}
    loop = by_name.get("for_loop")
    graph = by_name.get("subagents")
    if loop and graph and graph.get("wall_clock_ms"):
        print(
            f"\nCompute ratio for_loop / subagents: "
            f"{loop['wall_clock_ms'] / graph['wall_clock_ms']:.1f}x wall clock"
        )
    raw = by_name.get("raw_batch")
    if raw and raw.get("items_total"):
        print(
            f"raw_batch covered {raw.get('items_mentioned')}/{raw.get('items_total')} ids"
        )


if __name__ == "__main__":
    raise SystemExit(main())
