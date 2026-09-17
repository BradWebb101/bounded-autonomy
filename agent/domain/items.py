"""The talk batch: ten short orders. Each one is a job, not a file listing."""

from __future__ import annotations

import json

from domain.policy import Item, Line


DEFAULT_ITEMS: list[dict] = [
    {
        "id": "job-01",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 117.5,
        "discount_pct": 0,
        "lines": [
            {"sku": "NIC-1G", "qty": 3, "unit_eur": 12.5},
            {"sku": "SFP-SR", "qty": 1, "unit_eur": 80},
        ],
    },
    {
        "id": "job-02",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 620.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "GPU-L4", "qty": 2, "unit_eur": 250},
            {"sku": "CABLE-QSFP", "qty": 4, "unit_eur": 30},
        ],
    },
    {
        "id": "job-03",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 40.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "SSD-1T", "qty": 2, "unit_eur": 10},
            {"sku": "SATA", "qty": 1, "unit_eur": 5},
        ],
    },
    {
        "id": "job-04",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 0.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "RACK-U", "qty": 0, "unit_eur": 45},
        ],
    },
    {
        "id": "job-05",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 120.0,
        "discount_pct": 40,
        "lines": [
            {"sku": "MEM-32G", "qty": 2, "unit_eur": 100},
        ],
    },
    {
        "id": "job-06",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 22.5,
        "discount_pct": 0,
        "lines": [
            {"sku": "USB-C", "qty": 3, "unit_eur": 7.5},
        ],
    },
    {
        "id": "job-07",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 90.0,
        "discount_pct": 10,
        "lines": [
            {"sku": "PSU-750", "qty": 1, "unit_eur": 50},
            {"sku": "FAN-40", "qty": 2, "unit_eur": 25},
        ],
    },
    {
        "id": "job-08",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 600.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "SWITCH-48", "qty": 20, "unit_eur": 30},
        ],
    },
    {
        "id": "job-09",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 33.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "PATCH-1M", "qty": 4, "unit_eur": 8.25},
        ],
    },
    {
        "id": "job-10",
        "region": "eu-west-1",
        "task": "reconcile_order",
        "claimed_total_eur": 50.0,
        "discount_pct": 0,
        "lines": [
            {"sku": "SFP-LX", "qty": 2, "unit_eur": 15.5},
            {"sku": "LC-DUPLEX", "qty": 3, "unit_eur": 10},
        ],
    },
]


def item_from_dict(data: dict) -> Item:
    raw_lines = data.get("lines") or []
    if isinstance(data.get("lines_json"), str) and not raw_lines:
        raw_lines = json.loads(data["lines_json"])
    lines = tuple(
        Line(
            sku=str(line.get("sku") or ""),
            qty=float(line.get("qty") or 0),
            unit_eur=float(line.get("unit_eur") or 0),
        )
        for line in raw_lines
    )
    return Item(
        claimed_total_eur=float(data.get("claimed_total_eur") or 0),
        discount_pct=float(data.get("discount_pct") or 0),
        lines=lines,
    )


def tool_args(data: dict) -> dict:
    return {
        "item_id": data["id"],
        "claimed_total_eur": float(data["claimed_total_eur"]),
        "discount_pct": float(data.get("discount_pct") or 0),
        "lines_json": json.dumps(data.get("lines") or [], separators=(",", ":")),
    }


def render_item(data: dict) -> str:
    return json.dumps(data, sort_keys=True)


def render_batch(items: list[dict]) -> str:
    return (
        "Reconcile every order. For each id: recompute qty*unit_eur, apply "
        "discount_pct, compare to claimed_total_eur, then decide. Do not skip.\n\n"
        + json.dumps(items, separators=(",", ":"))
    )


def ids_mentioned(text: str, items: list[dict]) -> list[str]:
    return [item["id"] for item in items if item["id"] in text]
