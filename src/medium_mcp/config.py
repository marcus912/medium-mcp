"""Configuration management for Medium MCP server."""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables from .env file
load_dotenv()


class MediumMCPConfig(BaseModel):
    """Configuration for Medium MCP server."""

    rapidapi_key: str = Field(..., description="RapidAPI key for Medium API access")

    max_articles_per_request: int = Field(
        default=3,
        ge=1,
        le=100,
        description="Maximum number of articles to fetch per request",
    )

    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    @field_validator("rapidapi_key")
    @classmethod
    def validate_rapidapi_key(cls, v: str) -> str:
        """Validate RapidAPI key format."""
        if not v or len(v.strip()) < 10:
            raise ValueError("RapidAPI key must be at least 10 characters long")
        return v.strip()

    @classmethod
    def from_env(cls) -> "MediumMCPConfig":
        """Create config from environment variables."""
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if not rapidapi_key:
            raise ValueError(
                "RAPIDAPI_KEY environment variable is required. "
                "Get your key from https://rapidapi.com/nishujain199719-vgIfuFHZxVZ/api/medium2"
            )

        return cls(
            rapidapi_key=rapidapi_key,
            max_articles_per_request=int(os.getenv("MAX_ARTICLES_PER_REQUEST", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )
