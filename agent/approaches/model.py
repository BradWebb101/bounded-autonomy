from __future__ import annotations

import os

from strands.models import BedrockModel


def model_id() -> str:
    return os.environ.get("MODEL_ID", "eu.amazon.nova-lite-v1:0")


def make_model(*, temperature: float = 0.2, max_tokens: int | None = None) -> BedrockModel:
    kwargs: dict = {
        "model_id": model_id(),
        "temperature": temperature,
        "streaming": False,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    return BedrockModel(**kwargs)
