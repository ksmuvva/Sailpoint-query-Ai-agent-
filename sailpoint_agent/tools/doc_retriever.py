"""Custom MCP tool: SailPoint documentation page fetcher."""

import httpx
from claude_agent_sdk import tool


@tool(
    "doc_retriever",
    "Fetch a specific SailPoint documentation page by URL and extract its content "
    "as clean text. Use when you have a specific URL from search results and need "
    "the full page content for detailed information.",
    {
        "url": str,
    },
)
async def doc_retriever(args: dict) -> dict:
    """Fetch and parse a SailPoint documentation page."""
    url = args["url"]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, follow_redirects=True)
            content = _html_to_text(response.text)
            return {
                "content": [
                    {"type": "text", "text": f"Content from {url}:\n\n{content[:5000]}"}
                ]
            }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Failed to fetch {url}: {e}"}]}


def _html_to_text(html: str) -> str:
    """Convert HTML to clean text/markdown."""
    try:
        import html2text

        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0
        return converter.handle(html)
    except ImportError:
        pass

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        return soup.get_text(separator="\n", strip=True)
    except ImportError:
        pass

    # Bare fallback: strip HTML tags
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
