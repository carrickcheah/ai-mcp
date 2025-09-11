"""
MCP Prompt System
Model-discoverable prompts with tool binding
"""

# Import all prompt handlers to register them with MCP
from .handlers import sales_prompts

__all__ = ['sales_prompts']