from __future__ import annotations

import json
import uuid

import boto3


def invoke_runtime(arn: str, payload: dict, region: str) -> dict:
    client = boto3.client("bedrock-agentcore", region_name=region)
    session_id = f"bounded-autonomy-{uuid.uuid4()}"
    response = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        runtimeSessionId=session_id,
        qualifier="DEFAULT",
        payload=json.dumps(payload).encode("utf-8"),
    )
    return _read_body(response)


def _read_body(response: dict) -> dict:
    content_type = response.get("contentType", "")
    raw = response.get("response")
    chunks: list[str] = []

    if hasattr(raw, "iter_lines"):
        for line in raw.iter_lines(chunk_size=1024):
            if not line:
                continue
            text = line.decode("utf-8")
            if text.startswith("data: "):
                text = text[6:]
            chunks.append(text)
    elif isinstance(raw, list):
        chunks.extend(chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk) for chunk in raw)
    elif isinstance(raw, (bytes, bytearray)):
        chunks.append(raw.decode("utf-8"))
    elif raw is not None:
        chunks.append(str(raw))

    body = "".join(chunks).strip()
    if not body:
        return {"error": "empty runtime response", "contentType": content_type}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"raw": body, "contentType": content_type}
