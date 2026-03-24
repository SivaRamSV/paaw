"""
Node and Edge type definitions for the Mental Model.

Everything in PAAW's mental model is a node in a graph.
Nodes are connected by typed edges.

Philosophy: Minimal hardcoding. These types exist for:
- Querying (find all Jobs, find all Skills)
- UI rendering (show Jobs differently than Memories)
- Core system logic (scheduler knows what a Job is)

But attributes are flexible - LLM decides what's relevant.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """
    Types of nodes in the mental model.
    
    Core types are hardcoded for system functionality.
    LLM can still use flexible attributes within each type.
    """
    # Core entities
    USER = "User"           # The human user (root)
    ASSISTANT = "Assistant" # PAAW itself
    
    # User's life (emergent from conversations)
    DOMAIN = "Domain"       # Life areas (work, health, etc.)
    PERSON = "Person"       # People in user's life
    PROJECT = "Project"     # Things being worked on
    GOAL = "Goal"           # User's objectives
    MEMORY = "Memory"       # Facts, observations, episodes
    EVENT = "Event"         # Important dates, milestones
    
    # PAAW's work
    SKILL = "Skill"         # Installed skills (from skill.md)
    JOB = "Job"             # Assigned tasks (from job.md)
    TRAIL = "Trail"         # Job execution history
    MCP_SERVER = "MCP_Server" # MCP tool servers
    CONVERSATION = "Conversation"  # Daily conversation history
    
    # Legacy (keeping for compatibility)
    TASK = "Task"           # Simple tasks (may merge with Job)


class EdgeType(str, Enum):
    """
    Types of edges connecting nodes.
    
    Core relationships are hardcoded for querying.
    """
    # Hierarchical
    CHILD_OF = "CHILD_OF"
    HAS_CHILD = "HAS_CHILD"
    
    # Ownership/Membership
    BELONGS_TO = "BELONGS_TO"
    HAS_ASSISTANT = "HAS_ASSISTANT"  # User -> PAAW
    
    # PAAW's capabilities & work
    HAS_SKILL = "HAS_SKILL"          # PAAW -> Skill
    HAS_JOB = "HAS_JOB"              # PAAW -> Job
    HAS_MCP_SERVER = "HAS_MCP_SERVER" # PAAW -> MCP Server
    USES_SKILL = "USES_SKILL"        # Job -> Skill
    SERVES_GOAL = "SERVES_GOAL"      # Job -> Goal
    HAS_TRAIL = "HAS_TRAIL"          # Job -> Trail
    HAS_CONVERSATION = "HAS_CONVERSATION"  # User -> Conversation
    HAS_ALERT = "HAS_ALERT"            # User -> Alert
    
    # Conversation relationships
    DISCUSSES = "DISCUSSES"          # Conversation/Message -> Domain/Project/Topic
    MENTIONS = "MENTIONS"            # Message -> Entity (person, tech, etc.)
    
    # Relationships
    KNOWS = "KNOWS"
    WORKS_ON = "WORKS_ON"
    AFFECTS = "AFFECTS"
    RELATES_TO = "RELATES_TO"
    TRIGGERS = "TRIGGERS"


class BaseNode(BaseModel):
    """
    Base node schema - the skeleton that all nodes share.
    
    Every node has:
    - Identity: id, type, label
    - Understanding: context (LLM-generated), key_facts (bullet points)
    - Metadata: timestamps, access tracking
    - Flexibility: attributes dict for type-specific data
    """
    id: str = Field(..., description="Unique identifier like 'user_siva', 'person_priya'")
    type: NodeType = Field(..., description="Node type")
    label: str = Field(..., description="Display name")
    context: str = Field(default="", description="LLM-generated understanding of this node")
    key_facts: list[str] = Field(default_factory=list, description="Bullet-point facts")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Type-specific attributes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)

    def to_graph_props(self) -> dict[str, Any]:
        """Convert to properties for graph storage."""
        props = {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "context": self.context,
            "key_facts": self.key_facts,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
        }
        # Flatten attributes into props
        props.update(self.attributes)
        return props

    @classmethod
    def from_graph(cls, data: dict[str, Any]) -> "BaseNode":
        """Create node from graph query result."""
        # Extract known fields
        known_fields = {
            "id", "type", "label", "context", "key_facts",
            "created_at", "updated_at", "last_accessed", "access_count"
        }
        
        # Parse timestamps
        for ts_field in ["created_at", "updated_at", "last_accessed"]:
            if ts_field in data and isinstance(data[ts_field], str):
                data[ts_field] = datetime.fromisoformat(data[ts_field].replace("Z", "+00:00"))
        
        # Convert type string to enum
        if "type" in data and isinstance(data["type"], str):
            data["type"] = NodeType(data["type"])
        
        # Everything else goes into attributes
        attributes = {k: v for k, v in data.items() if k not in known_fields}
        
        return cls(
            id=data.get("id", ""),
            type=data.get("type", NodeType.MEMORY),
            label=data.get("label", ""),
            context=data.get("context", ""),
            key_facts=data.get("key_facts", []),
            attributes=attributes,
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
            last_accessed=data.get("last_accessed", datetime.utcnow()),
            access_count=data.get("access_count", 0),
        )


# =============================================================================
# SPECIALIZED NODE TYPES (convenience classes with typed attributes)
# =============================================================================

class UserNode(BaseNode):
    """The root node - represents the user."""
    type: NodeType = NodeType.USER
    
    # User-specific attributes (stored in self.attributes)
    @property
    def location(self) -> str | None:
        return self.attributes.get("location")
    
    @property
    def timezone(self) -> str | None:
        return self.attributes.get("timezone")
    
    @property
    def languages(self) -> list[str]:
        return self.attributes.get("languages", [])
    
    @property
    def response_style(self) -> str | None:
        return self.attributes.get("response_style")


class DomainNode(BaseNode):
    """Life domain - Work, Health, Family, Finance, etc."""
    type: NodeType = NodeType.DOMAIN
    
    @property
    def priority(self) -> str:
        return self.attributes.get("priority", "medium")


class PersonNode(BaseNode):
    """A person in the user's life."""
    type: NodeType = NodeType.PERSON
    
    @property
    def relationship(self) -> str | None:
        return self.attributes.get("relationship")
    
    @property
    def contact_info(self) -> dict[str, str]:
        return self.attributes.get("contact_info", {})


class ProjectNode(BaseNode):
    """A project the user is working on."""
    type: NodeType = NodeType.PROJECT
    
    @property
    def status(self) -> str:
        return self.attributes.get("status", "active")
    
    @property
    def priority(self) -> str:
        return self.attributes.get("priority", "medium")


class GoalNode(BaseNode):
    """A goal the user wants to achieve."""
    type: NodeType = NodeType.GOAL
    
    @property
    def status(self) -> str:
        return self.attributes.get("status", "active")
    
    @property
    def target_date(self) -> str | None:
        return self.attributes.get("target_date")
    
    @property
    def progress(self) -> float:
        return self.attributes.get("progress", 0.0)


class MemoryNode(BaseNode):
    """
    A memory - fact, observation, preference, or episode.
    
    Memory types:
    - fact: Objective information ("User works at TechCorp")
    - observation: Pattern PAAW noticed ("User is a night owl")
    - preference: User preference ("Prefers direct communication")
    - episode: Event/experience ("Had a tough day at work on Jan 5")
    """
    type: NodeType = NodeType.MEMORY
    
    @property
    def memory_type(self) -> str:
        return self.attributes.get("memory_type", "fact")
    
    @property
    def source_channel(self) -> str | None:
        return self.attributes.get("source_channel")
    
    @property
    def emotional_weight(self) -> float:
        return self.attributes.get("emotional_weight", 0.5)


class TaskNode(BaseNode):
    """
    A task PAAW needs to do or track.
    
    Lifecycle:
    1. Created from conversation → status: pending
    2. PAAW works on it → status: in_progress  
    3. Done → status: completed, result stored
    4. Result becomes a Memory (linked via TRIGGERS)
    """
    type: NodeType = NodeType.TASK
    
    @property
    def status(self) -> str:
        return self.attributes.get("status", "pending")
    
    @property
    def priority(self) -> str:
        return self.attributes.get("priority", "medium")
    
    @property
    def due_date(self) -> str | None:
        return self.attributes.get("due_date")
    
    @property
    def result(self) -> str | None:
        return self.attributes.get("result")
    
    @property
    def tool_to_use(self) -> str | None:
        return self.attributes.get("tool_to_use")


class EventNode(BaseNode):
    """A scheduled or past event."""
    type: NodeType = NodeType.EVENT
    
    @property
    def event_date(self) -> str | None:
        return self.attributes.get("event_date")
    
    @property
    def recurring(self) -> bool:
        return self.attributes.get("recurring", False)
    
    @property
    def recurrence_pattern(self) -> str | None:
        return self.attributes.get("recurrence_pattern")


# =============================================================================
# EDGE MODEL
# =============================================================================

class Edge(BaseModel):
    """An edge connecting two nodes."""
    from_id: str
    to_id: str
    edge_type: EdgeType
    context: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_node(node_type: NodeType, **kwargs) -> BaseNode:
    """Factory to create the appropriate node type."""
    type_map = {
        NodeType.USER: UserNode,
        NodeType.DOMAIN: DomainNode,
        NodeType.PERSON: PersonNode,
        NodeType.PROJECT: ProjectNode,
        NodeType.GOAL: GoalNode,
        NodeType.MEMORY: MemoryNode,
        NodeType.TASK: TaskNode,
        NodeType.EVENT: EventNode,
    }
    cls = type_map.get(node_type, BaseNode)
    return cls(type=node_type, **kwargs)
