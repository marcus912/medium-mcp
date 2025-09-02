"""Tests for MCP server functions."""

import json
import os
from unittest.mock import Mock, patch
import pytest

from medium_mcp.models import MediumError, MediumUser, MediumArticle, ArticleContent
from medium_mcp.server import (
    get_user_info,
    get_user_articles, 
    get_article_content,
    get_top_feeds,
    search_articles,
    VALID_FEED_MODES
)


@pytest.fixture
def mock_user():
    """Mock MediumUser for testing."""
    return MediumUser(
        user_id="123456",
        username="testuser",
        fullname="Test User",
        followers_count=1000,
        following_count=500,
    )


@pytest.fixture
def mock_article():
    """Mock MediumArticle for testing.""" 
    return MediumArticle(
        article_id="abc123",
        title="Test Article",
        author="testuser",
        published_at="2024-01-01",
        last_modified_at="2024-01-02",
        url="https://medium.com/@testuser/test-article",
        unique_slug="test-article",
    )


@pytest.fixture
def mock_article_content():
    """Mock ArticleContent for testing."""
    return ArticleContent(
        title="Test Article",
        content="This is test content",
        content_format="text",
        author="testuser", 
        published_at="2024-01-01",
    )


@pytest.fixture
def setup_env():
    """Setup test environment variables."""
    os.environ['RAPIDAPI_KEY'] = 'test_api_key_123456789012345'
    yield
    # Cleanup
    if 'RAPIDAPI_KEY' in os.environ:
        del os.environ['RAPIDAPI_KEY']


class TestGetUserInfo:
    """Test get_user_info MCP tool."""

    @patch('medium_mcp.server.ensure_client')
    def test_get_user_info_success(self, mock_ensure_client, mock_user, setup_env):
        """Test successful user info retrieval."""
        mock_client = Mock()
        mock_client.get_user_info.return_value = mock_user
        mock_ensure_client.return_value = mock_client

        result = get_user_info("testuser")
        
        # Parse JSON result
        data = json.loads(result)
        
        assert data['username'] == 'testuser'
        assert data['fullname'] == 'Test User'
        assert data['followers_count'] == 1000
        mock_client.get_user_info.assert_called_once_with("testuser")

    @patch('medium_mcp.server.ensure_client')
    def test_get_user_info_not_found(self, mock_ensure_client, setup_env):
        """Test user not found scenario."""
        mock_client = Mock()
        mock_client.get_user_info.return_value = None
        mock_ensure_client.return_value = mock_client

        result = get_user_info("nonexistent_user")
        
        data = json.loads(result)
        assert data is None

    @patch('medium_mcp.server.ensure_client')
    def test_get_user_info_medium_error(self, mock_ensure_client, setup_env):
        """Test Medium API error handling."""
        mock_client = Mock()
        mock_client.get_user_info.side_effect = MediumError("User not found", status_code=404)
        mock_ensure_client.return_value = mock_client

        with pytest.raises(Exception, match="Medium API Error: User not found"):
            get_user_info("testuser")


class TestGetUserArticles:
    """Test get_user_articles MCP tool."""

    @patch('medium_mcp.server.ensure_client')
    def test_get_user_articles_success(self, mock_ensure_client, mock_article, setup_env):
        """Test successful user articles retrieval."""
        mock_client = Mock()
        mock_client.get_user_articles.return_value = [mock_article]
        mock_ensure_client.return_value = mock_client

        result = get_user_articles("testuser", 3)
        
        data = json.loads(result)
        
        assert len(data) == 1
        assert data[0]['title'] == 'Test Article'
        assert data[0]['author'] == 'testuser'
        mock_client.get_user_articles.assert_called_once_with("testuser", 3)

    def test_get_user_articles_invalid_count(self, setup_env):
        """Test invalid count parameter validation."""
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            get_user_articles("testuser", 0)
        
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            get_user_articles("testuser", 101)

    @patch('medium_mcp.server.ensure_client')
    def test_get_user_articles_empty_result(self, mock_ensure_client, setup_env):
        """Test empty articles result."""
        mock_client = Mock()
        mock_client.get_user_articles.return_value = []
        mock_ensure_client.return_value = mock_client

        result = get_user_articles("testuser", 5)
        
        data = json.loads(result)
        assert data == []


class TestGetArticleContent:
    """Test get_article_content MCP tool."""

    @patch('medium_mcp.server.ensure_client')
    def test_get_article_content_success(self, mock_ensure_client, mock_article_content, setup_env):
        """Test successful article content retrieval."""
        mock_client = Mock()
        mock_client.get_article_content.return_value = mock_article_content
        mock_ensure_client.return_value = mock_client

        result = get_article_content("abc123", "text")
        
        data = json.loads(result)
        
        assert data['title'] == 'Test Article'
        assert data['content'] == 'This is test content'
        assert data['content_format'] == 'text'
        mock_client.get_article_content.assert_called_once_with("abc123", "text")

    def test_get_article_content_invalid_format(self, setup_env):
        """Test invalid format parameter validation."""
        with pytest.raises(Exception, match="Format must be 'text', 'html', or 'markdown'"):
            get_article_content("abc123", "invalid")

    @patch('medium_mcp.server.ensure_client')
    def test_get_article_content_default_format(self, mock_ensure_client, mock_article_content, setup_env):
        """Test default format parameter."""
        mock_client = Mock()
        mock_client.get_article_content.return_value = mock_article_content
        mock_ensure_client.return_value = mock_client

        result = get_article_content("abc123")  # No format specified
        
        data = json.loads(result)
        assert data['content_format'] == 'text'
        mock_client.get_article_content.assert_called_once_with("abc123", "text")


class TestGetTopFeeds:
    """Test get_top_feeds MCP tool."""

    @patch('medium_mcp.server.ensure_client')
    def test_get_top_feeds_success(self, mock_ensure_client, mock_article, setup_env):
        """Test successful top feeds retrieval."""
        mock_client = Mock()
        mock_client.get_top_feeds.return_value = [mock_article]
        mock_ensure_client.return_value = mock_client

        result = get_top_feeds("programming", "hot", 5)
        
        data = json.loads(result)
        
        assert len(data) == 1
        assert data[0]['title'] == 'Test Article'
        mock_client.get_top_feeds.assert_called_once_with("programming", "hot", 5)

    @patch('medium_mcp.server.ensure_client')
    def test_get_top_feeds_default_params(self, mock_ensure_client, mock_article, setup_env):
        """Test get_top_feeds with default parameters."""
        mock_client = Mock()
        mock_client.get_top_feeds.return_value = [mock_article]
        mock_ensure_client.return_value = mock_client

        result = get_top_feeds()  # All defaults
        
        data = json.loads(result)
        assert len(data) == 1
        mock_client.get_top_feeds.assert_called_once_with("", "top_month", 3)

    def test_get_top_feeds_invalid_mode(self, setup_env):
        """Test invalid mode parameter validation."""
        with pytest.raises(Exception, match="Invalid mode 'invalid_mode'"):
            get_top_feeds("programming", "invalid_mode", 5)

    def test_get_top_feeds_valid_modes(self, setup_env):
        """Test that all valid modes are accepted."""
        # This test ensures VALID_FEED_MODES matches FeedMode Literal
        expected_modes = ["hot", "new", "top_year", "top_month", "top_week", "top_all_time"]
        assert VALID_FEED_MODES == expected_modes

    def test_get_top_feeds_invalid_count(self, setup_env):
        """Test invalid count parameter validation."""
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            get_top_feeds("programming", "hot", 0)
        
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            get_top_feeds("programming", "hot", 101)


class TestSearchArticles:
    """Test search_articles MCP tool."""

    @patch('medium_mcp.server.ensure_client')
    def test_search_articles_success(self, mock_ensure_client, mock_article, setup_env):
        """Test successful article search."""
        mock_client = Mock()
        mock_client.search_articles.return_value = [mock_article]
        mock_ensure_client.return_value = mock_client

        result = search_articles("python programming", 5)
        
        data = json.loads(result)
        
        assert len(data) == 1
        assert data[0]['title'] == 'Test Article'
        mock_client.search_articles.assert_called_once_with("python programming", 5)

    def test_search_articles_empty_query(self, setup_env):
        """Test empty query validation."""
        with pytest.raises(Exception, match="Search query cannot be empty"):
            search_articles("", 5)
        
        with pytest.raises(Exception, match="Search query cannot be empty"):
            search_articles("   ", 5)

    def test_search_articles_invalid_count(self, setup_env):
        """Test invalid count parameter validation."""
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            search_articles("python", 0)
        
        with pytest.raises(Exception, match="Count must be between 1 and 100"):
            search_articles("python", 101)

    @patch('medium_mcp.server.ensure_client')
    def test_search_articles_no_results(self, mock_ensure_client, setup_env):
        """Test search with no results."""
        mock_client = Mock()
        mock_client.search_articles.return_value = []
        mock_ensure_client.return_value = mock_client

        result = search_articles("very_rare_query", 3)
        
        data = json.loads(result)
        assert data == []


class TestErrorHandling:
    """Test error handling across server functions."""

    @patch('medium_mcp.server.ensure_client')
    def test_client_not_initialized(self, mock_ensure_client):
        """Test behavior when client is not initialized."""
        mock_ensure_client.side_effect = MediumError("Client not initialized")
        
        with pytest.raises(Exception, match="Medium API Error: Client not initialized"):
            get_user_info("testuser")

    @patch('medium_mcp.server.ensure_client')
    def test_unexpected_error_handling(self, mock_ensure_client, setup_env):
        """Test unexpected error handling."""
        mock_client = Mock()
        mock_client.get_user_info.side_effect = RuntimeError("Unexpected error")
        mock_ensure_client.return_value = mock_client

        with pytest.raises(Exception, match="Error: Unexpected error"):
            get_user_info("testuser")