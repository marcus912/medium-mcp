#!/usr/bin/env python3
"""
Medium MCP Server

A Model Context Protocol server that provides access to Medium articles
and user data through the Medium API.

Note: Publication-related functionality has been removed.

Run with: mcp dev main.py
"""

import sys
from pathlib import Path

# Add src directory to Python path so we can import medium_mcp
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from medium_mcp.server import mcp

if __name__ == "__main__":

    # Run the server
    mcp.run()