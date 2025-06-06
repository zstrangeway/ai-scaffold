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
    libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependency definition files for the service
COPY ./services/user_service/pyproject.toml ./services/user_service/poetry.lock* ./services/user_service/

# Change to service directory for poetry install
WORKDIR /app/services/user_service

# Install project dependencies (without installing the project itself as editable, and no dev dependencies)
RUN poetry install --no-interaction --no-ansi --only main --no-root

# Change back to app root
WORKDIR /app

# Expose the gRPC port
EXPOSE 50051

# Command is handled by docker-compose startup script
