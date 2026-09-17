FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_CONTAINER=1

COPY requirements.txt .
RUN uv pip install -r requirements.txt \
    && uv pip install aws-opentelemetry-distro>=0.12.0

RUN useradd -m -u 1000 bedrock_agentcore

COPY --chown=bedrock_agentcore:bedrock_agentcore . .

USER bedrock_agentcore

EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "-m", "main"]
