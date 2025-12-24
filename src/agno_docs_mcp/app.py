"""ASGI application for production deployment.

This module provides a Starlette-based ASGI application that can be deployed
with uvicorn or any ASGI server for production use.

Usage:
    uvicorn agno_docs_mcp.app:app --host 0.0.0.0 --port 8000
"""

import contextlib

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from .server import mcp


async def health(request: Request) -> JSONResponse:
    """Health check endpoint for load balancers and monitoring."""
    return JSONResponse({
        "status": "healthy",
        "service": "agno-docs-mcp",
        "version": "0.1.0",
    })


async def root(request: Request) -> JSONResponse:
    """Root endpoint with service info."""
    return JSONResponse({
        "service": "Agno Documentation MCP Server",
        "version": "0.1.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health",
        "docs": "https://docs.agno.com",
        "tools": [
            "agno_docs",
            "agno_reference",
            "agno_examples",
            "agno_integrations",
            "agno_agentos",
            "agno_migration",
        ],
    })


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """Lifespan manager for the MCP session manager."""
    async with mcp.session_manager.run():
        yield


# Create the base Starlette app
_app = Starlette(
    routes=[
        Route("/", root),
        Route("/health", health),
        Mount("/", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)

# Wrap with CORS middleware for browser-based MCP clients
app = CORSMiddleware(
    _app,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
