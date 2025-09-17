# Simple multi-stage Dockerfile for deputydev-binary (no SSH required)
# Uses uv for fast, reproducible installs

FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for git+https installs and diagnostics
RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      curl \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Leverage Docker layer caching for deps
COPY pyproject.toml uv.lock ./

# Create and populate a local virtual environment under /app/.venv
RUN uv sync --frozen --no-cache

# Copy the application source
COPY . .

# ---------------- Runtime ----------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PYTHONPATH="/app/.venv/lib/python3.11/site-packages"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Minimal runtime tools
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      git \
    && rm -rf /var/lib/apt/lists/*

# Set git configuration for GitPython
ENV GIT_PYTHON_REFRESH=quiet
ENV GIT_PYTHON_GIT_EXECUTABLE="/usr/bin/git"

WORKDIR /app

# Bring app and virtualenv from builder
COPY --from=builder /app /app

EXPOSE 8001

# Default command mirrors compose usage
CMD ["python", "-m", "app.service", "8001"]