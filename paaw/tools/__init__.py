"""
PAAW Tools - MCP integration and tool registry.

Handles:
- Loading MCP server configurations
- Tracking available tools
- (Future) Starting MCP servers and calling tools
"""

from paaw.tools.registry import ToolRegistry, Tool

__all__ = ["ToolRegistry", "Tool"]
