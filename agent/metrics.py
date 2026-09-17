from __future__ import annotations

from typing import Any


def silent_callback(**_kwargs: Any) -> None:
    return None


def text_from_result(result: Any) -> str:
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        chunks = message.get("content") or []
        texts = [
            block.get("text", "")
            for block in chunks
            if isinstance(block, dict) and block.get("text")
        ]
        if texts:
            return "\n".join(texts).strip()
    return str(result).strip()


def empty_metrics(wall_ms: float, *, agent_executions: int = 0) -> dict[str, Any]:
    return {
        "wall_clock_ms": round(wall_ms, 1),
        "model_latency_ms": 0,
        "cycle_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "tools_used": [],
        "agent_executions": agent_executions,
    }


def metrics_from_result(
    result: Any | None,
    wall_ms: float,
    *,
    agent_executions: int = 1,
) -> dict[str, Any]:
    if result is None or not hasattr(result, "metrics"):
        return empty_metrics(wall_ms, agent_executions=agent_executions)

    metrics = result.metrics
    usage = getattr(metrics, "accumulated_usage", {}) or {}
    accumulated = getattr(metrics, "accumulated_metrics", {}) or {}
    tool_metrics = getattr(metrics, "tool_metrics", {}) or {}
    cycle_durations = getattr(metrics, "cycle_durations", []) or []

    return {
        "wall_clock_ms": round(wall_ms, 1),
        "model_latency_ms": accumulated.get("latencyMs", 0),
        "cycle_count": getattr(metrics, "cycle_count", len(cycle_durations)),
        "input_tokens": int(usage.get("inputTokens", 0) or 0),
        "output_tokens": int(usage.get("outputTokens", 0) or 0),
        "total_tokens": int(usage.get("totalTokens", 0) or 0),
        "tools_used": sorted(tool_metrics.keys()),
        "agent_executions": agent_executions,
    }


def metrics_from_graph(result: Any, wall_ms: float) -> dict[str, Any]:
    usage = getattr(result, "accumulated_usage", {}) or {}
    order = [
        getattr(node, "node_id", str(node))
        for node in (getattr(result, "execution_order", None) or [])
    ]
    execution_ms = getattr(result, "execution_time", None)
    return {
        "wall_clock_ms": round(float(execution_ms if execution_ms is not None else wall_ms), 1),
        "model_latency_ms": execution_ms,
        "cycle_count": getattr(result, "completed_nodes", len(order)),
        "input_tokens": int(usage.get("inputTokens", 0) or 0),
        "output_tokens": int(usage.get("outputTokens", 0) or 0),
        "total_tokens": int(usage.get("totalTokens", 0) or 0),
        "tools_used": [],
        "agent_executions": len(order) or getattr(result, "completed_nodes", 0),
        "execution_order": order,
    }


def merge_metrics(parts: list[dict[str, Any]], wall_ms: float) -> dict[str, Any]:
    tools: list[str] = []
    for part in parts:
        tools.extend(part.get("tools_used") or [])
    return {
        "wall_clock_ms": round(wall_ms, 1),
        "model_latency_ms": sum(p.get("model_latency_ms") or 0 for p in parts),
        "cycle_count": sum(p.get("cycle_count") or 0 for p in parts),
        "input_tokens": sum(p.get("input_tokens") or 0 for p in parts),
        "output_tokens": sum(p.get("output_tokens") or 0 for p in parts),
        "total_tokens": sum(p.get("total_tokens") or 0 for p in parts),
        "tools_used": sorted(set(tools)),
        "agent_executions": sum(p.get("agent_executions") or 0 for p in parts),
    }
