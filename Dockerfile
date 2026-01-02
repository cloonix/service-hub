FROM python:3.13-alpine

WORKDIR /app

# Install system dependencies (minimal)
RUN apk add --no-cache gcc musl-dev curl

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY lib/ ./lib/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/data /app/cache

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
