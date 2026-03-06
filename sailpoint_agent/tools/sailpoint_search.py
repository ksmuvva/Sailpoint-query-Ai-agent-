"""Custom MCP tool: SailPoint-scoped web search."""

import httpx
from claude_agent_sdk import tool


SAILPOINT_DOMAINS = [
    "developer.sailpoint.com",
    "documentation.sailpoint.com",
    "community.sailpoint.com",
    "github.com/sailpoint-oss",
]


@tool(
    "sailpoint_web_search",
    "Search SailPoint documentation, developer portal, community forums, "
    "and IAM resources. Prioritizes SailPoint official sources. Use for "
    "finding official docs, code examples, API references, and community solutions.",
    {
        "query": str,
        "product": str,
    },
)
async def sailpoint_web_search(args: dict) -> dict:
    """Search SailPoint-scoped domains with automatic query augmentation."""
    query = args["query"]
    product = args.get("product", "both")

    # Augment query with product-specific context
    if product == "iiq":
        query = f"SailPoint IdentityIQ {query}"
    elif product == "isc":
        query = f"SailPoint Identity Security Cloud ISC {query}"
    else:
        query = f"SailPoint {query}"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            results = await _execute_search(client, query)
            formatted = _format_results(results)
            return {"content": [{"type": "text", "text": formatted}]}
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Search failed: {e}. Try using WebSearch directly."}
            ]
        }


async def _execute_search(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Execute web search using configured backend.

    Supports Tavily and SerpAPI. Falls back to returning a hint to use
    the SDK's built-in WebSearch tool if no search backend is configured.
    """
    import os

    search_provider = os.getenv("SEARCH_PROVIDER", "built-in")
    search_api_key = os.getenv("SEARCH_API_KEY", "")

    if search_provider == "tavily" and search_api_key:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": search_api_key,
                "query": query,
                "search_depth": "advanced",
                "include_domains": SAILPOINT_DOMAINS,
                "max_results": 5,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
            }
            for r in data.get("results", [])
        ]

    if search_provider == "serpapi" and search_api_key:
        domain_filter = " OR ".join(f"site:{d}" for d in SAILPOINT_DOMAINS)
        response = await client.get(
            "https://serpapi.com/search",
            params={
                "api_key": search_api_key,
                "q": f"{query} ({domain_filter})",
                "num": 5,
            },
        )
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            }
            for r in data.get("organic_results", [])
        ]

    # No search backend configured — return guidance
    return [
        {
            "title": "No search backend configured",
            "url": "",
            "snippet": (
                "Set SEARCH_PROVIDER (tavily/serpapi) and SEARCH_API_KEY in .env. "
                "Alternatively, use the SDK's built-in WebSearch tool directly."
            ),
        }
    ]


def _format_results(results: list[dict]) -> str:
    """Format search results as readable text."""
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title', 'No title')}")
        if r.get("url"):
            lines.append(f"    URL: {r['url']}")
        lines.append(f"    {r.get('snippet', '')}")
        lines.append("")
    return "\n".join(lines)
