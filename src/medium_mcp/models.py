"""Type definitions for Medium MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class MediumUser(BaseModel):
    """Medium user information."""

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Medium username")
    fullname: str = Field(..., description="User's full name")
    bio: str | None = Field(None, description="User biography")
    followers_count: int = Field(..., description="Number of followers")
    following_count: int = Field(..., description="Number of people following")
    twitter_username: str | None = Field(None, description="Twitter handle")
    image_url: str | None = Field(None, description="Profile image URL")
    medium_member_at: str | None = Field(None, description="Medium membership date")
    is_writer_program_enrolled: bool = Field(False, description="Writer program status")
    has_list: bool = Field(False, description="Has lists")
    is_suspended: bool = Field(False, description="Account suspension status")


class MediumArticle(BaseModel):
    """Medium article information."""

    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    subtitle: str | None = Field(None, description="Article subtitle")
    author: str = Field(..., description="Author username")
    published_at: str = Field(..., description="Publication date")
    last_modified_at: str = Field(..., description="Last modification date")
    tags: list[str] = Field(default_factory=list, description="Article tags")
    topics: list[str] = Field(default_factory=list, description="Article topics")
    claps: int = Field(0, description="Number of claps")
    voters: int = Field(0, description="Number of voters")
    word_count: int = Field(0, description="Word count")
    reading_time: float = Field(0, description="Estimated reading time in minutes")
    responses_count: int = Field(0, description="Number of responses")
    url: str = Field(..., description="Article URL")
    unique_slug: str = Field(..., description="Unique article slug")
    is_locked: bool = Field(False, description="Member-only content")
    is_shortform: bool = Field(False, description="Short form content")
    language: str = Field("en", description="Content language")


class MediumComment(BaseModel):
    """Medium comment/response information."""

    comment_id: str = Field(..., description="Unique comment identifier")
    author: str = Field(..., description="Comment author username")
    content: str = Field(..., description="Comment content")
    claps: int = Field(0, description="Number of claps")
    created_at: str = Field(..., description="Comment creation date")


class ArticleContent(BaseModel):
    """Article content in different formats."""

    title: str = Field(..., description="Article title")
    subtitle: str | None = Field(None, description="Article subtitle")
    content: str = Field(..., description="Article content")
    content_format: str = Field(
        ..., description="Content format (text, html, markdown)"
    )
    author: str = Field(..., description="Author username")
    published_at: str = Field(..., description="Publication date")


class SearchResult(BaseModel):
    """Search results container."""

    query: str = Field(..., description="Search query used")
    total_results: int = Field(..., description="Total number of results")
    articles: list[MediumArticle] = Field(
        default_factory=list, description="Found articles"
    )
    users: list[MediumUser] = Field(default_factory=list, description="Found users")


class MediumError(Exception):
    """Custom exception for Medium API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
