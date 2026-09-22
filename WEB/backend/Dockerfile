FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck if needed
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY WEB/backend/requirements.txt /app/WEB/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/WEB/backend/requirements.txt

# Copy application files
COPY . /app

WORKDIR /app/WEB/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
