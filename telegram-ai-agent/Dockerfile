FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

# Install only the minimal system tools the agent sandbox needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git jq tini && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent -d /app -s /sbin/nologin agent

COPY . .

RUN mkdir -p memory skills && chown -R agent:agent /app

USER agent

# Health check — verify the Python process is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, signal; os.kill(1, 0)" || exit 1

# Use tini as init to handle PID 1 / signal forwarding properly
ENTRYPOINT ["tini", "--"]
CMD ["python", "bot.py"]
