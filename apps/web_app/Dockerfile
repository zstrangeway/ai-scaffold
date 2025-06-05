# Dockerfile for web_app (Next.js)
FROM node:18-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./

# Copy package.json files for dependency resolution
COPY apps/web_app/package.json ./apps/web_app/
COPY packages/*/package.json ./packages/*/
COPY apps/*/package.json ./apps/*/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy all shared packages (read-only for hot-reloading)
COPY packages ./packages

# Copy app source code
COPY apps/web_app ./apps/web_app

# Set working directory to the app
WORKDIR /app/apps/web_app

# Expose Next.js dev port
EXPOSE 3000

# Start Next.js development server
CMD ["pnpm", "dev", "--hostname", "0.0.0.0"]
