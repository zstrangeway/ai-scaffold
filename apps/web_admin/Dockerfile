# Use Node.js Alpine image
FROM node:20-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY apps/web_admin/package.json ./apps/web_admin/
COPY apps/*/package.json ./apps/*/
COPY packages/*/package.json ./packages/*/

# Copy packages source code for workspace linking
COPY packages/ ./packages/

# Build the web-ui package so it's available for workspace linking
RUN cd packages/web-ui && pnpm install --no-frozen-lockfile && pnpm build

# Install dependencies (now workspace links can be created properly)
RUN pnpm install --no-frozen-lockfile

# Expose Next.js port
EXPOSE 3002
