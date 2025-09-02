"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from medium_mcp.config import MediumMCPConfig


class TestMediumMCPConfig:
    """Test configuration management."""

    def test_valid_config_creation(self):
        """Test creating config with valid parameters."""
        config = MediumMCPConfig(
            rapidapi_key="test_key_123456789",
            max_articles_per_request=50,
        )

        assert config.rapidapi_key == "test_key_123456789"
        assert config.max_articles_per_request == 50

    def test_default_values(self):
        """Test default configuration values."""
        config = MediumMCPConfig(rapidapi_key="test_key_123456789")

        assert config.max_articles_per_request == 3

    def test_invalid_rapidapi_key(self):
        """Test validation of RapidAPI key."""
        with pytest.raises(ValidationError):
            MediumMCPConfig(rapidapi_key="")

        with pytest.raises(ValidationError):
            MediumMCPConfig(rapidapi_key="short")

    def test_key_trimming(self):
        """Test RapidAPI key trimming."""
        config = MediumMCPConfig(rapidapi_key="  test_key_123456789  ")
        assert config.rapidapi_key == "test_key_123456789"

    def test_articles_per_request_validation(self):
        """Test validation of max_articles_per_request."""
        with pytest.raises(ValidationError):
            MediumMCPConfig(
                rapidapi_key="test_key_123456789", max_articles_per_request=0
            )

        with pytest.raises(ValidationError):
            MediumMCPConfig(
                rapidapi_key="test_key_123456789", max_articles_per_request=101
            )


    @patch.dict(os.environ, {"RAPIDAPI_KEY": "test_key_from_env"})
    def test_from_env_with_key(self):
        """Test creating config from environment variables."""
        config = MediumMCPConfig.from_env()
        assert config.rapidapi_key == "test_key_from_env"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_without_key(self):
        """Test error when RAPIDAPI_KEY is missing."""
        with pytest.raises(
            ValueError, match="RAPIDAPI_KEY environment variable is required"
        ):
            MediumMCPConfig.from_env()

    @patch.dict(
        os.environ,
        {
            "RAPIDAPI_KEY": "test_key_from_env",
            "MAX_ARTICLES_PER_REQUEST": "50",
        },
    )
    def test_from_env_with_all_values(self):
        """Test creating config from all environment variables."""
        config = MediumMCPConfig.from_env()

        assert config.rapidapi_key == "test_key_from_env"
        assert config.max_articles_per_request == 50
