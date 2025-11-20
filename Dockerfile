# Multi-stage build for Python OneTimeSecret application
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/prod.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 ots && \
    mkdir -p /app && \
    chown -R ots:ots /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=ots:ots /root/.local /home/ots/.local

# Copy application code
COPY --chown=ots:ots src/ ./

# Switch to non-root user
USER ots

# Add user site-packages to PATH
ENV PATH=/home/ots/.local/bin:$PATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v2/status')"

# Run the application
CMD ["uvicorn", "onetimesecret.main:app", "--host", "0.0.0.0", "--port", "8000"]
