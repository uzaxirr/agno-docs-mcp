"""Agno Documentation MCP Server.

A Model Context Protocol server that provides access to Agno framework documentation.
Enables developers to easily access Agno docs through coding agents like Claude Code.
"""

import argparse

from mcp.server.fastmcp import FastMCP

from .tools.docs import agno_docs as _agno_docs
from .tools.reference import agno_reference as _agno_reference
from .tools.examples import agno_examples as _agno_examples
from .tools.integrations import agno_integrations as _agno_integrations
from .tools.agentos import agno_agentos as _agno_agentos
from .tools.migration import agno_migration as _agno_migration
from .tools.api import agno_api as _agno_api

# Create MCP server with HTTP-optimized settings
mcp = FastMCP(
    "agno-docs-server",
    stateless_http=True,   # Stateless for scalability
    json_response=True,    # JSON responses for HTTP
)


# Register tools with MCP server - using simple parameters for better LLM compatibility

@mcp.tool()
def agno_docs(path: str) -> str:
    """Get Agno SDK conceptual documentation and guides for writing agent code.

    Args:
        path: Documentation path. Use "basics/" to see all topics.

    SDK Documentation Paths:
        - "basics/agents/" - How to create and configure agents in code
        - "basics/tools/" - How to create custom tools for agents
        - "basics/memory/" - How to use memory in your agent code
        - "basics/knowledge/" - Knowledge bases and RAG implementation
        - "basics/teams/" - Multi-agent team coordination
        - "basics/workflows/" - Workflow orchestration patterns

    This is for SDK/library usage (writing Python code with Agno).
    For deployed agent REST APIs and runtime features, use agno_agentos instead.
    """
    # Convert single path to list for internal function
    return _agno_docs([path], None)


@mcp.tool()
def agno_reference(topic: str) -> str:
    """Get Agno SDK class and method reference (parameters, signatures, options).

    Args:
        topic: Reference topic. One of: agents, teams, workflows, tools, models,
               memory, knowledge, storage, hooks, compression, reasoning, agent-os

    This provides SDK CLASS documentation (e.g., Agent() constructor parameters,
    MemoryManager methods, Tool decorator options).

    For runtime REST API endpoints (deployed agent APIs), use agno_agentos instead.
    """
    return _agno_reference(topic, None)


@mcp.tool()
def agno_examples(category: str = "") -> str:
    """Get SDK code examples for building agents with Agno.

    Args:
        category: Example category. One of: agents, teams, workflows, tools, memory,
                  knowledge, models, database, evals, guardrails, hitl, multimodal,
                  reasoning, sessions, tracing
                  Leave empty to list all available categories.

    Returns complete, runnable Python code examples with imports and setup.
    These are SDK examples for writing agent code, not deployment examples.

    For deployment and hosting examples, use agno_agentos instead.
    """
    return _agno_examples(category if category else None, None)


@mcp.tool()
def agno_integrations(integration_type: str, name: str = "") -> str:
    """Get integration documentation for databases, vector stores, and models.

    Args:
        integration_type: Type of integration. One of: database, vectordb, models, toolkits
        name: Specific integration name. Leave empty to list all of that type.
              Database: postgres, mongodb, sqlite, mysql, redis, dynamodb, firestore
              VectorDB: pinecone, qdrant, chroma, weaviate, milvus, lancedb
              Models: openai, anthropic, google, azure, bedrock

    Examples:
        - integration_type="database", name="postgres"
        - integration_type="vectordb", name="pinecone"
        - integration_type="models" (lists all providers)
    """
    return _agno_integrations(integration_type, name if name else None, None)


@mcp.tool()
def agno_agentos(path: str = "") -> str:
    """Get AgentOS runtime and deployment documentation (REST APIs, endpoints, hosting).

    Args:
        path: Path within AgentOS docs. Leave empty for overview.

    AgentOS Sections:
        - "api/" - REST API authentication and endpoint usage
        - "features/" - Runtime features: memories, sessions, knowledge, tracing
        - "features/memories" - Memory API endpoints for deployed agents
        - "security/" - RBAC, authentication, authorization
        - "middleware/" - JWT auth, custom middleware
        - "interfaces/" - Slack, WhatsApp, A2A protocol integrations
        - "client/" - AgentOS Python client for calling deployed agents

    USE THIS TOOL for questions about:
    - Deployed agent REST API endpoints
    - Memory/session/knowledge endpoints in production
    - Authentication and security for hosted agents
    - Runtime features and middleware

    For SDK code usage (writing agents), use agno_docs or agno_reference instead.
    """
    return _agno_agentos(path if path else None, None)


@mcp.tool()
def agno_migration(topic: str = "") -> str:
    """Get migration guides and FAQ documentation.

    Args:
        topic: Topic to fetch. Leave empty to list all available topics.
               Migration guides: v2-migration, workflows-migration, installation, changelog
               FAQ topics: environment, openai-key, structured-outputs, docker-connection,
                          agentos-connection, rbac-auth, switching-models, tpm, tableplus

    Use for upgrading Agno versions, installation issues, and common errors.
    """
    # Determine if it's a migration topic or FAQ topic
    faq_topics = {
        "agentos-connection", "docker-connection", "environment", "openai-key",
        "rbac-auth", "structured-outputs", "switching-models", "tpm",
        "workflow-vs-team", "tableplus"
    }

    if topic in faq_topics:
        return _agno_migration(None, topic, None)
    else:
        return _agno_migration(topic if topic else None, None, None)


@mcp.tool()
def agno_api(resource: str = "") -> str:
    """Get AgentOS REST API endpoints from the OpenAPI specification.

    Args:
        resource: API resource to look up. One of: memory, agents, teams, workflows,
                  sessions, knowledge, evals, traces, metrics, database, playground
                  Leave empty to list all available API resources.

    Returns detailed REST API endpoint documentation including:
    - HTTP method and path (e.g., GET /memories, POST /memories)
    - Request parameters and their types
    - Request body schema
    - Response codes and descriptions

    USE THIS TOOL when the user asks about:
    - REST API endpoints for deployed AgentOS
    - HTTP methods for interacting with AgentOS
    - API schemas and parameters
    - How to call AgentOS programmatically via HTTP

    For SDK/Python code (classes, methods), use agno_reference instead.
    For conceptual docs about features, use agno_agentos instead.
    """
    return _agno_api(resource if resource else None, None)


def main() -> None:
    """Run the Agno Docs MCP server.

    Supports multiple transports:
    - stdio (default): For local CLI usage with Claude Code, Cursor, etc.
    - http: StreamableHTTP for remote access via URL
    - sse: Server-Sent Events transport
    """
    parser = argparse.ArgumentParser(
        description="Agno Documentation MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio (default, for local CLI tools)
  python -m agno_docs_mcp

  # Run HTTP server on port 8000
  python -m agno_docs_mcp --transport http --port 8000

  # Run SSE server
  python -m agno_docs_mcp --transport sse --port 8000
        """
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )

    args = parser.parse_args()

    if args.transport == "http":
        import uvicorn
        from .app import app
        print(f"Starting Agno Docs MCP server on http://{args.host}:{args.port}/mcp")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    elif args.transport == "sse":
        import uvicorn
        from .app import app
        print(f"Starting Agno Docs MCP server (SSE) on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
