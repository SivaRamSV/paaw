"""
Conversation Persistence for PAAW.

Stores daily conversations in the graph, with smart summarization
to manage context window limits.

Design:
- One conversation node per day per user (using user's LOCAL date)
- Recent messages kept in full (MAX_RECENT_MESSAGES)
- Older messages summarized when threshold crossed
- Summaries are cumulative (cover message ranges)
- Location/timezone metadata stored for context (auto-detected from system)
"""

import json
import structlog
from datetime import datetime
from typing import TYPE_CHECKING

from tzlocal import get_localzone

from paaw.models import ChatMessage, MessageRole
from paaw.mental_model.models import NodeType, EdgeType

if TYPE_CHECKING:
    from paaw.mental_model.graph import GraphDB
    from paaw.brain.llm import LLM

logger = structlog.get_logger()

# Configuration
MAX_RECENT_MESSAGES = 10  # Keep this many messages in full
SUMMARIZE_THRESHOLD = 15   # Trigger summarization when exceeded
SUMMARIZE_BATCH_SIZE = 10  # Messages per summary


def get_system_timezone_info() -> dict:
    """
    Get comprehensive timezone info directly from the system using tzlocal.
    No hardcoding - reads from OS.
    
    Returns:
        dict with: iana_timezone, timezone_abbrev, utc_offset, region, city, local_time, local_date
    """
    try:
        # Get system timezone using tzlocal
        tz = get_localzone()
        iana_tz = str(tz)  # e.g., "Asia/Kolkata"
        
        # Get current time in local timezone
        now = datetime.now(tz)
        
        # Get abbreviation and offset
        tz_abbrev = now.strftime("%Z")  # e.g., "IST"
        utc_offset = now.utcoffset()
        offset_hours = utc_offset.total_seconds() / 3600 if utc_offset else 0
        offset_str = f"UTC{'+' if offset_hours >= 0 else ''}{int(offset_hours)}"
        
        # Extract region/city from IANA timezone (e.g., "Asia" from "Asia/Kolkata")
        region = iana_tz.split('/')[0] if '/' in iana_tz else "Unknown"
        city = iana_tz.split('/')[-1].replace('_', ' ') if '/' in iana_tz else iana_tz
        
        return {
            "iana_timezone": iana_tz,
            "timezone_abbrev": tz_abbrev,
            "utc_offset": offset_str,
            "offset_hours": offset_hours,
            "region": region,
            "city": city,
            "local_time": now.strftime("%H:%M:%S"),
            "local_date": now.strftime("%Y-%m-%d"),
        }
    except Exception as e:
        logger.warning(f"Failed to get timezone info: {e}")
        # Fallback
        now = datetime.now()
        return {
            "iana_timezone": "Unknown",
            "timezone_abbrev": "UTC",
            "utc_offset": "UTC+0",
            "offset_hours": 0,
            "region": "Unknown",
            "city": "Unknown",
            "local_time": now.strftime("%H:%M:%S"),
            "local_date": now.strftime("%Y-%m-%d"),
        }


class ConversationManager:
    """
    Manages conversation persistence and summarization.
    
    Each conversation is stored as a node with:
    - messages: list of recent messages (full content)
    - summaries: list of {summary: str, messages_covered: str, timestamp: str}
    - message_count: total messages in conversation
    - tools_used: list of tool names used
    - channel: where the conversation happened (web, cli, etc.)
    - timezone_info: location/timezone metadata for context
    """
    
    def __init__(self, db: "GraphDB", llm: "LLM" = None):
        self.db = db
        self.llm = llm
        self._cache: dict[str, dict] = {}  # conversation_id -> data
        # Get timezone info from system (no hardcoding!)
        self._tz_info = get_system_timezone_info()
        self._tz = get_localzone()
    
    def _get_local_date(self) -> datetime:
        """Get current date in system's local timezone."""
        return datetime.now(self._tz)
    
    def _get_conversation_id(self, user_id: str, date: datetime = None) -> str:
        """Generate conversation ID for a user and date (uses local date by default)."""
        if date is None:
            date = self._get_local_date()
        date_str = date.strftime("%Y-%m-%d")
        return f"conv_{user_id}_{date_str}"
    
    def get_conversation_id_for_date(self, user_id: str, date_str: str) -> str:
        """Get conversation ID for a specific date string (YYYY-MM-DD)."""
        return f"conv_{user_id}_{date_str}"
    
    async def load_conversation(
        self, 
        user_id: str, 
        date: datetime = None
    ) -> list[ChatMessage]:
        """
        Load today's conversation from graph.
        
        Returns messages ready for LLM context.
        """
        conv_id = self._get_conversation_id(user_id, date)
        
        # Check cache first
        if conv_id in self._cache:
            return self._messages_from_cache(conv_id)
        
        # Load from graph
        try:
            node = await self.db.get_node(conv_id)
            if node is None:
                logger.info("No conversation found", conv_id=conv_id)
                return []
            
            # Get attributes from BaseNode object
            attrs = node.attributes if hasattr(node, 'attributes') else {}
            
            # Parse messages (stored as JSON string in graph)
            messages = attrs.get("messages", [])
            if isinstance(messages, str):
                messages = json.loads(messages)
            
            summaries = attrs.get("summaries", [])
            if isinstance(summaries, str):
                summaries = json.loads(summaries)
            
            tools_used = attrs.get("tools_used", [])
            if isinstance(tools_used, str):
                tools_used = json.loads(tools_used)
            
            # Cache it
            self._cache[conv_id] = {
                "messages": messages,
                "summaries": summaries,
                "message_count": attrs.get("message_count", len(messages)),
                "tools_used": tools_used,
                "channel": attrs.get("channel", "web"),
            }
            
            logger.info(
                "Conversation loaded",
                conv_id=conv_id,
                messages=len(messages),
                summaries=len(summaries),
            )
            
            return self._messages_from_cache(conv_id)
            
        except Exception as e:
            logger.error("Failed to load conversation", conv_id=conv_id, error=str(e))
            return []
    
    def _messages_from_cache(self, conv_id: str) -> list[ChatMessage]:
        """Convert cached messages to ChatMessage objects."""
        data = self._cache.get(conv_id, {})
        messages = data.get("messages", [])
        
        result = []
        for msg in messages:
            result.append(ChatMessage(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else None,
            ))
        
        return result
    
    async def get_conversation_by_date(
        self, 
        user_id: str, 
        date_str: str
    ) -> dict:
        """
        Get conversation data for a specific date.
        
        Args:
            user_id: User ID
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Dict with messages, summaries, message_count, etc.
        """
        conv_id = f"conv_{user_id}_{date_str}"
        
        # Try cache first
        if conv_id in self._cache:
            return self._cache[conv_id]
        
        # Load from graph
        try:
            node = await self.db.get_node(conv_id)
            if node is None:
                logger.info("No conversation found for date", date=date_str)
                return None
            
            attrs = node.attributes if hasattr(node, 'attributes') else {}
            
            messages = attrs.get("messages", [])
            if isinstance(messages, str):
                messages = json.loads(messages)
            
            summaries = attrs.get("summaries", [])
            if isinstance(summaries, str):
                summaries = json.loads(summaries)
            
            return {
                "date": date_str,
                "messages": messages,
                "summaries": summaries,
                "message_count": attrs.get("message_count", len(messages)),
                "channel": attrs.get("channel", "web"),
            }
            
        except Exception as e:
            logger.error("Failed to get conversation by date", date=date_str, error=str(e))
            return None
    
    async def list_conversations(self, user_id: str, limit: int = 10) -> list[dict]:
        """
        List recent conversations for a user.
        
        Returns list of {date, message_count, summary_preview} dicts.
        """
        try:
            # Query all conversation nodes for this user
            query = f"""
                MATCH (c:Conversation)
                WHERE c.id STARTS WITH 'conv_{user_id}_'
                RETURN c
                ORDER BY c.date DESC
                LIMIT {limit}
            """
            
            results = await self.db.query(query)
            conversations = []
            
            for row in results:
                if row and len(row) > 0:
                    node = row[0]
                    attrs = node.get('properties', {}) if isinstance(node, dict) else {}
                    
                    # Parse summaries for preview
                    summaries = attrs.get("summaries", [])
                    if isinstance(summaries, str):
                        summaries = json.loads(summaries)
                    
                    summary_preview = summaries[-1]["summary"][:100] + "..." if summaries else "No summary"
                    
                    conversations.append({
                        "date": attrs.get("date", "unknown"),
                        "message_count": attrs.get("message_count", 0),
                        "summary_preview": summary_preview,
                    })
            
            return conversations
            
        except Exception as e:
            logger.error("Failed to list conversations", error=str(e))
            return []
        
        return result
    
    async def save_message(
        self,
        user_id: str,
        message: ChatMessage,
        channel: str = "web",
        tools_used: list[str] = None,
    ):
        """
        Save a message to the conversation.
        
        Creates the conversation node if it doesn't exist.
        Triggers summarization if threshold exceeded.
        """
        conv_id = self._get_conversation_id(user_id)
        
        # Ensure conversation exists in cache
        if conv_id not in self._cache:
            await self.load_conversation(user_id)
            if conv_id not in self._cache:
                # Create new conversation
                self._cache[conv_id] = {
                    "messages": [],
                    "summaries": [],
                    "message_count": 0,
                    "tools_used": [],
                    "channel": channel,
                }
        
        # Add message to cache
        msg_dict = {
            "role": message.role.value,
            "content": message.content,
            "timestamp": (message.timestamp or datetime.utcnow()).isoformat(),
        }
        self._cache[conv_id]["messages"].append(msg_dict)
        self._cache[conv_id]["message_count"] += 1
        
        # Track tools used
        if tools_used:
            existing = set(self._cache[conv_id]["tools_used"])
            existing.update(tools_used)
            self._cache[conv_id]["tools_used"] = list(existing)
        
        # Check if we need to summarize
        if len(self._cache[conv_id]["messages"]) > SUMMARIZE_THRESHOLD:
            await self._maybe_summarize(conv_id)
        
        # Persist to graph
        await self._persist_conversation(user_id, conv_id)
    
    async def _maybe_summarize(self, conv_id: str):
        """Summarize older messages if we have too many."""
        data = self._cache.get(conv_id)
        if not data:
            return
        
        messages = data["messages"]
        
        if len(messages) <= SUMMARIZE_THRESHOLD:
            return
        
        # Take oldest batch for summarization
        to_summarize = messages[:SUMMARIZE_BATCH_SIZE]
        remaining = messages[SUMMARIZE_BATCH_SIZE:]
        
        # Generate summary
        if self.llm:
            summary_text = await self._generate_summary(to_summarize)
        else:
            # Fallback without LLM
            summary_text = f"[{len(to_summarize)} messages exchanged]"
        
        # Calculate message range covered
        summaries = data["summaries"]
        start_num = sum(
            int(s.get("messages_covered", "0-0").split("-")[1]) 
            for s in summaries
        ) + 1 if summaries else 1
        end_num = start_num + len(to_summarize) - 1
        
        # Add summary
        summaries.append({
            "summary": summary_text,
            "messages_covered": f"{start_num}-{end_num}",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Update cache
        data["messages"] = remaining
        data["summaries"] = summaries
        
        logger.info(
            "Conversation summarized",
            conv_id=conv_id,
            messages_summarized=len(to_summarize),
            remaining=len(remaining),
            total_summaries=len(summaries),
        )
    
    async def _generate_summary(self, messages: list[dict]) -> str:
        """Generate a summary of messages using LLM."""
        try:
            # Format messages for summarization
            formatted = []
            for msg in messages:
                role = "User" if msg["role"] == "user" else "PAAW"
                formatted.append(f"{role}: {msg['content'][:200]}...")
            
            conversation_text = "\n".join(formatted)
            
            prompt = f"""Summarize this conversation excerpt in 1-2 sentences. 
Focus on: topics discussed, actions taken, decisions made.
Be concise but capture the essence.

{conversation_text}

Summary:"""
            
            # Use simple completion
            response = await self.llm.chat(
                messages=[ChatMessage(role=MessageRole.USER, content=prompt)],
                system_prompt="You are a concise summarizer. Write brief, factual summaries.",
            )
            
            return response.strip() if isinstance(response, str) else response.get("content", "").strip()
            
        except Exception as e:
            logger.error("Summary generation failed", error=str(e))
            return f"[{len(messages)} messages exchanged]"
    
    async def _persist_conversation(self, user_id: str, conv_id: str):
        """Persist conversation to graph."""
        data = self._cache.get(conv_id)
        if not data:
            return
        
        try:
            # Check if node exists
            existing = await self.db.get_node(conv_id)
            
            attributes = {
                "messages": data["messages"],
                "summaries": data["summaries"],
                "message_count": data["message_count"],
                "tools_used": data["tools_used"],
                "channel": data["channel"],
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
            }
            
            if existing:
                # Update existing node
                await self.db.update_node(
                    node_id=conv_id,
                    attributes=attributes,
                )
            else:
                # Create new conversation node
                await self.db.create_node(
                    id=conv_id,
                    node_type=NodeType.CONVERSATION,
                    label=f"Conversation {datetime.utcnow().strftime('%Y-%m-%d')}",
                    context="Daily conversation history",
                    attributes=attributes,
                )
                
                # Link to user
                await self.db.create_edge(
                    from_id=user_id,
                    to_id=conv_id,
                    edge_type=EdgeType.HAS_CONVERSATION,
                )
                
                logger.info("Created conversation node", conv_id=conv_id, user_id=user_id)
            
        except Exception as e:
            logger.error("Failed to persist conversation", conv_id=conv_id, error=str(e))
    
    def get_context_for_llm(self, user_id: str) -> str:
        """
        Get conversation context formatted for LLM system prompt.
        
        Returns summaries + recent messages in a readable format.
        """
        conv_id = self._get_conversation_id(user_id)
        data = self._cache.get(conv_id)
        
        if not data:
            return ""
        
        parts = []
        
        # Add summaries as "earlier today" context
        if data["summaries"]:
            parts.append("=== Earlier Today ===")
            for s in data["summaries"]:
                parts.append(f"[Messages {s['messages_covered']}]: {s['summary']}")
        
        # Recent messages are included separately via conversation_history
        # This is just for the system prompt context
        
        return "\n".join(parts) if parts else ""
    
    def clear_cache(self, user_id: str = None):
        """Clear conversation cache."""
        if user_id:
            conv_id = self._get_conversation_id(user_id)
            self._cache.pop(conv_id, None)
        else:
            self._cache.clear()
