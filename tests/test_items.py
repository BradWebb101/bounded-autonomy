from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from domain.items import DEFAULT_ITEMS, ids_mentioned, item_from_dict, render_batch
from domain.policy import Decision, evaluate


def test_default_batch_is_ten_unique_jobs() -> None:
    ids = [item["id"] for item in DEFAULT_ITEMS]
    assert len(ids) == 10
    assert len(set(ids)) == 10
    assert {item["region"] for item in DEFAULT_ITEMS} == {"eu-west-1"}
    assert {item["task"] for item in DEFAULT_ITEMS} == {"reconcile_order"}


def test_samples_file_matches_default_batch() -> None:
    path = Path(__file__).resolve().parents[1] / "samples" / "items.json"
    assert json.loads(path.read_text()) == DEFAULT_ITEMS


def test_render_batch_is_a_job_list() -> None:
    text = render_batch(DEFAULT_ITEMS)
    assert ids_mentioned(text, DEFAULT_ITEMS) == [item["id"] for item in DEFAULT_ITEMS]
    blob = text.split("\n\n", 1)[1]
    parsed = json.loads(blob)
    assert parsed[0]["lines"][0]["sku"] == "NIC-1G"


def test_first_job_is_accepted() -> None:
    result = evaluate(item_from_dict(DEFAULT_ITEMS[0]))
    assert result.decision is Decision.ACCEPT
    assert result.expected_total_eur == 117.5


def test_mismatched_job_is_rejected() -> None:
    result = evaluate(item_from_dict(DEFAULT_ITEMS[2]))
    assert result.decision is Decision.REJECT
