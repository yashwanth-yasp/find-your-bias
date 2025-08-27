
# ========================
# Stage 1: Build dependencies
# ========================
FROM python:3.11-slim AS builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (e.g., gcc for building wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Install Python dependencies in a separate layer for caching
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ========================
# Stage 2: Final runtime image
# ========================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -ms /bin/bash appuser
WORKDIR /usr/local/app

# Copy wheels from builder stage and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy app source code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /usr/local/app
USER appuser

# Expose application port
EXPOSE 80

# # Healthcheck for container orchestration systems
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#   CMD curl --fail http://localhost:80/ || exit 1

# Start Gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--workers=4", "--threads=2", "--keep-alive=120", "--log-level=info"]
