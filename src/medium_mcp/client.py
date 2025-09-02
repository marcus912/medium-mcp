"""
Medium API client wrapper with error handling.
"""

import logging

from medium_api import Medium

from .config import MediumMCPConfig
from .formatting import convert_to_string, normalize_tag
from .models import (
    ArticleContent,
    MediumArticle,
    MediumError,
    MediumUser,
)
from .utils import safe_getattr

logger = logging.getLogger(__name__)


class MediumClient:
    """Enhanced Medium API client with MCP integration."""

    def __init__(self, config: MediumMCPConfig):
        """Initialize Medium client with configuration."""
        self.config = config
        self.medium = Medium(config.rapidapi_key)

    def _handle_api_error(self, error: Exception, context: str) -> None:
        """Handle API errors consistently."""
        error_msg = f"Medium API error in {context}: {str(error)}"
        logger.error(error_msg)

        if "rate limit" in str(error).lower():
            raise MediumError(
                "Rate limit exceeded. Please try again later.",
                status_code=429,
                details={"context": context},
            )
        elif "unauthorized" in str(error).lower():
            raise MediumError(
                "Invalid RapidAPI key. Please check your configuration.",
                status_code=401,
                details={"context": context},
            )
        elif "not found" in str(error).lower():
            raise MediumError(
                f"Resource not found: {context}",
                status_code=404,
                details={"context": context},
            )
        else:
            raise MediumError(
                error_msg, details={"context": context, "original_error": str(error)}
            )

    def get_user_info(self, username: str) -> MediumUser | None:
        """Get detailed user information."""
        try:
            user = self.medium.user(username=username)

            return MediumUser(
                user_id=getattr(user, "user_id", ""),
                username=user.username,
                fullname=user.fullname,
                bio=getattr(user, "bio", None),
                followers_count=user.followers_count,
                following_count=getattr(user, "following_count", 0),
                twitter_username=getattr(user, "twitter_username", None),
                image_url=getattr(user, "image_url", None),
                medium_member_at=convert_to_string(
                    getattr(user, "medium_member_at", None)
                ),
                is_writer_program_enrolled=getattr(
                    user, "is_writer_program_enrolled", False
                ),
                has_list=getattr(user, "has_list", False),
                is_suspended=getattr(user, "is_suspended", False),
            )
        except Exception as e:
            self._handle_api_error(e, f"getting user info for {username}")
            return None

    def get_user_articles(
        self, username: str, count: int
    ) -> list[MediumArticle] | None:
        """Get user's articles."""
        try:
            user = self.medium.user(username=username)
            user.fetch_articles()

            articles = []
            article_limit = min(count, self.config.max_articles_per_request)

            for article in user.articles[:article_limit]:
                articles.append(
                    MediumArticle(
                        article_id=getattr(article, "article_id", ""),
                        title=article.title,
                        subtitle=getattr(article, "subtitle", None),
                        author=username,
                        published_at=convert_to_string(
                            getattr(article, "published_at", "")
                        ),
                        last_modified_at=convert_to_string(
                            getattr(article, "last_modified_at", "")
                        ),
                        tags=getattr(article, "tags", []),
                        topics=getattr(article, "topics", []),
                        claps=getattr(article, "claps", 0),
                        voters=getattr(article, "voters", 0),
                        word_count=getattr(article, "word_count", 0),
                        reading_time=getattr(article, "reading_time", 0.0),
                        responses_count=getattr(article, "responses_count", 0),
                        url=article.url,
                        unique_slug=getattr(article, "unique_slug", ""),
                        is_locked=getattr(article, "is_locked", False),
                        is_shortform=getattr(article, "is_shortform", False),
                        language=getattr(article, "language", "en"),
                    )
                )

            return articles
        except Exception as e:
            self._handle_api_error(e, f"getting articles for user {username}")
            return None

    def get_article_content(
        self, article_id: str, content_format: str = "markdown"
    ) -> ArticleContent | None:
        """Get article content in specified format."""
        try:
            article = self.medium.article(article_id=article_id)

            if content_format == "html":
                content = article.html
            elif content_format == "markdown":
                content = article.markdown
            else:
                content = article.content

            # Get author safely
            author_value = getattr(article, "author", None)
            if author_value is None:
                author_value = ""

            # Get published_at safely
            published_at_value = getattr(article, "published_at", None)
            if published_at_value is None:
                published_at_value = ""

            return ArticleContent(
                title=article.title or "",
                subtitle=getattr(article, "subtitle", None),
                content=content or "",
                content_format=content_format,
                author=convert_to_string(author_value),
                published_at=convert_to_string(published_at_value),
            )
        except Exception as e:
            self._handle_api_error(e, f"getting content for article {article_id}")
            return None

    def get_top_feeds(
        self, tag: str | None, mode: str, count: int
    ) -> list[MediumArticle] | None:
        """Get top feed articles, optionally filtered by tag."""
        try:
            top_feeds = self.medium.topfeeds(tag=normalize_tag(tag), mode=mode)
            results = top_feeds.articles

            # Limit results to top count items
            article_limit = min(count, self.config.max_articles_per_request)
            results = results[:article_limit]
            self.medium.fetch_articles(results, html_fullpage=False)
            articles = []
            for article in results:
                articles.append(
                    MediumArticle(
                        article_id=getattr(article, "article_id", ""),
                        title=article.title,
                        subtitle=getattr(article, "subtitle", None),
                        author=convert_to_string(getattr(article, "author", "")),
                        published_at=convert_to_string(
                            getattr(article, "published_at", "")
                        ),
                        last_modified_at=convert_to_string(
                            getattr(article, "last_modified_at", "")
                        ),
                        tags=getattr(article, "tags", []),
                        topics=getattr(article, "topics", []),
                        claps=getattr(article, "claps", 0),
                        voters=getattr(article, "voters", 0),
                        word_count=getattr(article, "word_count", 0),
                        reading_time=getattr(article, "reading_time", 0.0),
                        responses_count=getattr(article, "responses_count", 0),
                        url=article.url,
                        unique_slug=getattr(article, "unique_slug", ""),
                        is_locked=getattr(article, "is_locked", False),
                        is_shortform=getattr(article, "is_shortform", False),
                        language=getattr(article, "language", "en"),
                    )
                )

            return articles
        except Exception as e:
            self._handle_api_error(e, f"getting top feeds for tag {tag}")
            return None

    def search_articles(self, query: str, count: int) -> list[MediumArticle] | None:
        try:
            # Note: Medium API search_articles doesn't support count parameter
            results = self.medium.search_articles(query=query)

            # Limit results to top count items
            article_limit = min(count, self.config.max_articles_per_request)
            results = results[:article_limit]
            self.medium.fetch_articles(results, html_fullpage=False)

            articles = []
            for article in results:
                articles.append(
                    MediumArticle(
                        article_id=safe_getattr(article, "article_id", ""),
                        title=safe_getattr(article, "title", ""),
                        subtitle=safe_getattr(article, "subtitle", None),
                        author=convert_to_string(safe_getattr(article, "author", "")),
                        published_at=convert_to_string(
                            safe_getattr(article, "published_at", "")
                        ),
                        last_modified_at=convert_to_string(
                            safe_getattr(article, "last_modified_at", "")
                        ),
                        tags=safe_getattr(article, "tags", []),
                        topics=safe_getattr(article, "topics", []),
                        claps=safe_getattr(article, "claps", 0),
                        voters=safe_getattr(article, "voters", 0),
                        word_count=safe_getattr(article, "word_count", 0),
                        reading_time=safe_getattr(article, "reading_time", 0.0),
                        responses_count=safe_getattr(article, "responses_count", 0),
                        url=safe_getattr(article, "url", ""),
                        unique_slug=safe_getattr(article, "unique_slug", ""),
                        is_locked=safe_getattr(article, "is_locked", False),
                        is_shortform=safe_getattr(article, "is_shortform", False),
                        language=safe_getattr(article, "language", "en"),
                    )
                )

            return articles
        except Exception as e:
            self._handle_api_error(e, f"searching articles with query: {query}")
            return None
