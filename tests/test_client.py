"""Tests for Medium API client wrapper."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from medium_mcp.client import MediumClient
from medium_mcp.config import MediumMCPConfig
from medium_mcp.models import MediumError, MediumUser, MediumArticle, ArticleContent


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return MediumMCPConfig(
        rapidapi_key="test_api_key_123456789012345",
        max_articles_per_request=5
    )


@pytest.fixture
def mock_medium_api():
    """Mock Medium API instance."""
    return Mock()


@pytest.fixture 
def client(mock_config, mock_medium_api):
    """Create MediumClient instance with mocked dependencies."""
    with patch('medium_mcp.client.Medium', return_value=mock_medium_api):
        return MediumClient(mock_config)


class TestMediumClient:
    """Test MediumClient initialization."""

    def test_client_initialization(self, mock_config):
        """Test client initializes correctly."""
        with patch('medium_mcp.client.Medium') as mock_medium:
            client = MediumClient(mock_config)
            
            assert client.config == mock_config
            mock_medium.assert_called_once_with(mock_config.rapidapi_key)


class TestGetUserInfo:
    """Test get_user_info method."""

    def test_get_user_info_success(self, client, mock_medium_api):
        """Test successful user info retrieval."""
        # Mock API response - need to use configure_mock for getattr compatibility
        mock_user = Mock()
        mock_user.configure_mock(**{
            'user_id': 'user123',
            'username': 'testuser',
            'fullname': 'Test User',
            'bio': None,
            'followers_count': 1000,
            'following_count': 500,
            'twitter_username': None,
            'image_url': None,
            'medium_member_at': None,
            'is_writer_program_enrolled': False,
            'has_list': False,
            'is_suspended': False,
        })
        mock_medium_api.user.return_value = mock_user

        result = client.get_user_info("testuser")

        assert isinstance(result, MediumUser)
        assert result.username == "testuser"
        assert result.fullname == "Test User"
        assert result.followers_count == 1000
        mock_medium_api.user.assert_called_once_with(username="testuser")

    def test_get_user_info_with_optional_fields(self, client, mock_medium_api):
        """Test user info with optional fields."""
        mock_user = Mock()
        mock_user.configure_mock(**{
            'user_id': 'user123',
            'username': 'testuser',
            'fullname': 'Test User',
            'bio': 'Test bio',
            'followers_count': 1000,
            'following_count': 500,
            'twitter_username': 'testuser_tw',
            'image_url': 'https://example.com/image.jpg',
            'medium_member_at': datetime(2024, 1, 1),
            'is_writer_program_enrolled': True,
            'has_list': True,
            'is_suspended': False,
        })
        mock_medium_api.user.return_value = mock_user

        result = client.get_user_info("testuser")

        assert result.bio == "Test bio"
        assert result.twitter_username == "testuser_tw"
        assert "2024-01-01" in result.medium_member_at

    def test_get_user_info_api_error(self, client, mock_medium_api):
        """Test API error handling."""
        mock_medium_api.user.side_effect = Exception("User not found")

        with patch.object(client, '_handle_api_error') as mock_handle_error:
            mock_handle_error.side_effect = MediumError("User not found", status_code=404)
            
            with pytest.raises(MediumError, match="User not found"):
                client.get_user_info("nonexistent")
            mock_handle_error.assert_called_once()


class TestGetUserArticles:
    """Test get_user_articles method."""

    def test_get_user_articles_success(self, client, mock_medium_api):
        """Test successful user articles retrieval."""
        # Mock user and articles with proper attributes
        mock_user = Mock()
        mock_user.fetch_articles = Mock()
        mock_article = Mock()
        mock_article.configure_mock(**{
            'article_id': 'article123',
            'title': 'Test Article',
            'subtitle': None,
            'published_at': '2024-01-01',
            'last_modified_at': '2024-01-02',
            'tags': [],
            'topics': [],
            'claps': 100,
            'voters': 10,
            'word_count': 500,
            'reading_time': 2.5,
            'responses_count': 5,
            'url': 'https://medium.com/test',
            'unique_slug': 'test-article',
            'is_locked': False,
            'is_shortform': False,
            'language': 'en',
        })
        mock_user.articles = [mock_article]
        mock_medium_api.user.return_value = mock_user

        result = client.get_user_articles("testuser", 3)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], MediumArticle)
        assert result[0].title == "Test Article"
        mock_user.fetch_articles.assert_called_once()

    def test_get_user_articles_count_limit(self, client, mock_medium_api):
        """Test article count limiting."""
        mock_user = Mock()
        mock_user.fetch_articles = Mock()
        # Create more articles than requested with all required fields
        mock_articles = []
        for i in range(10):
            mock_article = Mock()
            mock_article.configure_mock(**{
                'article_id': f'article{i}',
                'title': f'Article {i}',
                'subtitle': None,
                'published_at': '2024-01-01',
                'last_modified_at': '2024-01-02',
                'tags': [],
                'topics': [],
                'claps': 100,
                'voters': 10,
                'word_count': 500,
                'reading_time': 2.5,
                'responses_count': 5,
                'url': f'https://medium.com/article{i}',
                'unique_slug': f'article-{i}',
                'is_locked': False,
                'is_shortform': False,
                'language': 'en',
            })
            mock_articles.append(mock_article)
        
        mock_user.articles = mock_articles
        mock_medium_api.user.return_value = mock_user

        result = client.get_user_articles("testuser", 3)

        # Should only return 3 articles
        assert len(result) == 3

    def test_get_user_articles_max_limit(self, client, mock_medium_api):
        """Test max articles per request limit."""
        mock_user = Mock()
        mock_user.fetch_articles = Mock()
        mock_articles = []
        for i in range(10):
            mock_article = Mock()
            mock_article.configure_mock(**{
                'article_id': f'article{i}',
                'title': 'Test',
                'subtitle': None,
                'published_at': '2024-01-01',
                'last_modified_at': '2024-01-02',
                'tags': [],
                'topics': [],
                'claps': 100,
                'voters': 10,
                'word_count': 500,
                'reading_time': 2.5,
                'responses_count': 5,
                'url': 'https://medium.com/test',
                'unique_slug': f'test-{i}',
                'is_locked': False,
                'is_shortform': False,
                'language': 'en',
            })
            mock_articles.append(mock_article)
        
        mock_user.articles = mock_articles
        mock_medium_api.user.return_value = mock_user

        # Request more than max_articles_per_request (5)
        result = client.get_user_articles("testuser", 10)

        # Should be limited to config.max_articles_per_request
        assert len(result) == 5


class TestGetArticleContent:
    """Test get_article_content method."""

    def test_get_article_content_markdown(self, client, mock_medium_api):
        """Test article content in markdown format."""
        mock_article = Mock()
        mock_article.configure_mock(**{
            'title': 'Test Article',
            'subtitle': None,
            'markdown': '# Test Content',
            'author': 'testuser',
            'published_at': '2024-01-01'
        })
        mock_medium_api.article.return_value = mock_article

        result = client.get_article_content("abc123", "markdown")

        assert isinstance(result, ArticleContent)
        assert result.title == "Test Article"
        assert result.content == "# Test Content"
        assert result.content_format == "markdown"
        mock_medium_api.article.assert_called_once_with(article_id="abc123")

    def test_get_article_content_html(self, client, mock_medium_api):
        """Test article content in HTML format."""
        mock_article = Mock()
        mock_article.configure_mock(**{
            'title': 'Test Article',
            'subtitle': None,
            'html': '<h1>Test Content</h1>',
            'author': 'testuser',
            'published_at': '2024-01-01'
        })
        mock_medium_api.article.return_value = mock_article

        result = client.get_article_content("abc123", "html")

        assert result.content == "<h1>Test Content</h1>"
        assert result.content_format == "html"

    def test_get_article_content_text(self, client, mock_medium_api):
        """Test article content in text format."""
        mock_article = Mock()
        mock_article.configure_mock(**{
            'title': 'Test Article',
            'subtitle': None,
            'content': 'Test Content',
            'author': 'testuser',
            'published_at': '2024-01-01'
        })
        mock_medium_api.article.return_value = mock_article

        result = client.get_article_content("abc123", "text")

        assert result.content == "Test Content"
        assert result.content_format == "text"

    def test_get_article_content_safe_handling(self, client, mock_medium_api):
        """Test safe handling of None values."""
        mock_article = Mock()
        mock_article.configure_mock(**{
            'title': 'Test Article',
            'subtitle': None,
            'content': 'Test Content',
            'author': None,  # Test None handling
            'published_at': None  # Test None handling
        })
        mock_medium_api.article.return_value = mock_article

        result = client.get_article_content("abc123", "text")

        assert result.author == ""  # Should be converted to empty string
        assert result.published_at == ""  # Should be converted to empty string


class TestGetTopFeeds:
    """Test get_top_feeds method."""

    def test_get_top_feeds_success(self, client, mock_medium_api):
        """Test successful top feeds retrieval."""
        # Mock top feeds response
        mock_feeds = Mock()
        mock_article = Mock()
        mock_article.configure_mock(**{
            'article_id': 'trending123',
            'title': 'Trending Article',
            'subtitle': None,
            'author': 'trendy_author',
            'published_at': '2024-01-01',
            'last_modified_at': '2024-01-02',
            'tags': [],
            'topics': [],
            'claps': 500,
            'voters': 50,
            'word_count': 1000,
            'reading_time': 4.0,
            'responses_count': 20,
            'url': 'https://medium.com/trending',
            'unique_slug': 'trending-article',
            'is_locked': False,
            'is_shortform': False,
            'language': 'en',
        })
        mock_feeds.articles = [mock_article]
        
        mock_medium_api.topfeeds.return_value = mock_feeds
        mock_medium_api.fetch_articles = Mock()

        result = client.get_top_feeds("programming", "hot", 3)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].title == "Trending Article"
        mock_medium_api.topfeeds.assert_called_once_with(tag="programming", mode="hot")
        mock_medium_api.fetch_articles.assert_called_once_with([mock_article], html_fullpage=False)

    def test_get_top_feeds_tag_normalization(self, client, mock_medium_api):
        """Test tag normalization in get_top_feeds."""
        mock_feeds = Mock()
        mock_feeds.articles = []
        mock_medium_api.topfeeds.return_value = mock_feeds
        mock_medium_api.fetch_articles = Mock()

        client.get_top_feeds("Data Science", "hot", 3)

        # Should normalize "Data Science" to "data-science"
        mock_medium_api.topfeeds.assert_called_once_with(tag="data-science", mode="hot")

    def test_get_top_feeds_no_tag(self, client, mock_medium_api):
        """Test get_top_feeds with no tag specified."""
        mock_feeds = Mock()
        mock_feeds.articles = []
        mock_medium_api.topfeeds.return_value = mock_feeds
        mock_medium_api.fetch_articles = Mock()

        client.get_top_feeds(None, "hot", 3)

        mock_medium_api.topfeeds.assert_called_once_with(tag=None, mode="hot")


class TestSearchArticles:
    """Test search_articles method."""

    def test_search_articles_success(self, client, mock_medium_api):
        """Test successful article search."""
        mock_article = Mock()
        mock_article.configure_mock(**{
            'article_id': 'search123',
            'title': 'Search Result',
            'subtitle': None,
            'author': 'search_author',
            'published_at': '2024-01-01',
            'last_modified_at': '2024-01-02',
            'tags': [],
            'topics': [],
            'claps': 50,
            'voters': 5,
            'word_count': 800,
            'reading_time': 3.2,
            'responses_count': 8,
            'url': 'https://medium.com/search',
            'unique_slug': 'search-result',
            'is_locked': False,
            'is_shortform': False,
            'language': 'en',
        })
        mock_medium_api.search_articles.return_value = [mock_article]
        mock_medium_api.fetch_articles = Mock()

        result = client.search_articles("python programming", 5)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].title == "Search Result"
        mock_medium_api.search_articles.assert_called_once_with(query="python programming")
        mock_medium_api.fetch_articles.assert_called_once()

    def test_search_articles_count_limit(self, client, mock_medium_api):
        """Test search results count limiting."""
        # Create more results than requested with all required fields
        mock_articles = []
        for i in range(10):
            mock_article = Mock()
            mock_article.configure_mock(**{
                'article_id': f'result{i}',
                'title': f'Result {i}',
                'subtitle': None,
                'author': 'result_author',
                'published_at': '2024-01-01',
                'last_modified_at': '2024-01-02',
                'tags': [],
                'topics': [],
                'claps': 25,
                'voters': 3,
                'word_count': 400,
                'reading_time': 1.5,
                'responses_count': 2,
                'url': f'https://medium.com/result{i}',
                'unique_slug': f'result-{i}',
                'is_locked': False,
                'is_shortform': False,
                'language': 'en',
            })
            mock_articles.append(mock_article)
        
        mock_medium_api.search_articles.return_value = mock_articles
        mock_medium_api.fetch_articles = Mock()

        result = client.search_articles("test", 3)

        # Should only return 3 results
        assert len(result) == 3


class TestErrorHandling:
    """Test error handling in client."""

    def test_handle_api_error_rate_limit(self, client):
        """Test rate limit error handling."""
        error = Exception("rate limit exceeded")
        
        with pytest.raises(MediumError) as exc_info:
            client._handle_api_error(error, "test context")
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_handle_api_error_unauthorized(self, client):
        """Test unauthorized error handling."""
        error = Exception("unauthorized access")
        
        with pytest.raises(MediumError) as exc_info:
            client._handle_api_error(error, "test context")
        
        assert exc_info.value.status_code == 401
        assert "Invalid RapidAPI key" in str(exc_info.value)

    def test_handle_api_error_not_found(self, client):
        """Test not found error handling."""
        error = Exception("not found")
        
        with pytest.raises(MediumError) as exc_info:
            client._handle_api_error(error, "test context")
        
        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)

    def test_handle_api_error_generic(self, client):
        """Test generic error handling."""
        error = Exception("unknown error")
        
        with pytest.raises(MediumError) as exc_info:
            client._handle_api_error(error, "test context")
        
        assert "unknown error" in str(exc_info.value)
        assert exc_info.value.details["context"] == "test context"


class TestFormattingIntegration:
    """Test integration with formatting utilities."""

    def test_normalize_tag_integration(self, client, mock_medium_api):
        """Test that normalize_tag is properly used."""
        mock_feeds = Mock()
        mock_feeds.articles = []
        mock_medium_api.topfeeds.return_value = mock_feeds

        # Test various tag formats
        test_cases = [
            ("Machine Learning", "machine-learning"),
            ("DATA SCIENCE", "data-science"),
            ("AI", "ai"),
            ("", ""),
        ]

        for input_tag, expected_tag in test_cases:
            mock_medium_api.reset_mock()
            client.get_top_feeds(input_tag, "hot", 1)
            
            if expected_tag:
                mock_medium_api.topfeeds.assert_called_with(tag=expected_tag, mode="hot")
            else:
                mock_medium_api.topfeeds.assert_called_with(tag="", mode="hot")

    def test_convert_to_string_integration(self, client, mock_medium_api):
        """Test that convert_to_string is properly used."""
        mock_user = Mock()
        mock_user.configure_mock(**{
            'user_id': 'user123',
            'username': 'testuser',
            'fullname': 'Test User',
            'bio': None,
            'followers_count': 1000,
            'following_count': 500,
            'twitter_username': None,
            'image_url': None,
            'medium_member_at': datetime(2024, 1, 1, 10, 30, 45),
            'is_writer_program_enrolled': False,
            'has_list': False,
            'is_suspended': False,
        })
        mock_medium_api.user.return_value = mock_user

        result = client.get_user_info("testuser")

        # Should convert datetime to ISO format string
        assert result.medium_member_at == "2024-01-01T10:30:45"