# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables for Poetry
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install tools needed for Poetry installation and build dependencies
# For Debian, use apt-get
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependency definition files for the service
COPY ./services/gateway_service/pyproject.toml ./services/gateway_service/poetry.lock* ./services/gateway_service/

# Change to service directory for poetry install
WORKDIR /app/services/gateway_service

# Install project dependencies (without installing the project itself as editable, and no dev dependencies)
RUN poetry install --no-interaction --no-ansi --only main --no-root

# Change back to app root
WORKDIR /app

# Expose the port the app runs on (FastAPI default via Uvicorn is often 8000, but Dockerfile typically exposes 80 or a common app port)
# The actual mapping happens in docker-compose.yml
EXPOSE 8000

# Command is handled by docker-compose startup script
