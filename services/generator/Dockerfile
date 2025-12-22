# Dockerfile for Generator Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities and generator service
COPY shared/ ./shared/
COPY services/generator/ ./services/generator/

# Set Python path
ENV PYTHONPATH=/app

# Run the generator microservice
CMD ["python", "services/generator/main.py"]
