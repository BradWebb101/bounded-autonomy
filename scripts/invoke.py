#!/usr/bin/env python3
"""Invoke one approach against the deployed AgentCore runtime."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runtime import invoke_runtime  # noqa: E402

CHOICES = [
    "raw_batch",
    "for_loop",
    "subagents",
    "direct_tool",
    "agent_tools",
    "prompted_tools",
    "user_prompt_exec",
    "compare",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approach", default="subagents", choices=CHOICES)
    parser.add_argument(
        "--items",
        default=str(Path(__file__).resolve().parents[1] / "samples" / "items.json"),
    )
    parser.add_argument("--arn", default=os.environ.get("AGENT_RUNTIME_ARN"))
    parser.add_argument("--region", default=os.environ.get("AWS_REGION", "eu-west-1"))
    args = parser.parse_args()

    if not args.arn:
        print("Pass --arn or set AGENT_RUNTIME_ARN", file=sys.stderr)
        return 2

    items = json.loads(Path(args.items).read_text())
    if isinstance(items, dict):
        items = items.get("items") or items.get("claims")

    result = invoke_runtime(
        args.arn,
        {"items": items, "approach": args.approach},
        args.region,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
