# Base Image: Minimal and fast Python 3.11 runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_DATA_DIR=/app/data

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create runtime database storage directory with appropriate permissions
RUN mkdir -p /app/data

# Copy application source code
COPY app/ ./app/

# Expose FastAPI service port
EXPOSE 8000

# Start Uvicorn ASGI Server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
