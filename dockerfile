# Use Python 3.13.1 slim base image
FROM python:3.13.1-slim

# Set environment variables
ENV PYTHONPATH=/app:/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=3

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install --no-cache-dir uv==0.5.6

# Copy requirements first (better cache)
COPY requirements.txt ./

# Install dependencies with UV (correct syntax)
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy application code (separate layer for better cache)
COPY src/ ./src/
COPY pyproject.toml ./

# Create necessary directories
RUN mkdir -p /app/chroma_store /app/data /app/plots

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]