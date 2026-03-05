FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run on schedule (no immediate run on container start)
ENTRYPOINT ["python", "bot.py"]
CMD ["--schedule"]
