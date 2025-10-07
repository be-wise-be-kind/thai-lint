# Purpose: Multi-stage Docker build for thai-lint CLI with optimized image size and security
# Scope: Production Docker image for running thai-lint in containerized environments
# Overview: Multi-stage Docker build configuration that creates an optimized production image
#     for the thai-lint CLI tool. Build stage installs Poetry and all dependencies, while
#     runtime stage creates a minimal Python slim image with only production dependencies.
#     Implements security best practices by running as non-root user, optimizes layer caching
#     for faster rebuilds, and configures /workspace as the working directory for volume mounts.
#     Supports CLI execution via ENTRYPOINT for seamless command-line usage.
# Dependencies: Docker, Python 3.11, Poetry for dependency management
# Exports: Docker image thailint/thailint with CLI entrypoint
# Interfaces: Volume mount at /workspace, CLI arguments via docker run
# Environment: Production containerized deployment, development via docker-compose
# Related: docker-compose.yml, .dockerignore, pyproject.toml
# Implementation: Multi-stage build pattern, non-root user, Poetry dependency installation,
#     optimized layer caching with separate dependency and code copy steps

# ============================================================================
# Build Stage: Install dependencies with Poetry
# ============================================================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /build

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files first (better layer caching)
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual env (we're in a container)
RUN poetry config virtualenvs.create false

# Install dependencies only (no dev dependencies)
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy source code
COPY src/ ./src/

# ============================================================================
# Runtime Stage: Minimal production image
# ============================================================================
FROM python:3.11-slim

# Set labels for metadata
LABEL maintainer="Steve Jackson <steve@example.com>"
LABEL description="Thai-Lint - AI code linter for multi-language projects"
LABEL version="0.1.0"

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash thailint

# Set working directory (for volume mounts)
WORKDIR /workspace

# Install Poetry in runtime (needed for dependency resolution)
RUN pip install --no-cache-dir poetry==1.7.1

# Copy pyproject.toml and poetry.lock
COPY --chown=thailint:thailint pyproject.toml poetry.lock /app/

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy source code
COPY --chown=thailint:thailint src/ /app/src/

# Add app directory to PYTHONPATH
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Switch to non-root user
USER thailint

# Set entrypoint to thai-lint CLI
ENTRYPOINT ["python", "-m", "src.cli"]

# Default command: show help
CMD ["--help"]
