"""
Tool Registry - Manages MCP tools and their availability.

For Phase 3, this is mostly a "promise" layer - tracking what tools
PAAW thinks it has, with actual MCP integration coming later.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """A tool that PAAW can use."""
    name: str
    server: str  # Which MCP server provides this
    description: str = ""
    input_schema: dict = field(default_factory=dict)
    enabled: bool = False


@dataclass  
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    enabled: bool = False


class ToolRegistry:
    """
    Registry of available tools from MCP servers.
    
    Phase 3: Just tracks what tools exist based on config.
    Future: Actually starts MCP servers and calls tools.
    """
    
    def __init__(self, mcp_config_path: Optional[Path] = None):
        self.servers: dict[str, MCPServerConfig] = {}
        self.tools: dict[str, Tool] = {}
        
        if mcp_config_path:
            self.load_config(mcp_config_path)
    
    def load_config(self, config_path: Path) -> None:
        """Load MCP server configurations from JSON file."""
        if not config_path.exists():
            logger.warning(f"MCP config not found: {config_path}")
            return
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            for name, server_config in config.get("mcpServers", {}).items():
                self.servers[name] = MCPServerConfig(
                    name=name,
                    command=server_config.get("command", ""),
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                    enabled=server_config.get("enabled", False)
                )
                
                # Register known tools for this server
                # In the future, this will be discovered via MCP protocol
                self._register_known_tools(name)
            
            logger.info(f"Loaded {len(self.servers)} MCP server configs")
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
    
    def _register_known_tools(self, server_name: str) -> None:
        """
        Register known tools for a server.
        
        This is a temporary approach - we hardcode known tools for each server.
        In the future, we'll discover tools via MCP protocol.
        """
        server = self.servers.get(server_name)
        if not server:
            return
        
        # Known tools for common MCP servers
        known_tools = {
            "duckduckgo": [
                Tool(
                    name="search",
                    server="duckduckgo",
                    description="Search the web using DuckDuckGo. Returns titles, URLs, and snippets.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "max_results": {"type": "integer", "description": "Max results (default 10)"},
                            "region": {"type": "string", "description": "Region code like us-en, cn-zh"}
                        },
                        "required": ["query"]
                    },
                    enabled=server.enabled
                ),
                Tool(
                    name="fetch_content",
                    server="duckduckgo",
                    description="Fetch and parse content from a webpage URL",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"}
                        },
                        "required": ["url"]
                    },
                    enabled=server.enabled
                )
            ],
            "fetch": [
                Tool(
                    name="fetch",
                    server="fetch",
                    description="Fetch content from a URL",
                    input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
                    enabled=server.enabled
                )
            ],
            "filesystem": [
                Tool(
                    name="read_file",
                    server="filesystem", 
                    description="Read contents of a file",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                    enabled=server.enabled
                ),
                Tool(
                    name="write_file",
                    server="filesystem",
                    description="Write content to a file",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
                    enabled=server.enabled
                ),
                Tool(
                    name="list_directory",
                    server="filesystem",
                    description="List contents of a directory",
                    input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                    enabled=server.enabled
                )
            ],
            "code_executor": [
                Tool(
                    name="execute_python",
                    server="code_executor",
                    description="Execute Python code",
                    input_schema={"type": "object", "properties": {"code": {"type": "string"}}},
                    enabled=server.enabled
                )
            ]
        }
        
        for tool in known_tools.get(server_name, []):
            self.tools[tool.name] = tool
    
    def get_enabled_tools(self) -> list[Tool]:
        """Get list of enabled tools."""
        return [t for t in self.tools.values() if t.enabled]
    
    def get_tools_for_skill(self, tool_names: list[str]) -> list[Tool]:
        """Get tools that a skill wants to use."""
        return [
            self.tools[name] 
            for name in tool_names 
            if name in self.tools
        ]
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        return self.tools.get(name)
    
    def is_tool_available(self, name: str) -> bool:
        """Check if a tool is available and enabled."""
        tool = self.tools.get(name)
        return tool is not None and tool.enabled
    
    def get_tools_context(self) -> str:
        """
        Generate context about available tools for PAAW.
        
        This is included in the system prompt so PAAW knows what tools exist.
        """
        enabled = self.get_enabled_tools()
        
        if not enabled:
            return "No tools are currently enabled."
        
        lines = ["Available tools:"]
        for tool in enabled:
            lines.append(f"- {tool.name}: {tool.description}")
        
        return "\n".join(lines)
    
    async def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Call a tool with given arguments.
        
        Phase 3: Returns a simulated response.
        Future: Actually calls the MCP server.
        """
        tool = self.tools.get(name)
        
        if not tool:
            return {"error": f"Tool not found: {name}"}
        
        if not tool.enabled:
            return {"error": f"Tool not enabled: {name}"}
        
        # For now, return a simulated response
        # This will be replaced with actual MCP calls
        logger.info(f"[SIMULATED] Tool call: {name}({arguments})")
        
        return {
            "simulated": True,
            "tool": name,
            "arguments": arguments,
            "result": f"Simulated result for {name}. MCP integration coming in future phase."
        }


# Singleton instance for the application
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def init_tool_registry(mcp_config_path: Path) -> ToolRegistry:
    """Initialize the global tool registry with config."""
    global _registry
    _registry = ToolRegistry(mcp_config_path)
    return _registry
