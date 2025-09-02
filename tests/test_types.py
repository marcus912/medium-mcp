"""Tests for type definitions."""

import pytest

from medium_mcp.models import (
    ArticleContent,
    MediumArticle,
    MediumComment,
    MediumError,
    MediumUser,
    SearchResult,
)


class TestMediumUser:
    """Test MediumUser type."""

    def test_valid_user_creation(self):
        """Test creating a valid user."""
        user = MediumUser(
            user_id="123456",
            username="testuser",
            fullname="Test User",
            followers_count=1000,
            following_count=500,
        )

        assert user.user_id == "123456"
        assert user.username == "testuser"
        assert user.fullname == "Test User"
        assert user.followers_count == 1000
        assert user.following_count == 500

    def test_user_with_optional_fields(self):
        """Test user with optional fields."""
        user = MediumUser(
            user_id="123456",
            username="testuser",
            fullname="Test User",
            bio="A test user bio",
            followers_count=1000,
            following_count=500,
            twitter_username="testuser_tw",
            image_url="https://example.com/image.jpg",
        )

        assert user.bio == "A test user bio"
        assert user.twitter_username == "testuser_tw"
        assert user.image_url == "https://example.com/image.jpg"


class TestMediumArticle:
    """Test MediumArticle type."""

    def test_valid_article_creation(self):
        """Test creating a valid article."""
        article = MediumArticle(
            article_id="abc123",
            title="Test Article",
            author="testuser",
            published_at="2024-01-01",
            last_modified_at="2024-01-02",
            url="https://medium.com/@testuser/test-article",
            unique_slug="test-article",
        )

        assert article.article_id == "abc123"
        assert article.title == "Test Article"
        assert article.author == "testuser"
        assert article.url == "https://medium.com/@testuser/test-article"

    def test_article_with_metrics(self):
        """Test article with engagement metrics."""
        article = MediumArticle(
            article_id="abc123",
            title="Test Article",
            author="testuser",
            published_at="2024-01-01",
            last_modified_at="2024-01-02",
            url="https://medium.com/@testuser/test-article",
            unique_slug="test-article",
            claps=250,
            voters=45,
            word_count=1500,
            reading_time=6.5,
            responses_count=12,
        )

        assert article.claps == 250
        assert article.voters == 45
        assert article.word_count == 1500
        assert article.reading_time == 6.5
        assert article.responses_count == 12



class TestArticleContent:
    """Test ArticleContent type."""

    def test_valid_content_creation(self):
        """Test creating valid article content."""
        content = ArticleContent(
            title="Test Article",
            content="This is test content",
            content_format="text",
            author="testuser",
            published_at="2024-01-01",
        )

        assert content.title == "Test Article"
        assert content.content == "This is test content"
        assert content.content_format == "text"
        assert content.author == "testuser"


class TestMediumError:
    """Test MediumError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = MediumError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.details == {}

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = MediumError("Not found", status_code=404)

        assert error.status_code == 404

    def test_error_with_details(self):
        """Test error with additional details."""
        details = {"context": "user_lookup", "username": "invalid"}
        error = MediumError("User not found", details=details)

        assert error.details == details


class TestSearchResult:
    """Test SearchResult type."""

    def test_empty_search_result(self):
        """Test creating empty search result."""
        result = SearchResult(query="test query", total_results=0)

        assert result.query == "test query"
        assert result.total_results == 0
        assert result.articles == []
        assert result.users == []

    def test_search_result_with_articles(self):
        """Test search result with articles."""
        article = MediumArticle(
            article_id="abc123",
            title="Test Article",
            author="testuser",
            published_at="2024-01-01",
            last_modified_at="2024-01-02",
            url="https://medium.com/@testuser/test-article",
            unique_slug="test-article",
        )

        result = SearchResult(query="test query", total_results=1, articles=[article])

        assert len(result.articles) == 1
        assert result.articles[0].title == "Test Article"


class TestMediumComment:
    """Test MediumComment type."""

    def test_valid_comment_creation(self):
        """Test creating a valid comment."""
        comment = MediumComment(
            comment_id="comment123",
            author="commenter",
            content="Great article!",
            claps=5,
            created_at="2024-01-01",
        )

        assert comment.comment_id == "comment123"
        assert comment.author == "commenter"
        assert comment.content == "Great article!"
        assert comment.claps == 5
        assert comment.created_at == "2024-01-01"
