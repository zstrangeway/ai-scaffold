# Dockerfile for web_site (Next.js)
FROM node:20-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./

# Copy package.json files for dependency resolution
COPY apps/web_site/package.json ./apps/web_site/
COPY apps/*/package.json ./apps/*/
COPY packages/*/package.json ./packages/*/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY apps/web_site ./apps/web_site
COPY packages ./packages

# Set working directory to web_site app
WORKDIR /app/apps/web_site

# Expose Next.js port
EXPOSE 3000

# Start Next.js with hot-reloading
CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]
