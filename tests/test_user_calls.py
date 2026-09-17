from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent"))

from domain.items import DEFAULT_ITEMS, item_from_dict
from domain.policy import Decision, evaluate
from domain.user_calls import parse_user_function_calls, render_user_function_calls


def test_user_prompt_round_trips_ten_jobs() -> None:
    prompt = render_user_function_calls(DEFAULT_ITEMS)
    parsed = parse_user_function_calls(prompt)
    assert [call["item_id"] for call in parsed] == [item["id"] for item in DEFAULT_ITEMS]
    third = parsed[2]
    result = evaluate(
        item_from_dict(
            {
                "id": third["item_id"],
                "claimed_total_eur": third["claimed_total_eur"],
                "discount_pct": third["discount_pct"],
                "lines_json": third["lines_json"],
            }
        )
    )
    assert result.decision is Decision.REJECT
    assert json.loads(third["lines_json"])[0]["sku"] == "SSD-1T"
