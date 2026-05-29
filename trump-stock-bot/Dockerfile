FROM python:3.11-slim

# truthbrush needs git for some installs; keep image lean otherwise.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install deps first for better layer caching.
# Core deps are required.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# truthbrush (Truth Social) is best-effort: if it fails to install the bot
# still runs with the Google News + GDELT sources.
RUN pip install --no-cache-dir truthbrush \
    || echo "truthbrush install skipped — Truth Social source will be disabled"

COPY . .

# Persist the de-dup database across restarts via a mounted volume.
VOLUME ["/app/data"]

# Run continuously, scanning on the interval from SCAN_INTERVAL_SECONDS.
CMD ["python", "main.py", "--loop"]
