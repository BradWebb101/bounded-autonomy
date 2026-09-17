"""Shared one-order worker used by the for-loop and Graph subagents."""

from __future__ import annotations

from strands import Agent

from approaches.model import make_model
from domain.items import render_item
from metrics import silent_callback

WORKER_PROMPT = """
Reconcile exactly one order. Recompute sum(qty*unit_eur), apply discount_pct,
compare to claimed_total_eur.
Reject invalid lines (qty<1) or a total mismatch > 0.05 EUR.
Hold if discount_pct > 25. Review if expected total >= 500. Else accept.
JSON only: {"id":"...","expected_total_eur":0,"decision":"accept|hold|review|reject","reason":"..."}
""".strip()


def make_worker(*, name: str, item: dict) -> Agent:
    return Agent(
        name=name,
        model=make_model(temperature=0.0, max_tokens=160),
        system_prompt=WORKER_PROMPT + "\n\n" + render_item(item),
        callback_handler=silent_callback,
    )
