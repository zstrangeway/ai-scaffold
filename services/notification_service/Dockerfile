# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set environment variables for Poetry
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install tools needed for Poetry installation and then Poetry itself
# For Alpine, use apk
RUN apk add --no-cache curl && \
    curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /app

# Copy the dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install project dependencies (without installing the project itself as editable, and no dev dependencies)
RUN poetry install --no-interaction --no-ansi --no-dev --no-root

# Copy the application code into the container
COPY ./app /app/app

# Expose the port the app runs on (FastAPI default via Uvicorn is often 8000, but Dockerfile typically exposes 80 or a common app port)
# The actual mapping happens in docker-compose.yml
EXPOSE 8003

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
