FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ src/
COPY data/.gitkeep data/.gitkeep

ENV PODFLOW_DATA_DIR=/app/data

EXPOSE 8080

CMD ["uv", "run", "podflow"]
