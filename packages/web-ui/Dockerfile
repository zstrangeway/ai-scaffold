# Dockerfile for web-ui package (Storybook)
FROM node:18-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./

# Copy package.json files for dependency resolution
COPY packages/web-ui/package.json ./packages/web-ui/
COPY apps/*/package.json ./apps/*/
COPY packages/*/package.json ./packages/*/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY packages/web-ui ./packages/web-ui

# Set working directory to web-ui package
WORKDIR /app/packages/web-ui

# Expose Storybook port
EXPOSE 6006

# Start Storybook with hot-reloading
CMD ["pnpm", "dev", "--host", "0.0.0.0"]