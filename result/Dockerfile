FROM node:18-slim

# Install tini for proper signal handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy package files + install deps + copy source + create user + set ownership
COPY package*.json ./
COPY . .

RUN npm ci --only=production && npm cache clean --force && \
    addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /usr/src/app
USER appuser

ENV NODE_ENV=production \
    PORT=3000
EXPOSE 3000

# Single entrypoint (no CMD)
ENTRYPOINT ["/usr/bin/tini", "--", "node", "server.js"]
