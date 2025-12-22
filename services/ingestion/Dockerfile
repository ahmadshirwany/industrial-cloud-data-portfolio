# Dockerfile for Ingestion Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities and ingestion service
COPY shared/ ./shared/
COPY services/ingestion/ ./services/ingestion/

# Set Python path
ENV PYTHONPATH=/app

# Run the ingestion microservice
CMD ["python", "services/ingestion/main.py"]
