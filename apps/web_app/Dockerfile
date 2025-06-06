# Use Node.js Alpine image
FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY apps/web_app/package.json ./apps/web_app/
COPY apps/*/package.json ./apps/*/
COPY packages/*/package.json ./packages/*/

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Expose Next.js port
EXPOSE 3001
