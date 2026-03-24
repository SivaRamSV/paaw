"""
Mental Model Interface

Unified interface for all mental model operations.
This is the single entry point for reading/writing to the graph.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from paaw.mental_model.graph import GraphDB
from paaw.mental_model.models import BaseNode, NodeType, EdgeType
from paaw.mental_model.search import NodeSearch
from paaw.config import settings

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    """Context about the user for a conversation."""
    user_id: str
    user_node: BaseNode | None
    name: str
    location: str | None = None
    timezone: str | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    key_facts: list[str] = field(default_factory=list)
    context: str = ""


@dataclass
class JobInfo:
    """Information about a job from the mental model."""
    id: str
    name: str
    goal: str
    skill: str
    status: str
    schedule: dict[str, Any]
    serves: list[dict[str, str]] = field(default_factory=list)
    last_run: datetime | None = None
    next_run: datetime | None = None


class MentalModel:
    """
    Unified interface to the mental model graph.
    
    This class provides a clean API for all mental model operations,
    abstracting away the underlying graph database.
    
    Usage:
        model = await MentalModel.create()
        
        # Get user context
        user_ctx = await model.get_user_context("user_default")
        
        # Search for relevant nodes
        results = await model.search("birthday mom", limit=5)
        
        # Create a new job
        await model.create_job(
            id="job_xyz",
            name="Research Task",
            goal="...",
            skill="web_researcher"
        )
    """
    
    def __init__(self, db: GraphDB):
        self.db = db
        self.search = NodeSearch(db)
    
    @classmethod
    async def create(cls, database_url: str | None = None) -> "MentalModel":
        """Create a new MentalModel instance."""
        url = database_url or str(settings.database.url)
        db = await GraphDB.create(url)
        return cls(db)
    
    async def close(self):
        """Close the database connection."""
        await self.db.close()
    
    # =========================================================================
    # USER OPERATIONS
    # =========================================================================
    
    async def get_user_context(self, user_id: str = "user_default") -> UserContext:
        """Get the full user context for conversation."""
        user_node = await self.db.get_user_node(user_id)
        
        if not user_node:
            return UserContext(
                user_id=user_id,
                user_node=None,
                name="New User",
            )
        
        return UserContext(
            user_id=user_id,
            user_node=user_node,
            name=user_node.label,
            location=user_node.attributes.get("location"),
            timezone=user_node.attributes.get("timezone"),
            preferences={
                "response_style": user_node.attributes.get("response_style"),
                "languages": user_node.attributes.get("languages", []),
            },
            key_facts=user_node.key_facts,
            context=user_node.context,
        )
    
    async def user_exists(self, user_id: str = "user_default") -> bool:
        """Check if a user exists in the mental model."""
        return await self.db.user_exists(user_id)
    
    async def get_user_preferences(self, user_id: str = "user_default") -> dict[str, Any]:
        """Get user preferences from the mental model."""
        user_ctx = await self.get_user_context(user_id)
        return user_ctx.preferences
    
    async def create_user(
        self,
        user_id: str,
        name: str,
        context: str = "",
        **attributes
    ) -> str:
        """Create a new user node."""
        return await self.db.create_node(
            id=user_id,
            node_type=NodeType.USER,
            label=name,
            context=context,
            attributes=attributes,
        )
    
    # =========================================================================
    # SEARCH OPERATIONS
    # =========================================================================
    
    async def search_nodes(
        self,
        query: str,
        limit: int = 10
    ) -> list[BaseNode]:
        """Search for nodes matching a query."""
        results = await self.search.search(query, limit=limit)
        return [r.node for r in results]
    
    async def get_root_nodes(self, user_id: str = "user_default") -> list[BaseNode]:
        """Get all root-level nodes for a user."""
        return await self.db.get_root_nodes(user_id)
    
    async def get_node(self, node_id: str) -> BaseNode | None:
        """Get a specific node by ID."""
        return await self.db.get_node(node_id)
    
    async def get_recent_memories(
        self,
        node_id: str,
        limit: int = 5
    ) -> list[BaseNode]:
        """Get recent memories for a node."""
        return await self.db.get_recent_memories(node_id, limit=limit)
    
    # =========================================================================
    # ENTITY OPERATIONS
    # =========================================================================
    
    async def create_entity(
        self,
        entity_type: str,
        label: str,
        parent_id: str | None = None,
        context: str = "",
        key_facts: list[str] | None = None,
        **attributes
    ) -> str:
        """
        Create a new entity (Person, Domain, Project, Goal, etc.)
        
        Returns the created node ID.
        """
        # Map type string to NodeType
        try:
            node_type = NodeType(entity_type)
        except ValueError:
            node_type = NodeType.DOMAIN
        
        # Generate node ID
        clean_label = label.lower().replace(" ", "_")
        node_id = f"{entity_type.lower()}_{clean_label[:30]}"
        
        # Check if already exists
        if await self.db.node_exists(node_id):
            logger.info(f"Entity {node_id} already exists")
            return node_id
        
        # Create the node
        await self.db.create_node(
            id=node_id,
            node_type=node_type,
            label=label,
            context=context,
            key_facts=key_facts or [],
            attributes=attributes,
        )
        
        # Link to parent if provided
        if parent_id and await self.db.node_exists(parent_id):
            await self.db.create_edge(node_id, parent_id, EdgeType.CHILD_OF)
            await self.db.create_edge(parent_id, node_id, EdgeType.HAS_CHILD)
        
        logger.info(f"Created entity: {node_id}")
        return node_id
    
    async def update_entity(
        self,
        node_id: str,
        context: str | None = None,
        key_facts: list[str] | None = None,
        **attributes
    ) -> bool:
        """Update an existing entity."""
        return await self.db.update_node(
            node_id,
            context=context,
            key_facts=key_facts,
            attributes=attributes if attributes else None,
        )
    
    async def add_memory(
        self,
        content: str,
        memory_type: str = "fact",
        belongs_to: list[str] | None = None,
        user_id: str = "user_default"
    ) -> str:
        """Add a memory to the mental model."""
        return await self.db.add_memory(
            content=content,
            memory_type=memory_type,
            belongs_to=belongs_to or [],
            user_id=user_id,
        )
    
    # =========================================================================
    # JOB OPERATIONS
    # =========================================================================
    
    async def get_all_jobs(self) -> list[JobInfo]:
        """Get all jobs from the mental model."""
        query = "MATCH (j:Job) RETURN j"
        try:
            results = await self.db._cypher(query)
            jobs = []
            for r in results:
                props = r.get("properties", r)
                jobs.append(JobInfo(
                    id=props.get("id", ""),
                    name=props.get("label", ""),
                    goal=props.get("goal", props.get("context", "")),
                    skill=props.get("skill", ""),
                    status=props.get("status", "active"),
                    schedule=props.get("schedule", {}),
                ))
            return jobs
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    async def get_job(self, job_id: str) -> JobInfo | None:
        """Get a specific job by ID."""
        node = await self.db.get_node(job_id)
        if not node:
            return None
        
        return JobInfo(
            id=node.id,
            name=node.label,
            goal=node.context,
            skill=node.attributes.get("skill", ""),
            status=node.attributes.get("status", "active"),
            schedule=node.attributes.get("schedule", {}),
        )
    
    async def create_job(
        self,
        job_id: str,
        name: str,
        goal: str,
        skill: str,
        schedule: dict[str, Any] | None = None,
        context: str = "",
        serves: list[dict[str, str]] | None = None,
        created_by: str = "system"
    ) -> str:
        """
        Create a new job in the mental model.
        
        Also creates edges to:
        - PAAW (HAS_JOB)
        - Skill (USES_SKILL)
        - Goal/Person nodes (SERVES_GOAL, SERVES_PERSON)
        """
        # Create job node
        await self.db.create_node(
            id=job_id,
            node_type=NodeType.JOB,
            label=name,
            context=goal,
            key_facts=[f"Skill: {skill}", f"Created by: {created_by}"],
            attributes={
                "skill": skill,
                "schedule": schedule or {},
                "status": "active",
                "created_by": created_by,
                "additional_context": context,
            }
        )
        
        # Link to PAAW
        if await self.db.node_exists("assistant_paaw"):
            await self.db.create_edge(
                "assistant_paaw", job_id, EdgeType.HAS_JOB
            )
        
        # Link to skill
        skill_node_id = f"skill_{skill}"
        if await self.db.node_exists(skill_node_id):
            await self.db.create_edge(
                job_id, skill_node_id, EdgeType.USES_SKILL
            )
        
        # Link to serves targets
        if serves:
            for target in serves:
                target_id = target.get("node_id")
                target_type = target.get("type", "goal")
                if target_id and await self.db.node_exists(target_id):
                    edge_type = (
                        EdgeType.SERVES_GOAL if target_type == "goal"
                        else EdgeType.RELATES_TO
                    )
                    await self.db.create_edge(job_id, target_id, edge_type)
        
        logger.info(f"Created job: {job_id}")
        return job_id
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        last_run: datetime | None = None
    ) -> bool:
        """Update a job's status."""
        attrs = {"status": status}
        if last_run:
            attrs["last_run"] = last_run.isoformat()
        
        return await self.db.update_node(job_id, attributes=attrs)
    
    # =========================================================================
    # TRAIL OPERATIONS (Job Execution History)
    # =========================================================================
    
    async def create_trail(
        self,
        job_id: str,
        success: bool,
        output: str,
        started_at: datetime,
        finished_at: datetime,
        skill_id: str = "",
        error: str | None = None,
        scratchpad: list[dict] | None = None,
    ) -> str:
        """Create a trail (execution record) for a job."""
        trail_id = f"trail_{job_id}_{started_at.strftime('%Y%m%d_%H%M%S')}"
        
        await self.db.create_node(
            id=trail_id,
            node_type=NodeType.TRAIL,
            label=f"Trail: {job_id}",
            context=output,
            key_facts=[
                f"Status: {'SUCCESS' if success else 'FAILED'}",
                f"Duration: {(finished_at - started_at).total_seconds():.2f}s",
            ],
            attributes={
                "job_id": job_id,
                "skill_id": skill_id,
                "success": success,
                "error": error,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "scratchpad": scratchpad or [],
            }
        )
        
        # Link to job
        if await self.db.node_exists(job_id):
            await self.db.create_edge(job_id, trail_id, EdgeType.HAS_TRAIL)
        
        logger.info(f"Created trail: {trail_id}")
        return trail_id
    
    async def get_job_trails(
        self,
        job_id: str,
        limit: int = 10
    ) -> list[BaseNode]:
        """Get recent trails for a job."""
        query = f"""
            MATCH (j {{id: '{job_id}'}})-[:HAS_TRAIL]->(t:Trail)
            RETURN t
            ORDER BY t.started_at DESC
            LIMIT {limit}
        """
        try:
            results = await self.db._cypher(query)
            return [self.db._parse_node(r) for r in results]
        except Exception as e:
            logger.error(f"Failed to get trails: {e}")
            return []
    
    # =========================================================================
    # SKILL OPERATIONS
    # =========================================================================
    
    async def get_skill(self, skill_id: str) -> BaseNode | None:
        """Get a skill node."""
        node_id = f"skill_{skill_id}" if not skill_id.startswith("skill_") else skill_id
        return await self.db.get_node(node_id)
    
    async def get_all_skills(self) -> list[BaseNode]:
        """Get all skills."""
        query = "MATCH (s:Skill) RETURN s"
        try:
            results = await self.db._cypher(query)
            return [self.db._parse_node(r) for r in results]
        except Exception as e:
            logger.error(f"Failed to get skills: {e}")
            return []
    
    # =========================================================================
    # RELATIONSHIP OPERATIONS
    # =========================================================================
    
    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        context: str = ""
    ) -> bool:
        """Create a relationship between two nodes."""
        try:
            edge_type = EdgeType(relationship_type)
        except ValueError:
            edge_type = EdgeType.RELATES_TO
        
        return await self.db.create_edge(from_id, to_id, edge_type, context)
    
    async def get_related_nodes(
        self,
        node_id: str,
        relationship_type: str | None = None,
        direction: str = "outgoing"
    ) -> list[BaseNode]:
        """Get nodes related to a given node."""
        if relationship_type:
            if direction == "outgoing":
                query = f"""
                    MATCH (a {{id: '{node_id}'}})-[:{relationship_type}]->(b)
                    RETURN b
                """
            else:
                query = f"""
                    MATCH (a {{id: '{node_id}'}})<-[:{relationship_type}]-(b)
                    RETURN b
                """
        else:
            query = f"""
                MATCH (a {{id: '{node_id}'}})-[]-(b)
                RETURN DISTINCT b
            """
        
        try:
            results = await self.db._cypher(query)
            return [self.db._parse_node(r) for r in results]
        except Exception as e:
            logger.error(f"Failed to get related nodes: {e}")
            return []


# Global mental model instance
_mental_model: MentalModel | None = None


async def get_mental_model() -> MentalModel:
    """Get or create the global mental model instance."""
    global _mental_model
    if _mental_model is None:
        _mental_model = await MentalModel.create()
    return _mental_model


async def close_mental_model():
    """Close the global mental model instance."""
    global _mental_model
    if _mental_model:
        await _mental_model.close()
        _mental_model = None
