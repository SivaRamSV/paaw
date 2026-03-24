"""
Core data models for PAAW.

These are the fundamental data structures used throughout the application.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"  # For tool call results


class GoalStatus(str, Enum):
    """Status of a goal."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GoalPriority(str, Enum):
    """Priority level of a goal."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MemoryType(str, Enum):
    """Type of memory."""

    FACT = "fact"  # Factual information about user
    PREFERENCE = "preference"  # User preferences
    EPISODE = "episode"  # Event or experience
    TASK = "task"  # Task-related memory
    SKILL = "skill"  # User skill or ability


class ActionStatus(str, Enum):
    """Status of an action."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class Channel(str, Enum):
    """Communication channel."""

    CLI = "cli"
    WEB = "web"
    TELEGRAM = "telegram"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


# =============================================================================
# Message Models
# =============================================================================


class Attachment(BaseModel):
    """File or media attachment."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    content_type: str
    size: int
    url: str | None = None
    data: bytes | None = None


class UnifiedMessage(BaseModel):
    """
    Unified message format acitsross all channels.

    Every message from any channel (CLI, Web, Telegram, etc.) is normalized
    to this format before processing.
    """

    model_config = {"use_enum_values": True}

    id: str = Field(default_factory=lambda: str(uuid4()))
    channel: Channel
    user_id: str
    content: str
    attachments: list[Attachment] = Field(default_factory=list)
    reply_to: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """A single message in a conversation."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    metadata: dict[str, Any] = Field(default_factory=dict)
    # For tool calling support
    tool_calls: list[dict] | None = None  # When assistant calls tools
    tool_call_id: str | None = None  # When this is a tool response


# =============================================================================
# Goal Models
# =============================================================================


class Goal(BaseModel):
    """A user goal with hierarchical structure."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    description: str | None = None
    parent_id: UUID | None = None
    status: GoalStatus = GoalStatus.ACTIVE
    priority: GoalPriority = GoalPriority.MEDIUM
    progress: float = Field(default=0, ge=0, le=100)
    context_summary: str | None = None
    key_facts: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(tz=None))


class GoalContext(BaseModel):
    """Context loaded for a specific goal."""

    goal: Goal
    recent_conversations: list[list[ChatMessage]] = Field(default_factory=list)
    summary: str | None = None
    key_facts: list[str] = Field(default_factory=list)
    related_memories: list["Memory"] = Field(default_factory=list)
    parent_context: str | None = None  # Light context from parent goal


# =============================================================================
# Memory Models
# =============================================================================


class Memory(BaseModel):
    """A memory stored in the graph."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    goal_id: UUID | None = None
    content: str
    type: MemoryType
    embedding: list[float] | None = None
    strength: float = Field(default=1.0, ge=0, le=1)
    source_channel: str | None = None
    source_message_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(tz=None))


# =============================================================================
# Action Models
# =============================================================================


class Action(BaseModel):
    """An action performed by PAAW (for audit logging)."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID | None = None
    goal_id: UUID | None = None
    action_type: str
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    tool_used: str | None = None
    model_used: str | None = None
    channel: str | None = None
    status: ActionStatus = ActionStatus.PENDING
    error: str | None = None
    attempts: int = 1
    duration_ms: int | None = None
    memory_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))


# =============================================================================
# Response Models
# =============================================================================


class JobRequest(BaseModel):
    """
    Job request from LLM response.
    
    The LLM decides when a job is needed by outputting a <job> tag.
    No hardcoded pattern matching - LLM has full context to decide.
    """
    
    skill: str  # Which skill to use (e.g., "web_researcher")
    mode: str = "immediate"  # "immediate" (run now) or "scheduled" (recurring)
    schedule: str | None = None  # Cron or natural language schedule if mode=scheduled
    description: str = ""  # What the job should do
    
    def is_scheduled(self) -> bool:
        return self.mode == "scheduled"


class AgentResponse(BaseModel):
    """Response from the PAAW agent."""

    content: str
    goal_id: UUID | None = None
    memories_used: list[UUID] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    model_used: str | None = None
    thinking: str | None = None  # Optional chain-of-thought
    metadata: dict[str, Any] = Field(default_factory=dict)
    job_request: JobRequest | None = None  # LLM-decided job request (V2 architecture)


# =============================================================================
# User Models
# =============================================================================


class User(BaseModel):
    """User profile."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    timezone: str = "UTC"
    locale: str = "en"
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=None))


# Forward reference update
GoalContext.model_rebuild()
