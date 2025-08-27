FROM node:18-slim

# Install tini for proper signal handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy only package files first (better layer caching)
COPY package*.json ./

# Install only production deps
RUN npm ci --only=production && npm cache clean --force

# Copy app source
COPY . .

# Create non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /usr/src/app
USER appuser

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

# Single entrypoint (no CMD)
ENTRYPOINT ["/usr/bin/tini", "--", "node", "server.js"]
