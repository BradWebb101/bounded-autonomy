"""Reconcile one order: recompute the total, then decide."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Decision(str, Enum):
    ACCEPT = "accept"
    HOLD = "hold"
    REVIEW = "review"
    REJECT = "reject"


VALUE_REVIEW_EUR = 500.0
HIGH_DISCOUNT_PCT = 25.0
TOTAL_TOLERANCE_EUR = 0.05


@dataclass(frozen=True)
class Line:
    sku: str
    qty: float
    unit_eur: float


@dataclass(frozen=True)
class Item:
    claimed_total_eur: float
    discount_pct: float
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    rule_id: str
    reasons: list[str]
    expected_total_eur: float
    claimed_total_eur: float
    item: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision"] = self.decision.value
        return payload


def expected_total(item: Item) -> float:
    subtotal = sum(line.qty * line.unit_eur for line in item.lines)
    return round(subtotal * (1 - item.discount_pct / 100.0), 2)


def evaluate(item: Item) -> PolicyResult:
    expected = expected_total(item)
    record = {
        "claimed_total_eur": item.claimed_total_eur,
        "discount_pct": item.discount_pct,
        "lines": [asdict(line) for line in item.lines],
    }

    if not item.lines:
        return PolicyResult(
            decision=Decision.REJECT,
            rule_id="EMPTY_ORDER",
            reasons=["Order has no line items."],
            expected_total_eur=0.0,
            claimed_total_eur=item.claimed_total_eur,
            item=record,
        )

    if any(line.qty < 1 or line.unit_eur < 0 for line in item.lines):
        return PolicyResult(
            decision=Decision.REJECT,
            rule_id="INVALID_LINE",
            reasons=["A line has qty < 1 or a negative unit price."],
            expected_total_eur=expected,
            claimed_total_eur=item.claimed_total_eur,
            item=record,
        )

    if abs(expected - item.claimed_total_eur) > TOTAL_TOLERANCE_EUR:
        return PolicyResult(
            decision=Decision.REJECT,
            rule_id="TOTAL_MISMATCH",
            reasons=[
                f"Recomputed {expected:.2f} EUR vs claimed {item.claimed_total_eur:.2f} EUR."
            ],
            expected_total_eur=expected,
            claimed_total_eur=item.claimed_total_eur,
            item=record,
        )

    if item.discount_pct > HIGH_DISCOUNT_PCT:
        return PolicyResult(
            decision=Decision.HOLD,
            rule_id="HIGH_DISCOUNT",
            reasons=[f"Discount {item.discount_pct:g}% is above {HIGH_DISCOUNT_PCT:g}%."],
            expected_total_eur=expected,
            claimed_total_eur=item.claimed_total_eur,
            item=record,
        )

    if expected >= VALUE_REVIEW_EUR:
        return PolicyResult(
            decision=Decision.REVIEW,
            rule_id="HIGH_VALUE",
            reasons=[f"Expected {expected:.2f} EUR is at or above {VALUE_REVIEW_EUR:.0f} EUR."],
            expected_total_eur=expected,
            claimed_total_eur=item.claimed_total_eur,
            item=record,
        )

    return PolicyResult(
        decision=Decision.ACCEPT,
        rule_id="MATCH",
        reasons=["Recomputed total matches the claim."],
        expected_total_eur=expected,
        claimed_total_eur=item.claimed_total_eur,
        item=record,
    )
