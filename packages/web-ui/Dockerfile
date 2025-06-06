# Use Node.js Alpine image
FROM node:18-alpine

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages/web-ui/package.json ./packages/web-ui/
COPY apps/*/package.json ./apps/*/
COPY packages/*/package.json ./packages/*/

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Expose Storybook port
EXPOSE 6006