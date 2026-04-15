FROM python:3.12-slim

# Install iputils-ping for the nettools feature
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r vulnpy && useradd -r -g vulnpy -d /app -s /bin/bash vulnpy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Writable dirs for the app (uploads + sqlite db)
RUN mkdir -p /app/uploads && chown -R vulnpy:vulnpy /app

USER vulnpy

EXPOSE 5000

CMD ["python", "app.py"]
