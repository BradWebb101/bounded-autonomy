"""Order reconcilation as a Strands tool and as a plain function."""

from __future__ import annotations

from strands import tool

from domain.items import item_from_dict
from domain.policy import evaluate


def run_evaluate_item(
    item_id: str,
    claimed_total_eur: float,
    discount_pct: float,
    lines_json: str,
) -> dict:
    result = evaluate(
        item_from_dict(
            {
                "id": item_id,
                "claimed_total_eur": claimed_total_eur,
                "discount_pct": discount_pct,
                "lines_json": lines_json,
            }
        )
    )
    payload = result.as_dict()
    payload["id"] = item_id
    return payload


@tool
def evaluate_item(
    item_id: str,
    claimed_total_eur: float,
    discount_pct: float,
    lines_json: str,
) -> dict:
    """Reconcile one order. Recompute line totals, apply discount, decide."""
    return run_evaluate_item(
        item_id=item_id,
        claimed_total_eur=claimed_total_eur,
        discount_pct=discount_pct,
        lines_json=lines_json,
    )
