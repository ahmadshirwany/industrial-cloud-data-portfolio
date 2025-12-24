# Dockerfile for Ingestion Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run the ingestion microservice
CMD ["python", "services/ingestion/main.py"]
