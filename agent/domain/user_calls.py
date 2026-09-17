"""Function calls that live on the user turn, not the system prompt."""

from __future__ import annotations

import ast

from domain.items import tool_args


def render_user_function_calls(items: list[dict]) -> str:
    lines = []
    for item in items:
        args = tool_args(item)
        lines.append(
            "evaluate_item("
            f"item_id={args['item_id']!r}, "
            f"claimed_total_eur={args['claimed_total_eur']}, "
            f"discount_pct={args['discount_pct']}, "
            f"lines_json={args['lines_json']!r})"
        )
    return "\n".join(lines)


def parse_user_function_calls(text: str) -> list[dict]:
    """Read evaluate_item(...) lines out of a user message."""
    calls: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("evaluate_item("):
            continue
        tree = ast.parse(line, mode="eval")
        node = tree.body
        if not isinstance(node, ast.Call):
            raise ValueError(f"not a call: {line}")
        kwargs: dict = {}
        for keyword in node.keywords:
            if keyword.arg is None:
                raise ValueError("star kwargs are not allowed")
            kwargs[keyword.arg] = ast.literal_eval(keyword.value)
        calls.append(kwargs)
    return calls
