# Use official Python 3.11 slim image (smaller, production-appropriate)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files (bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr (logs appear immediately)
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# postgresql-client: needed for psycopg2
# gcc, python3-dev, libpq-dev: needed to compile Python packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching optimization)
# If requirements.txt doesn't change, this layer is cached
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
# This comes AFTER pip install so code changes don't invalidate dependency cache
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the application
# Will be overridden by docker-compose for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]