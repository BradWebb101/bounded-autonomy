"""AgentCore HTTP host. Strands is the agent framework for every approach."""

from __future__ import annotations

import json
import logging
import os
from importlib.metadata import PackageNotFoundError, version

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder

from approaches import APPROACHES, BENCH_APPROACHES, run_approach, run_compare
from domain.items import DEFAULT_ITEMS

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger("bounded-autonomy")

try:
    STRANDS_VERSION = version("strands-agents")
except PackageNotFoundError as exc:
    raise RuntimeError(
        "strands-agents is required. Install agent/requirements.txt."
    ) from exc

# Touch the Strands surface used by the talk so a missing install fails at boot,
# not on the first invoke.
_ = (Agent, BedrockModel, GraphBuilder, tool)

app = BedrockAgentCoreApp()
log.info("framework=strands version=%s", STRANDS_VERSION)


@app.entrypoint
def invoke(payload, context):  # noqa: ANN001
    if not isinstance(payload, dict):
        return {"error": "payload must be a JSON object"}

    items = payload.get("items") or payload.get("claims") or DEFAULT_ITEMS
    if not isinstance(items, list) or not items:
        return {"error": "items must be a non-empty list of dictionaries"}

    approach = payload.get("approach", "subagents")
    if not isinstance(approach, str):
        return {"error": "approach must be a string"}

    log.info(
        "session=%s approach=%s items=%s framework=strands",
        getattr(context, "session_id", None),
        approach,
        len(items),
    )

    try:
        if approach == "compare":
            result = run_compare(items, BENCH_APPROACHES)
        else:
            result = run_approach(approach, items)
    except ValueError as exc:
        return {"error": str(exc), "approaches": sorted(APPROACHES) + ["compare"]}
    except Exception as exc:  # noqa: BLE001
        log.exception("approach %s failed", approach)
        return {"error": f"{type(exc).__name__}: {exc}"}

    result["framework"] = "strands"
    result["strands_version"] = STRANDS_VERSION
    result["model_id"] = os.environ.get("MODEL_ID")
    log.info("result_metrics=%s", json.dumps(result.get("metrics") or result.get("comparison")))
    return result


if __name__ == "__main__":
    app.run()
