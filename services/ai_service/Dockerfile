# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables for Poetry
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install tools needed for Poetry installation and build dependencies
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
COPY ./services/ai_service/pyproject.toml ./services/ai_service/poetry.lock* ./services/ai_service/

# Change to service directory for poetry install
WORKDIR /app/services/ai_service

# Install project dependencies
RUN poetry install --no-interaction --no-ansi --only main --no-root

# Change back to app directory
WORKDIR /app

# Expose FastAPI port
EXPOSE 8000
