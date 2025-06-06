# Simple development Dockerfile
FROM node:22-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 3002

# Volume mounts and docker-compose command handle the rest
