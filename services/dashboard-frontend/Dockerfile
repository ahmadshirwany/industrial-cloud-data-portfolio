FROM python:3.11-slim

WORKDIR /app

# Copy requirements from service
COPY services/dashboard-frontend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project  
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application directly
CMD ["python", "services/dashboard-frontend/main.py"]
