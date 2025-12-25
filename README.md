# Agno Docs MCP Server

A Model Context Protocol (MCP) server that provides access to [Agno](https://agno.com) framework documentation. Enables developers to easily access Agno docs through coding agents like Claude Code, Cursor, and other MCP-compatible tools.

## Quick Start (New Laptop Setup)

### Prerequisites

- Python 3.10 or higher
- Git
- Access to the `agno-docs` repository (for documentation source)

### Step 1: Clone the Repository

```bash
git clone https://github.com/agno-agi/agno-docs-mcp
cd agno-docs-mcp
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first (required for pyproject.toml editable installs)
pip install --upgrade pip

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Step 4: Clone Agno Docs (if not already available)

```bash
# Clone the agno-docs repository (adjust path as needed)
git clone https://github.com/agno-agi/agno-docs ~/Work/agno-docs
```

### Step 5: Prepare Documentation

```bash
# Set the path to your agno-docs repository
export AGNO_DOCS_PATH=~/Work/agno-docs

# Run the preparation script to copy and index docs
python -m agno_docs_mcp.prepare
```

You should see output like:
```
Preparing Agno documentation...
  Source: /Users/you/Work/agno-docs
  Output: /Users/you/Work/agno-docs-mcp/.docs

Copying documentation files...
  Copied 596 files from basics/
  Copied 148 files from reference/
  Copied 74 files from reference-api/
  ...
  Copied OpenAPI spec (openapi.json)

Building search index...
  Indexed 1851 files in 10 categories

Done!
```

### Step 6: Configure Your MCP Client

#### Claude Code

Add to `~/.claude.json` or your project's `.claude/settings.json`:

```json
{
  "mcpServers": {
    "agno-docs": {
      "command": "/path/to/agno-docs-mcp/.venv/bin/python",
      "args": ["-m", "agno_docs_mcp"]
    }
  }
}
```

#### Cursor

Add to your Cursor MCP settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "agno-docs": {
      "command": "/path/to/agno-docs-mcp/.venv/bin/python",
      "args": ["-m", "agno_docs_mcp"]
    }
  }
}
```

#### Using HTTP Transport (Remote Access)

```json
{
  "mcpServers": {
    "agno-docs": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Step 7: Verify Installation

```bash
# Test the server directly
python -c "from agno_docs_mcp.tools.api import agno_api; print(agno_api('memory')[:200])"

# Or start the HTTP server
python -m agno_docs_mcp --transport http --port 8000

# In another terminal, test with curl
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Features

- **7 Specialized Tools** for navigating Agno documentation:
  - `agno_docs` - SDK conceptual documentation (agents, teams, workflows, basics)
  - `agno_reference` - SDK class and method reference
  - `agno_examples` - Code snippets and usage examples
  - `agno_integrations` - Database, VectorDB, and model provider guides
  - `agno_agentos` - AgentOS runtime documentation
  - `agno_api` - **REST API endpoints** from OpenAPI spec
  - `agno_migration` - Migration guides, FAQs, and troubleshooting

- **OpenAPI Integration** - Parses the OpenAPI spec for accurate REST endpoint docs
- **Keyword-based search** across all documentation
- **Path-based navigation** for exploring docs structure
- **Offline support** - docs are preprocessed and bundled locally
- **Multiple transports** - stdio (local) and HTTP (remote) support

## Running the Server

### Local CLI Mode (stdio) - Default

```bash
# Activate venv first
source .venv/bin/activate

# Run with stdio transport (for Claude Code, Cursor)
python -m agno_docs_mcp
```

### HTTP Server Mode

```bash
# Run HTTP server on port 8000
python -m agno_docs_mcp --transport http --port 8000

# Server available at http://localhost:8000/mcp
# Health check at http://localhost:8000/health
```

### Production Deployment

```bash
# Using uvicorn directly
uvicorn agno_docs_mcp.app:app --host 0.0.0.0 --port 8000

# Using Docker
docker build -t agno-docs-mcp .
docker run -p 8000:8000 agno-docs-mcp
```

## Tools Reference

### agno_api (NEW - REST API Endpoints)

Get AgentOS REST API endpoints from the OpenAPI specification.

```
agno_api(resource="memory")
```

**Parameters:**
- `resource` (str) - API resource: memory, agents, teams, workflows, sessions, knowledge, evals, traces, metrics, database, playground

**Use for:** REST API endpoints, HTTP methods, request/response schemas

### agno_docs

Get SDK conceptual documentation and guides for writing agent code.

```
agno_docs(path="basics/agents/")
```

**Parameters:**
- `path` (str) - Documentation path (e.g., "basics/", "basics/agents/", "basics/memory/")

**Use for:** How to write Python code with Agno SDK

### agno_reference

Get SDK class and method reference (parameters, signatures, options).

```
agno_reference(topic="agents")
```

**Parameters:**
- `topic` (str) - Reference topic: agents, teams, workflows, tools, models, memory, knowledge, storage, hooks, compression, reasoning, agent-os

**Use for:** Agent() constructor parameters, method signatures, configuration options

### agno_examples

Get SDK code examples for building agents.

```
agno_examples(category="agents")
```

**Parameters:**
- `category` (str) - Category: agents, teams, workflows, tools, memory, knowledge, models, database, evals, guardrails, hitl, multimodal, reasoning, sessions, tracing

### agno_integrations

Get integration documentation for databases, vector stores, and models.

```
agno_integrations(integration_type="database", name="postgres")
```

**Parameters:**
- `integration_type` (str) - Type: database, vectordb, models, toolkits
- `name` (str, optional) - Specific integration name

### agno_agentos

Get AgentOS runtime and deployment documentation.

```
agno_agentos(path="features/memories")
```

**Parameters:**
- `path` (str) - Path within AgentOS docs (e.g., "api/", "features/", "security/")

**Use for:** Deployment docs, runtime features, authentication, middleware

### agno_migration

Get migration guides and FAQ documentation.

```
agno_migration(topic="v2-migration")
```

**Parameters:**
- `topic` (str) - Migration topic or FAQ topic

## Tool Selection Guide

| Question Type | Use This Tool |
|--------------|---------------|
| "What REST API endpoints for memory?" | `agno_api("memory")` |
| "How to create an agent in Python?" | `agno_docs("basics/agents/")` |
| "What parameters does Agent() accept?" | `agno_reference("agents")` |
| "Show me agent code examples" | `agno_examples("agents")` |
| "How to connect to Postgres?" | `agno_integrations("database", "postgres")` |
| "How to deploy agents?" | `agno_agentos("api/")` |
| "How to migrate from v1?" | `agno_migration("v2-migration")` |

## Project Structure

```
agno-docs-mcp/
├── pyproject.toml
├── README.md
├── .venv/                      # Virtual environment
├── src/
│   └── agno_docs_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py           # Main MCP server with tool registration
│       ├── app.py              # FastAPI/ASGI app for HTTP
│       ├── tools/              # Tool implementations
│       │   ├── docs.py
│       │   ├── reference.py
│       │   ├── examples.py
│       │   ├── integrations.py
│       │   ├── agentos.py
│       │   ├── api.py          # NEW: OpenAPI parser
│       │   └── migration.py
│       ├── utils/              # Utility modules
│       │   ├── search.py
│       │   ├── paths.py
│       │   └── content.py
│       └── prepare/            # Doc preparation
│           └── prepare_docs.py
├── .docs/                      # Preprocessed docs (generated)
│   ├── raw/                    # Copied MDX files
│   ├── snippets/               # Snippet files
│   ├── index.json              # Search index
│   └── openapi.json            # OpenAPI spec
└── tests/
```

## Updating Documentation

When the agno-docs repository is updated:

```bash
# Pull latest docs
cd ~/Work/agno-docs
git pull

# Re-run preparation
cd ~/Work/agno-docs-mcp
source .venv/bin/activate
python -m agno_docs_mcp.prepare
```

## Troubleshooting

### "OpenAPI specification not found"

Run the prepare script:
```bash
export AGNO_DOCS_PATH=~/Work/agno-docs
python -m agno_docs_mcp.prepare
```

### "Module not found" errors

Make sure you're using the virtual environment:
```bash
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

### MCP client not connecting

1. Check the path in your MCP config points to the venv Python:
   ```json
   "command": "/absolute/path/to/agno-docs-mcp/.venv/bin/python"
   ```

2. Test the server manually:
   ```bash
   /path/to/agno-docs-mcp/.venv/bin/python -m agno_docs_mcp
   ```

## License

MIT

## Links

- [Agno Documentation](https://docs.agno.com)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [MCP Specification](https://modelcontextprotocol.io)
