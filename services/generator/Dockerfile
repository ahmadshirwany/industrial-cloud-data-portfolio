# Dockerfile for Generator Microservice
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY services/generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run the generator microservice
CMD ["python", "services/generator/main.py"]
