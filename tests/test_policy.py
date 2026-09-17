from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from domain.policy import Decision, Item, Line, evaluate, expected_total


def _order(*, claimed: float, discount: float, lines: list[tuple[str, float, float]]) -> Item:
    return Item(
        claimed_total_eur=claimed,
        discount_pct=discount,
        lines=tuple(Line(sku=sku, qty=qty, unit_eur=price) for sku, qty, price in lines),
    )


def test_matching_small_order_is_accepted() -> None:
    item = _order(claimed=117.5, discount=0, lines=[("NIC-1G", 3, 12.5), ("SFP-SR", 1, 80)])
    result = evaluate(item)
    assert expected_total(item) == 117.5
    assert result.decision is Decision.ACCEPT


def test_total_mismatch_is_rejected() -> None:
    item = _order(claimed=40, discount=0, lines=[("SSD-1T", 2, 10), ("SATA", 1, 5)])
    result = evaluate(item)
    assert result.decision is Decision.REJECT
    assert result.rule_id == "TOTAL_MISMATCH"


def test_zero_qty_is_rejected() -> None:
    result = evaluate(_order(claimed=0, discount=0, lines=[("RACK-U", 0, 45)]))
    assert result.decision is Decision.REJECT
    assert result.rule_id == "INVALID_LINE"


def test_high_discount_is_held() -> None:
    item = _order(claimed=120, discount=40, lines=[("MEM-32G", 2, 100)])
    result = evaluate(item)
    assert expected_total(item) == 120.0
    assert result.decision is Decision.HOLD


def test_high_value_is_reviewed() -> None:
    item = _order(claimed=620, discount=0, lines=[("GPU-L4", 2, 250), ("CABLE-QSFP", 4, 30)])
    result = evaluate(item)
    assert result.decision is Decision.REVIEW
