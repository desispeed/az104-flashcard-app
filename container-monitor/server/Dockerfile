# Docker CLI (no daemon) — we only ever run `docker ps` against remote/local hosts.
FROM node:20-slim

# docker CLI + ssh client so DOCKER_HOST=ssh://... works.
COPY --from=docker:25-cli /usr/local/bin/docker /usr/local/bin/docker
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY src ./src

EXPOSE 8080
CMD ["node", "src/index.js"]
