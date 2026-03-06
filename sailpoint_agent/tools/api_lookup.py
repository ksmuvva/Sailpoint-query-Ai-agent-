"""Custom MCP tool: SailPoint API endpoint lookup."""

import httpx
from claude_agent_sdk import tool

API_DOCS = {
    "iiq": "https://developer.sailpoint.com/docs/api/iiq/",
    "isc": "https://developer.sailpoint.com/docs/api/v3/",
}


@tool(
    "api_lookup",
    "Look up SailPoint API endpoints, methods, parameters, and examples. "
    "Covers IIQ SCIM APIs and ISC V3/v2025 APIs. Returns structured API documentation.",
    {
        "endpoint": str,
        "product": str,
    },
)
async def api_lookup(args: dict) -> dict:
    """Fetch API documentation for specific SailPoint endpoints."""
    endpoint = args["endpoint"]
    product = args.get("product", "isc")
    base_url = API_DOCS.get(product, API_DOCS["isc"])

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(base_url, follow_redirects=True)
            content = _extract_api_content(response.text, endpoint)
            return {"content": [{"type": "text", "text": content}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"API lookup failed: {e}"}]}


def _extract_api_content(html: str, endpoint: str) -> str:
    """Extract API documentation for a specific endpoint from HTML."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Try to find the section relevant to the endpoint
        lines = text.split("\n")
        relevant_lines = []
        capturing = False
        endpoint_lower = endpoint.lower().strip("/")

        for line in lines:
            if endpoint_lower in line.lower():
                capturing = True
            if capturing:
                relevant_lines.append(line)
                if len(relevant_lines) > 50:
                    break

        if relevant_lines:
            return f"API documentation for '{endpoint}':\n\n" + "\n".join(relevant_lines)

        # Fallback: return first portion of text
        return f"Page content (endpoint '{endpoint}' not found in extracted text):\n\n" + "\n".join(lines[:30])

    except ImportError:
        return f"BeautifulSoup not available. Visit {API_DOCS.get('isc', '')}{endpoint} for API docs."
