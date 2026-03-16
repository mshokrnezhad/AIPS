FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api_fetcher.py .
COPY cleanup.py .
COPY compare_results.py .
COPY data_saver.py .
COPY email_sender.py .
COPY link_verifier.py .
COPY llm_extractor.py .
COPY main.py .

# Copy .env file into the image
COPY .env .

# Create data directory that will be used for mounting
RUN mkdir -p /data

# Set environment variable to tell Python where to find .env
ENV PYTHONUNBUFFERED=1

# Run the application from /data directory where urls.json and venue folders are
WORKDIR /data
CMD ["python3", "/app/main.py"]
