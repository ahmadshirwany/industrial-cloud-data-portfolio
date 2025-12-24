# Dockerfile for Transformer Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# Copy entire project
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run the transformer microservice
CMD ["python", "services/transformer/main.py"]
