"""MCP server implementation for Medium data access.

Available MCP Tools:
- get_user_info: Get detailed user profile information
- get_user_articles: Fetch articles written by a user
- get_article_content: Get full article content in various formats
- get_top_feeds: Get trending articles, optionally filtered by tag
- search_articles: Search articles by keyword/query

Note: Publication-related tools have been removed from this version.
"""

import json
import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP

try:
    # Relative imports (when run as module)
    from .client import MediumClient
    from .config import MediumMCPConfig
    from .models import MediumError
except ImportError:
    # Absolute imports (when run directly)
    from medium_mcp.client import MediumClient
    from medium_mcp.config import MediumMCPConfig
    from medium_mcp.models import MediumError

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("Medium MCP Server", dependencies=["pydantic", "medium-api"])

# Global client instance
client: MediumClient | None = None


def initialize_client() -> None:
    """Initialize the Medium client."""
    global client
    try:
        config = MediumMCPConfig.from_env()
        client = MediumClient(config)
        logger.info("Medium MCP server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Medium MCP server: {e}")
        raise


def ensure_client() -> MediumClient:
    """Ensure client is initialized and return it."""
    if client is None:
        raise MediumError(
            "Medium MCP server not initialized. Check your RAPIDAPI_KEY environment variable."
        )
    return client


@mcp.tool()
def get_user_info(username: str) -> str:
    """Get detailed information about a Medium user.

    Args:
        username: Medium username (without @)

    Returns:
        JSON string with user information
    """
    try:
        medium_client = ensure_client()
        user = medium_client.get_user_info(username)
        return json.dumps(
            user.model_dump() if user else None, indent=2, ensure_ascii=False
        )
    except MediumError as e:
        logger.error(f"Medium API error: {e.message}")
        raise Exception(f"Medium API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error getting user info: {e}")
        raise Exception(f"Error: {str(e)}")


@mcp.tool()
def get_user_articles(username: str, count: int = 3) -> str:
    """Get articles written by a specific Medium user.

    WARNING: This function will consume API requests proportional to the number of
    articles published by the user. The cost increases significantly for prolific
    authors with hundreds or thousands of published articles.

    Args:
        username: Medium username (without @)
        count: Number of articles to fetch (max 100)

    Returns:
        JSON string with user's articles
    """
    try:
        if count < 1 or count > 100:
            raise ValueError("Count must be between 1 and 100")

        medium_client = ensure_client()
        articles = medium_client.get_user_articles(username, count)
        return json.dumps(
            [article.model_dump() for article in articles] if articles else [],
            indent=2,
            ensure_ascii=False,
        )
    except MediumError as e:
        logger.error(f"Medium API error: {e.message}")
        raise Exception(f"Medium API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error getting user articles: {e}")
        raise Exception(f"Error: {str(e)}")


@mcp.tool()
def get_article_content(article_id: str, format: str = "text") -> str:
    """Get full content of a Medium article, including member-only stories.
    
    This tool can access the complete content of Medium articles, even those marked as 
    "member-only" that are normally behind a paywall. If you encounter a Medium article 
    URL that shows only a preview due to membership restrictions, you can use this tool 
    to get the full content.
    
    To extract the article ID from a Medium URL:
    - URL format: https://medium.com/[publication]/[title]-[article_id]
    - Example: https://medium.com/coding-nexus/no-more-guesswork-how-autorag-finds-the-best-rag-setup-for-you-6cda0e7c6dca
    - Article ID: 6cda0e7c6dca (the last section after the final hyphen)

    Args:
        article_id: Unique Medium article ID (extract from URL's last section)
        format: Content format - "text" (default), "html", or "markdown"

    Returns:
        JSON string with complete article content including title, content, author, and metadata
    """
    try:
        if format not in ["text", "html", "markdown"]:
            raise ValueError("Format must be 'text', 'html', or 'markdown'")

        medium_client = ensure_client()
        content = medium_client.get_article_content(article_id, format)
        return json.dumps(
            content.model_dump() if content else None, indent=2, ensure_ascii=False
        )
    except MediumError as e:
        logger.error(f"Medium API error: {e.message}")
        raise Exception(f"Medium API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error getting article content: {e}")
        raise Exception(f"Error: {str(e)}")

# Type alias for valid feed modes
FeedMode = Literal["hot", "new", "top_year", "top_month", "top_week", "top_all_time"]

# Extract valid modes from the Literal type for runtime validation
VALID_FEED_MODES = list(FeedMode.__args__)

@mcp.tool()
def get_top_feeds(tag: str = "", mode: FeedMode = "top_month", count: int = 3) -> str:
    """Get top trending articles from Medium.

    Args:
        tag: Optional tag to filter articles (e.g., 'programming', 'ai')
        mode: Article sorting mode (hot, new, top_year, top_month, top_week, top_all_time)
        count: Number of articles to fetch (max 100)

    Returns:
        JSON string with trending articles
    """
    try:
        if count < 1 or count > 100:
            raise ValueError("Count must be between 1 and 100")
        
        # Validate mode parameter
        if mode not in VALID_FEED_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_FEED_MODES)}")

        medium_client = ensure_client()
        articles = medium_client.get_top_feeds(tag, mode, count)
        return json.dumps(
            [article.model_dump() for article in articles] if articles else [],
            indent=2,
            ensure_ascii=False,
        )
    except MediumError as e:
        logger.error(f"Medium API error: {e.message}")
        raise Exception(f"Medium API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error getting top feeds: {e}")
        raise Exception(f"Error: {str(e)}")


@mcp.tool()
def search_articles(query: str, count: int = 3) -> str:
    """Search Medium articles by keyword.

    WARNING: This function makes additional API calls to fetch detailed article information.
    The search results initially contain only article IDs. To get complete article metadata,
    fetch_articles() is called, which makes {count} additional API requests - 1 per article.
    This will consume extra API quota and incur additional costs on your RapidAPI plan.

    Args:
        query: Search query string
        count: Number of results to fetch (max 100)

    Returns:
        JSON string with search results
    """
    try:
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if count < 1 or count > 100:
            raise ValueError("Count must be between 1 and 100")

        medium_client = ensure_client()
        articles = medium_client.search_articles(query, count)
        return json.dumps(
            [article.model_dump() for article in articles] if articles else [],
            indent=2,
            ensure_ascii=False,
        )
    except MediumError as e:
        logger.error(f"Medium API error: {e.message}")
        raise Exception(f"Medium API Error: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error searching articles: {e}")
        raise Exception(f"Error: {str(e)}")


# Initialize client when module is imported (for MCP framework)
try:
    initialize_client()
except Exception as e:
    logger.warning(f"Failed to initialize client during import: {e}")
    # Client will remain None, tools will handle this gracefully
