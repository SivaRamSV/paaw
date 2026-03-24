"""
Conversation History Tools for PAAW Agent.

These tools allow the agent to access past conversation history on demand,
rather than always loading it into context.
"""

import json
import structlog
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from tzlocal import get_localzone

if TYPE_CHECKING:
    from paaw.mental_model.graph import GraphDB

logger = structlog.get_logger()


class ConversationTools:
    """
    Tools for accessing conversation history.
    
    The agent can call these tools when it needs to:
    - Look up what was discussed on a specific date
    - Search past conversations for a topic
    - List recent conversations
    """
    
    def __init__(self, db: "GraphDB", user_id: str):
        self.db = db
        self.user_id = user_id
        # Get timezone from system - no hardcoding!
        self._tz = get_localzone()
    
    def _get_local_date_str(self) -> str:
        """Get current date string in system's local timezone."""
        return datetime.now(self._tz).strftime("%Y-%m-%d")
    
    async def get_conversation_by_date(self, date_str: str) -> dict:
        """
        Get conversation details for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format, or "today", "yesterday"
            
        Returns:
            Dict with messages, summaries, and metadata
        """
        # Handle relative dates using system's local time
        if date_str.lower() == "today":
            date_str = self._get_local_date_str()
        elif date_str.lower() == "yesterday":
            yesterday = datetime.now(self._tz) - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
        
        conv_id = f"conv_{self.user_id}_{date_str}"
        
        try:
            node = await self.db.get_node(conv_id)
            if node is None:
                return {
                    "found": False,
                    "date": date_str,
                    "message": f"No conversation found for {date_str}"
                }
            
            attrs = node.attributes if hasattr(node, 'attributes') else {}
            
            messages = attrs.get("messages", [])
            if isinstance(messages, str):
                messages = json.loads(messages)
            
            summaries = attrs.get("summaries", [])
            if isinstance(summaries, str):
                summaries = json.loads(summaries)
            
            # Format messages for agent consumption
            formatted_messages = []
            for msg in messages[-20:]:  # Last 20 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:500]  # Truncate long messages
                timestamp = msg.get("timestamp", "")
                formatted_messages.append({
                    "role": role,
                    "content": content,
                    "time": timestamp.split("T")[1][:5] if "T" in timestamp else ""
                })
            
            # Get summary text
            summary_text = ""
            if summaries:
                summary_text = "\n".join([s.get("summary", "") for s in summaries[-3:]])
            
            return {
                "found": True,
                "date": date_str,
                "message_count": attrs.get("message_count", len(messages)),
                "summaries": summary_text,
                "recent_messages": formatted_messages,
                "topics_discussed": self._extract_topics(messages, summaries)
            }
            
        except Exception as e:
            logger.error("Failed to get conversation", date=date_str, error=str(e))
            return {
                "found": False,
                "date": date_str,
                "error": str(e)
            }
    
    async def list_recent_conversations(self, limit: int = 7) -> list[dict]:
        """
        List recent conversations with summaries.
        
        Args:
            limit: Number of recent conversations to return
            
        Returns:
            List of conversation summaries
        """
        try:
            query = f"""
                MATCH (c:Conversation)
                WHERE c.id STARTS WITH 'conv_{self.user_id}_'
                RETURN c
                ORDER BY c.date DESC
                LIMIT {limit}
            """
            
            results = await self.db._cypher(query)
            conversations = []
            
            for node in results:
                props = node.get('properties', {}) if isinstance(node, dict) else {}
                
                summaries = props.get("summaries", [])
                if isinstance(summaries, str):
                    summaries = json.loads(summaries)
                
                # Get latest summary or generate brief
                preview = "No summary available"
                if summaries:
                    preview = summaries[-1].get("summary", "")[:200]
                
                conversations.append({
                    "date": props.get("date", "unknown"),
                    "message_count": props.get("message_count", 0),
                    "preview": preview
                })
            
            return conversations
            
        except Exception as e:
            logger.error("Failed to list conversations", error=str(e))
            return []
    
    async def search_conversations(self, query: str, limit: int = 5) -> list[dict]:
        """
        Search past conversations for a topic/keyword.
        
        Args:
            query: Search term
            limit: Max results
            
        Returns:
            List of matching conversation excerpts
        """
        try:
            # Escape query for Cypher
            escaped_query = query.replace("'", "\\'")
            
            # Search in conversation messages (stored as JSON)
            cypher = f"""
                MATCH (c:Conversation)
                WHERE c.id STARTS WITH 'conv_{self.user_id}_'
                  AND (c.messages CONTAINS '{escaped_query}' OR c.summaries CONTAINS '{escaped_query}')
                RETURN c
                ORDER BY c.date DESC
                LIMIT {limit}
            """
            
            results = await self.db._cypher(cypher)
            matches = []
            
            for node in results:
                props = node.get('properties', {}) if isinstance(node, dict) else {}
                
                messages = props.get("messages", [])
                if isinstance(messages, str):
                    messages = json.loads(messages)
                
                # Find matching messages
                matching_excerpts = []
                query_lower = query.lower()
                for msg in messages:
                    content = msg.get("content", "")
                    if query_lower in content.lower():
                        # Get context around match
                        excerpt = content[:300] + "..." if len(content) > 300 else content
                        matching_excerpts.append({
                            "role": msg.get("role"),
                            "excerpt": excerpt
                        })
                
                if matching_excerpts:
                    matches.append({
                        "date": props.get("date", "unknown"),
                        "matches": matching_excerpts[:3]  # Top 3 matches per conversation
                    })
            
            return matches
            
        except Exception as e:
            logger.error("Failed to search conversations", error=str(e))
            return []
    
    def _extract_topics(self, messages: list, summaries: list) -> list[str]:
        """Extract key topics from conversation."""
        topics = set()
        
        # From summaries
        for s in summaries:
            summary = s.get("summary", "")
            # Simple keyword extraction (could be enhanced with NLP)
            for word in summary.split():
                if len(word) > 5 and word[0].isupper():
                    topics.add(word.strip(".,!?"))
        
        return list(topics)[:10]


def get_conversation_tools_schema() -> list[dict]:
    """Get OpenAI-style function schemas for conversation tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_conversation_history",
                "description": "Get what was discussed with the user on a specific date. Use this when user asks 'what did we talk about yesterday/on March 22/last week'. Dates should be in YYYY-MM-DD format or use 'today'/'yesterday'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date to look up. Use YYYY-MM-DD format (e.g., '2026-03-22') or 'today'/'yesterday'"
                        }
                    },
                    "required": ["date"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_recent_conversations",
                "description": "List the user's recent conversation history with brief summaries. Use when user wants to see their conversation history or asks 'what have we been talking about lately'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of recent days to list (default 7)",
                            "default": 7
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_conversation_history",
                "description": "Search past conversations for a specific topic or keyword. Use when user asks 'did I mention X before' or 'what did I say about Y'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The topic or keyword to search for"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
