FROM node:18-slim

# Install tini + libcap
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini libcap2-bin && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy package files + source
COPY package*.json ./
COPY . .

# Install deps, create user, set ownership
RUN npm ci --only=production && npm cache clean --force && \
    addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /usr/src/app && \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/node

USER appuser

ENV NODE_ENV=production \
    PORT=80
EXPOSE 80

ENTRYPOINT ["/usr/bin/tini", "--", "node", "server.js"]