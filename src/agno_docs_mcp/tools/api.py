"""REST API endpoint documentation tool for AgentOS."""

import json
from pathlib import Path
from typing import Any


def get_openapi_path() -> Path:
    """Get the path to the OpenAPI spec file."""
    return Path(__file__).parent.parent.parent.parent / ".docs" / "openapi.json"


def load_openapi_spec() -> dict[str, Any] | None:
    """Load the OpenAPI specification."""
    openapi_path = get_openapi_path()
    if not openapi_path.exists():
        return None

    try:
        with open(openapi_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


# Map resource names to path patterns
RESOURCE_PATTERNS = {
    "memory": ["/memories", "/memory_topics", "/user_memory_stats", "/optimize-memories"],
    "memories": ["/memories", "/memory_topics", "/user_memory_stats", "/optimize-memories"],
    "agents": ["/agents"],
    "teams": ["/teams"],
    "workflows": ["/workflows"],
    "sessions": ["/sessions"],
    "knowledge": ["/knowledge", "/content"],
    "evals": ["/evals", "/evaluation"],
    "traces": ["/traces", "/spans"],
    "metrics": ["/metrics"],
    "database": ["/database", "/migrate"],
    "playground": ["/playground"],
}


def get_endpoints_for_resource(spec: dict[str, Any], resource: str) -> list[dict[str, Any]]:
    """Extract endpoints matching a resource pattern."""
    resource_lower = resource.lower()
    patterns = RESOURCE_PATTERNS.get(resource_lower, [f"/{resource_lower}"])

    endpoints = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        # Check if path matches any pattern
        matches = any(pattern in path.lower() for pattern in patterns)
        if not matches:
            continue

        for method, details in methods.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            endpoint = {
                "method": method.upper(),
                "path": path,
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "parameters": [],
                "request_body": None,
                "responses": {},
            }

            # Extract parameters
            for param in details.get("parameters", []):
                endpoint["parameters"].append({
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": param.get("required", False),
                    "description": param.get("description", ""),
                    "type": param.get("schema", {}).get("type", "string"),
                })

            # Extract request body schema
            request_body = details.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})
                endpoint["request_body"] = schema

            # Extract response info
            for status, response in details.get("responses", {}).items():
                endpoint["responses"][status] = response.get("description", "")

            endpoints.append(endpoint)

    return endpoints


def format_endpoint(endpoint: dict[str, Any]) -> str:
    """Format a single endpoint as markdown."""
    lines = []

    # Header with method and path
    lines.append(f"### {endpoint['summary'] or endpoint['path']}")
    lines.append(f"**`{endpoint['method']} {endpoint['path']}`**")
    lines.append("")

    # Description
    if endpoint["description"]:
        lines.append(endpoint["description"])
        lines.append("")

    # Parameters
    if endpoint["parameters"]:
        lines.append("**Parameters:**")
        lines.append("| Name | In | Type | Required | Description |")
        lines.append("|------|----|----|----------|-------------|")
        for param in endpoint["parameters"]:
            required = "Yes" if param["required"] else "No"
            lines.append(f"| `{param['name']}` | {param['in']} | {param['type']} | {required} | {param['description']} |")
        lines.append("")

    # Request body
    if endpoint["request_body"]:
        lines.append("**Request Body:** JSON")
        # Show properties if available
        props = endpoint["request_body"].get("properties", {})
        if props:
            lines.append("| Field | Type | Description |")
            lines.append("|-------|------|-------------|")
            for prop_name, prop_info in props.items():
                prop_type = prop_info.get("type", "any")
                prop_desc = prop_info.get("description", "")
                lines.append(f"| `{prop_name}` | {prop_type} | {prop_desc} |")
        lines.append("")

    # Responses
    if endpoint["responses"]:
        lines.append("**Responses:**")
        for status, desc in endpoint["responses"].items():
            lines.append(f"- `{status}`: {desc}")
        lines.append("")

    return "\n".join(lines)


def format_endpoints_list(endpoints: list[dict[str, Any]], resource: str) -> str:
    """Format a list of endpoints as markdown."""
    if not endpoints:
        return f"No endpoints found for resource: {resource}"

    lines = [
        f"## {resource.title()} API Endpoints",
        "",
        f"Found {len(endpoints)} endpoint(s):",
        "",
    ]

    for endpoint in endpoints:
        lines.append(format_endpoint(endpoint))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def list_all_resources(spec: dict[str, Any]) -> str:
    """List all available API resources."""
    paths = spec.get("paths", {})

    # Group paths by resource
    resources: dict[str, list[str]] = {}
    for path in paths.keys():
        # Extract resource name from path (first segment)
        parts = path.strip("/").split("/")
        if parts:
            resource = parts[0].replace("_", " ").replace("-", " ").title()
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(path)

    lines = [
        "## AgentOS REST API Resources",
        "",
        "Available API resources:",
        "",
    ]

    for resource, paths_list in sorted(resources.items()):
        lines.append(f"### {resource}")
        for path in sorted(set(paths_list))[:5]:  # Show up to 5 paths per resource
            lines.append(f"- `{path}`")
        if len(paths_list) > 5:
            lines.append(f"- ... and {len(paths_list) - 5} more")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Usage:** Call `agno_api(resource=\"memory\")` to get detailed endpoint info.")
    lines.append("")
    lines.append("**Available resources:** " + ", ".join(sorted(RESOURCE_PATTERNS.keys())))

    return "\n".join(lines)


def agno_api(resource: str | None = None, query_keywords: list[str] | None = None) -> str:
    """Get AgentOS REST API endpoint documentation.

    Args:
        resource: API resource to look up (e.g., "memory", "agents", "sessions").
                  Leave empty to list all available resources.
        query_keywords: Optional keywords (unused, for interface compatibility)

    Returns:
        Formatted markdown with endpoint documentation
    """
    spec = load_openapi_spec()

    if spec is None:
        return (
            "OpenAPI specification not found.\n"
            "Run `python -m agno_docs_mcp.prepare` to prepare docs including the API spec."
        )

    # If no resource specified, list all resources
    if not resource or resource.strip() == "":
        return list_all_resources(spec)

    # Get endpoints for the specified resource
    endpoints = get_endpoints_for_resource(spec, resource.strip())
    return format_endpoints_list(endpoints, resource)
