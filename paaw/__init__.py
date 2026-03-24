"""
PAAW - Personal AI Assistant that Works 🐾

A goal-oriented AI assistant with memory that lives on your machine.

Architecture v3:
- Mental Model: Graph-based memory (Apache AGE)
- Conversations: First-class nodes with full history
- Agent: Simple tool-calling loop (like Claude)
- MCP Tools: Direct tool access via MCP protocol
"""

__version__ = "0.3.0"
__author__ = "SivaRamSV"

# Re-export key components for convenience
from paaw.mental_model import MentalModel, get_mental_model

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Mental Model
    "MentalModel",
    "get_mental_model",
]
