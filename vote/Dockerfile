# Build Stage
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels && \
    apt-get purge -y build-essential gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Runtime Stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /usr/local/app

# Install runtime deps + create user
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev libcap2-bin && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -ms /bin/bash appuser

# Copy wheels and app source code
COPY --from=builder /wheels /wheels
COPY . .

# Install wheels + set ownership
RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels && \
    chown -R appuser:appuser /usr/local/app && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/python3.11

USER appuser

EXPOSE 80

ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:80"]