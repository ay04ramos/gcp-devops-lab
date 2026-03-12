# Use a lightweight Python base
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app ./app

# Env
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
# (Optional) GOOGLE_CLOUD_PROJECT is set at deploy time on Cloud Run

# Start with gunicorn in production
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 0 app.main:app
