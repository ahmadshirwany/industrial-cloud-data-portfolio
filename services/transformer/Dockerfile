# Dockerfile for Transformer Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY services/transformer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run the transformer microservice
CMD ["python", "services/transformer/main.py"]
