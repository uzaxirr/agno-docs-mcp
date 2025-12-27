FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir -e .

# Copy preprocessed documentation
COPY .docs/ .docs/

# Expose the MCP server port
EXPOSE 8000

# Health check (Railway handles health checks externally, but keeping for local Docker use)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the HTTP server (uses Railway's PORT env var, defaults to 8000)
CMD ["sh", "-c", "python -m agno_docs_mcp --transport http --host 0.0.0.0 --port ${PORT:-8000}"]
