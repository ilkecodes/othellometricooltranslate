FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Make init script executable
RUN chmod +x /app/init-db.sh

# Expose port
EXPOSE 8000

# Start with init script then run uvicorn
CMD ["/bin/bash", "-c", "/app/init-db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
