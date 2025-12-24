# Agno Docs MCP Server

A Model Context Protocol (MCP) server that provides access to [Agno](https://agno.com) framework documentation. Enables developers to easily access Agno docs through coding agents like Claude Code, Cursor, and other MCP-compatible tools.

## Features

- **6 Specialized Tools** for navigating Agno documentation:
  - `agno_docs` - Core documentation (agents, teams, workflows, basics)
  - `agno_reference` - API reference and parameter docs
  - `agno_examples` - Code snippets and usage examples
  - `agno_integrations` - Database, VectorDB, and model provider guides
  - `agno_agentos` - AgentOS runtime documentation
  - `agno_migration` - Migration guides, FAQs, and troubleshooting

- **Keyword-based search** across all documentation
- **Path-based navigation** for exploring docs structure
- **Offline support** - docs are preprocessed and bundled locally
- **Multiple transports** - stdio (local) and HTTP (remote) support
- **Production-ready** - Docker support, health checks, CORS configured

## Installation

### Using pip

```bash
pip install agno-docs-mcp
```

### From source

```bash
git clone https://github.com/agno-agi/agno-docs-mcp
cd agno-docs-mcp
pip install -e .
```

## Setup

### 1. Prepare Documentation

Before using the server, you need to prepare the documentation:

```bash
# Set the path to your Agno docs repository
export AGNO_DOCS_PATH=/path/to/agno-docs

# Run the preparation script
python -m agno_docs_mcp.prepare
```

This copies and indexes the documentation for fast access.

### 2. Configure Your MCP Client

#### Claude Code / Claude Desktop

Add to your Claude configuration:

```json
{
  "mcpServers": {
    "agno-docs": {
      "command": "python",
      "args": ["-m", "agno_docs_mcp"]
    }
  }
}
```

#### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "agno-docs": {
      "command": "python",
      "args": ["-m", "agno_docs_mcp"]
    }
  }
}
```

#### Remote HTTP Server

If using the hosted version at `mcp.docs.agno.com`:

```json
{
  "mcpServers": {
    "agno-docs": {
      "url": "https://mcp.docs.agno.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

## Running the Server

### Local CLI Mode (stdio)

```bash
# Default - runs with stdio transport for local CLI tools
python -m agno_docs_mcp
```

### HTTP Server Mode

```bash
# Run HTTP server on port 8000
python -m agno_docs_mcp --transport http --port 8000

# Server available at http://localhost:8000/mcp
# Health check at http://localhost:8000/health
```

### Production Deployment (uvicorn)

```bash
# For production, use uvicorn with the ASGI app
uvicorn agno_docs_mcp.app:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t agno-docs-mcp .

# Run the container
docker run -p 8000:8000 agno-docs-mcp

# Or use docker-compose
docker-compose up
```

## Usage

Once configured, the MCP tools are available to your coding agent.

### Example Queries

**Explore documentation structure:**
```
Use agno_docs with paths=["basics/"] to see what's available
```

**Get agent documentation:**
```
Use agno_docs with paths=["basics/agents/overview"]
```

**Find code examples:**
```
Use agno_examples with category="agents" to get agent examples
```

**Look up API reference:**
```
Use agno_reference with topic="models" to see model configuration
```

**Get integration docs:**
```
Use agno_integrations with integration_type="database", name="postgres"
```

**Check AgentOS docs:**
```
Use agno_agentos with path="features/security"
```

**Migration help:**
```
Use agno_migration with topic="v2-migration"
```

## Tools Reference

### agno_docs

Navigate core Agno documentation.

**Parameters:**
- `paths` (list[str], required) - Documentation paths to fetch
- `query_keywords` (list[str], optional) - Keywords for content matching

**Coverage:** Get Started, Basics (agents, teams, workflows, tools, memory, knowledge), FAQ, How-to guides

### agno_reference

Access API reference documentation.

**Parameters:**
- `topic` (str, required) - Reference topic: agents, teams, workflows, tools, models, memory, knowledge, storage, hooks, compression, reasoning, agent-os
- `query_keywords` (list[str], optional) - Keywords for filtering

### agno_examples

Get code examples and snippets.

**Parameters:**
- `category` (str, optional) - Category: agents, teams, workflows, tools, memory, knowledge, models, database, evals, guardrails, hitl, multimodal, reasoning, sessions, tracing
- `query_keywords` (list[str], optional) - Keywords for searching

### agno_integrations

Access integration guides.

**Parameters:**
- `integration_type` (str, required) - Type: database, vectordb, models, toolkits, memory, observability, discord, testing
- `name` (str, optional) - Specific integration name (e.g., "postgres", "pinecone")
- `query_keywords` (list[str], optional) - Keywords for searching

### agno_agentos

Get AgentOS runtime documentation.

**Parameters:**
- `path` (str, optional) - Path within agent-os docs (e.g., "overview", "features/security")
- `query_keywords` (list[str], optional) - Keywords for searching

### agno_migration

Access migration guides and FAQs.

**Parameters:**
- `topic` (str, optional) - Migration topic: v2-migration, workflows-migration, installation, contributing, cursor-rules, changelog
- `faq_topic` (str, optional) - FAQ topic: agentos-connection, docker-connection, environment, openai-key, rbac-auth, structured-outputs, switching-models, tpm, workflow-vs-team, tableplus
- `query_keywords` (list[str], optional) - Keywords for searching

## Development

### Project Structure

```
agno-docs-mcp/
├── pyproject.toml
├── README.md
├── src/
│   └── agno_docs_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py           # Main MCP server
│       ├── tools/              # Tool implementations
│       │   ├── docs.py
│       │   ├── reference.py
│       │   ├── examples.py
│       │   ├── integrations.py
│       │   ├── agentos.py
│       │   └── migration.py
│       ├── utils/              # Utility modules
│       │   ├── search.py
│       │   ├── paths.py
│       │   └── content.py
│       └── prepare/            # Doc preparation
│           └── prepare_docs.py
├── .docs/                      # Preprocessed docs (generated)
└── tests/
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Building

```bash
pip install build
python -m build
```

## License

MIT

## Links

- [Agno Documentation](https://docs.agno.com)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [MCP Specification](https://modelcontextprotocol.io)
