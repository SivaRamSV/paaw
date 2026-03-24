"""
Graph Database Operations for Mental Model.

Uses Apache AGE (PostgreSQL graph extension) for Cypher queries.
Provides async interface for all graph operations.
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import asyncpg

from paaw.mental_model.models import (
    BaseNode,
    EdgeType,
    NodeType,
)

logger = logging.getLogger(__name__)


class GraphDB:
    """
    Async interface to Apache AGE graph database.
    
    All mental model data is stored in a graph called 'mental_model'.
    """
    
    GRAPH_NAME = "mental_model"
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self._initialized = False
    
    @classmethod
    async def create(cls, database_url: str) -> "GraphDB":
        """Create GraphDB with connection pool."""
        pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
        )
        db = cls(pool)
        await db._init_session()
        return db
    
    async def _init_session(self):
        """Initialize AGE extension for the session."""
        if self._initialized:
            return
        
        async with self.pool.acquire() as conn:
            await conn.execute("LOAD 'age'")
            await conn.execute('SET search_path = ag_catalog, "$user", public')
        
        self._initialized = True
    
    @asynccontextmanager
    async def connection(self):
        """Get a connection with AGE initialized."""
        async with self.pool.acquire() as conn:
            await conn.execute("LOAD 'age'")
            await conn.execute('SET search_path = ag_catalog, "$user", public')
            yield conn
    
    async def close(self):
        """Close the connection pool."""
        await self.pool.close()
    
    def _escape(self, s: str) -> str:
        """Escape string for Cypher."""
        if s is None:
            return ""
        return str(s).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    
    def _format_key_facts(self, facts: list[str]) -> str:
        """Format key_facts list for Cypher."""
        if not facts:
            return "[]"
        escaped = [f"'{self._escape(f)}'" for f in facts]
        return "[" + ", ".join(escaped) + "]"
    
    async def _cypher(self, query: str) -> list[dict]:
        """Execute a Cypher query and return results."""
        async with self.connection() as conn:
            sql = f"SELECT * FROM cypher('{self.GRAPH_NAME}', $$ {query} $$) AS (result agtype)"
            rows = await conn.fetch(sql)
            results = []
            for row in rows:
                val = row['result']
                if val is not None:
                    # Parse agtype to dict
                    try:
                        val_str = str(val)
                        # Remove ::vertex or ::edge suffix
                        if '::vertex' in val_str:
                            val_str = val_str.rsplit('::vertex', 1)[0]
                        if '::edge' in val_str:
                            val_str = val_str.rsplit('::edge', 1)[0]
                        parsed = json.loads(val_str)
                        results.append(parsed)
                    except json.JSONDecodeError:
                        results.append({"value": str(val)})
            return results
    
    # =========================================================================
    # NODE OPERATIONS
    # =========================================================================
    
    async def create_node(
        self,
        id: str,
        node_type: NodeType,
        label: str,
        context: str = "",
        key_facts: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> str:
        """Create a new node in the graph."""
        key_facts = key_facts or []
        attributes = attributes or {}
        now = datetime.utcnow().isoformat()
        
        # Build properties
        props = [
            f"id: '{self._escape(id)}'",
            f"type: '{node_type.value}'",
            f"label: '{self._escape(label)}'",
            f"context: '{self._escape(context)}'",
            f"key_facts: {self._format_key_facts(key_facts)}",
            f"created_at: '{now}'",
            f"updated_at: '{now}'",
            f"last_accessed: '{now}'",
            f"access_count: 0",
        ]
        
        # Add custom attributes
        for k, v in attributes.items():
            if v is not None:
                if isinstance(v, (list, dict)):
                    props.append(f"{k}: '{self._escape(json.dumps(v))}'")
                elif isinstance(v, bool):
                    props.append(f"{k}: {str(v).lower()}")
                elif isinstance(v, (int, float)):
                    props.append(f"{k}: {v}")
                else:
                    props.append(f"{k}: '{self._escape(str(v))}'")
        
        props_str = ", ".join(props)
        query = f"CREATE (n:{node_type.value} {{{props_str}}}) RETURN n.id"
        
        await self._cypher(query)
        logger.info(f"Created node: {id} ({node_type.value})")
        return id
    
    async def get_node(self, node_id: str) -> BaseNode | None:
        """Get a node by ID."""
        query = f"MATCH (n) WHERE n.id = '{self._escape(node_id)}' RETURN n"
        results = await self._cypher(query)
        
        if not results:
            return None
        
        return self._parse_node(results[0])
    
    def _parse_node(self, data: dict) -> BaseNode:
        """Parse a graph result into a BaseNode."""
        # Handle nested properties from AGE
        props = data.get('properties', data)
        
        # Parse timestamps
        for ts_field in ["created_at", "updated_at", "last_accessed"]:
            if ts_field in props and isinstance(props[ts_field], str):
                try:
                    props[ts_field] = datetime.fromisoformat(props[ts_field].replace("Z", "+00:00"))
                except ValueError:
                    props[ts_field] = datetime.utcnow()
        
        # Parse type
        node_type = props.get("type", "Memory")
        if isinstance(node_type, str):
            try:
                node_type = NodeType(node_type)
            except ValueError:
                node_type = NodeType.MEMORY
        
        # Extract known fields
        known_fields = {
            "id", "type", "label", "context", "key_facts",
            "created_at", "updated_at", "last_accessed", "access_count"
        }
        attributes = {k: v for k, v in props.items() if k not in known_fields}
        
        return BaseNode(
            id=props.get("id", ""),
            type=node_type,
            label=props.get("label", ""),
            context=props.get("context", ""),
            key_facts=props.get("key_facts", []),
            attributes=attributes,
            created_at=props.get("created_at", datetime.utcnow()),
            updated_at=props.get("updated_at", datetime.utcnow()),
            last_accessed=props.get("last_accessed", datetime.utcnow()),
            access_count=props.get("access_count", 0),
        )
    
    async def update_node(
        self,
        node_id: str,
        context: str | None = None,
        key_facts: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> bool:
        """Update a node's properties."""
        sets = [f"n.updated_at = '{datetime.utcnow().isoformat()}'"]
        
        if context is not None:
            sets.append(f"n.context = '{self._escape(context)}'")
        
        if key_facts is not None:
            sets.append(f"n.key_facts = {self._format_key_facts(key_facts)}")
        
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    if isinstance(v, (list, dict)):
                        sets.append(f"n.{k} = '{self._escape(json.dumps(v))}'")
                    elif isinstance(v, bool):
                        sets.append(f"n.{k} = {str(v).lower()}")
                    elif isinstance(v, (int, float)):
                        sets.append(f"n.{k} = {v}")
                    else:
                        sets.append(f"n.{k} = '{self._escape(str(v))}'")
        
        set_str = ", ".join(sets)
        query = f"MATCH (n) WHERE n.id = '{self._escape(node_id)}' SET {set_str} RETURN n.id"
        
        try:
            await self._cypher(query)
            logger.info(f"Updated node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {e}")
            return False
    
    async def delete_node(self, node_id: str) -> bool:
        """Delete a node and its edges."""
        query = f"MATCH (n) WHERE n.id = '{self._escape(node_id)}' DETACH DELETE n"
        try:
            await self._cypher(query)
            logger.info(f"Deleted node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete node {node_id}: {e}")
            return False
    
    async def node_exists(self, node_id: str) -> bool:
        """Check if a node exists."""
        node = await self.get_node(node_id)
        return node is not None
    
    # =========================================================================
    # EDGE OPERATIONS
    # =========================================================================
    
    async def create_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: EdgeType,
        context: str = "",
    ) -> bool:
        """Create an edge between two nodes."""
        now = datetime.utcnow().isoformat()
        query = f"""
            MATCH (a), (b) 
            WHERE a.id = '{self._escape(from_id)}' AND b.id = '{self._escape(to_id)}' 
            CREATE (a)-[r:{edge_type.value} {{context: '{self._escape(context)}', created_at: '{now}'}}]->(b)
            RETURN type(r)
        """
        try:
            await self._cypher(query)
            logger.info(f"Created edge: {from_id} -[{edge_type.value}]-> {to_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create edge: {e}")
            return False
    
    async def get_children(
        self,
        node_id: str,
        edge_type: EdgeType = EdgeType.CHILD_OF,
    ) -> list[BaseNode]:
        """Get all child nodes of a parent."""
        query = f"""
            MATCH (child)-[:{edge_type.value}]->(parent) 
            WHERE parent.id = '{self._escape(node_id)}' 
            RETURN child
        """
        results = await self._cypher(query)
        return [self._parse_node(r) for r in results]
    
    # =========================================================================
    # USER-SPECIFIC OPERATIONS
    # =========================================================================
    
    async def get_user_node(self, user_id: str) -> BaseNode | None:
        """Get the User node."""
        query = f"MATCH (n:User) WHERE n.id = '{self._escape(user_id)}' RETURN n"
        results = await self._cypher(query)
        
        if not results:
            return None
        
        return self._parse_node(results[0])
    
    async def get_root_nodes(self, user_id: str) -> list[BaseNode]:
        """Get all root-level nodes for system prompt."""
        query = f"""
            MATCH (user:User {{id: '{self._escape(user_id)}'}})-[:HAS_CHILD]->(child)
            RETURN child
            ORDER BY child.type, child.label
        """
        results = await self._cypher(query)
        return [self._parse_node(r) for r in results]
    
    async def user_exists(self, user_id: str = "user_default") -> bool:
        """Check if a user node exists."""
        user = await self.get_user_node(user_id)
        return user is not None
    
    # =========================================================================
    # MEMORY OPERATIONS
    # =========================================================================
    
    async def add_memory(
        self,
        content: str,
        memory_type: str = "fact",
        belongs_to: list[str] | None = None,
        source_channel: str = "cli",
        emotional_weight: float = 0.5,
        user_id: str = "user_default",
    ) -> str:
        """Add a new memory node and link it to relevant nodes.
        
        If none of the belongs_to nodes exist, falls back to linking to the user node.
        """
        belongs_to = belongs_to or []
        
        memory_id = f"memory_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        await self.create_node(
            id=memory_id,
            node_type=NodeType.MEMORY,
            label=content[:50] + "..." if len(content) > 50 else content,
            context=content,
            attributes={
                "memory_type": memory_type,
                "source_channel": source_channel,
                "emotional_weight": emotional_weight,
            },
        )
        
        # Try to link to each target node, track if any succeeded
        linked_to_any = False
        for node_id in belongs_to:
            # Check if target node exists before creating edge
            if await self.node_exists(node_id):
                await self.create_edge(memory_id, node_id, EdgeType.BELONGS_TO)
                linked_to_any = True
            else:
                logger.warning(f"Cannot link memory to non-existent node: {node_id}")
        
        # Fallback: if no links succeeded, link to user node
        if not linked_to_any:
            await self.create_edge(memory_id, user_id, EdgeType.BELONGS_TO)
            logger.info(f"Memory {memory_id} fell back to linking to {user_id}")
        
        logger.info(f"Added memory: {memory_id} -> {belongs_to if linked_to_any else [user_id]}")
        return memory_id
    
    async def get_recent_memories(
        self,
        node_id: str,
        limit: int = 10,
    ) -> list[BaseNode]:
        """Get recent memories belonging to a node."""
        query = f"""
            MATCH (m:Memory)-[:BELONGS_TO]->(n)
            WHERE n.id = '{self._escape(node_id)}'
            RETURN m
            ORDER BY m.created_at DESC
            LIMIT {limit}
        """
        results = await self._cypher(query)
        return [self._parse_node(r) for r in results]
    
    # =========================================================================
    # TASK OPERATIONS
    # =========================================================================
    
    async def create_task(
        self,
        label: str,
        belongs_to: list[str] | None = None,
        due_date: str | None = None,
        priority: str = "medium",
        tool_to_use: str | None = None,
    ) -> str:
        """Create a new task node."""
        belongs_to = belongs_to or []
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        await self.create_node(
            id=task_id,
            node_type=NodeType.TASK,
            label=label,
            context=label,
            attributes={
                "status": "pending",
                "priority": priority,
                "due_date": due_date,
                "tool_to_use": tool_to_use,
            },
        )
        
        for node_id in belongs_to:
            await self.create_edge(task_id, node_id, EdgeType.BELONGS_TO)
        
        logger.info(f"Created task: {task_id}")
        return task_id
    
    async def complete_task(self, task_id: str, result: str) -> str | None:
        """Mark a task as completed and create a memory from the result."""
        task = await self.get_node(task_id)
        if task is None:
            return None
        
        await self.update_node(
            task_id,
            attributes={"status": "completed", "result": result},
        )
        
        # Get nodes this task belongs to
        query = f"""
            MATCH (t)-[:BELONGS_TO]->(n)
            WHERE t.id = '{self._escape(task_id)}'
            RETURN n.id
        """
        results = await self._cypher(query)
        belongs_to = [r.get('value', r) if isinstance(r, dict) else str(r) for r in results]
        
        # Create memory from result
        memory_id = await self.add_memory(
            content=f"Task completed: {task.label}. Result: {result}",
            memory_type="episode",
            belongs_to=belongs_to,
        )
        
        await self.create_edge(task_id, memory_id, EdgeType.TRIGGERS)
        
        logger.info(f"Completed task: {task_id} -> memory: {memory_id}")
        return memory_id
    
    async def get_pending_tasks(self, user_id: str) -> list[BaseNode]:
        """Get all pending tasks."""
        query = """
            MATCH (t:Task)
            WHERE t.status = 'pending'
            RETURN t
            ORDER BY t.priority, t.due_date
        """
        results = await self._cypher(query)
        return [self._parse_node(r) for r in results]
    
    # =========================================================================
    # ACCESS TRACKING
    # =========================================================================
    
    async def record_access(self, node_ids: list[str]) -> None:
        """Record that nodes were accessed."""
        now = datetime.utcnow().isoformat()
        for node_id in node_ids:
            query = f"""
                MATCH (n) 
                WHERE n.id = '{self._escape(node_id)}' 
                SET n.last_accessed = '{now}', 
                    n.access_count = COALESCE(n.access_count, 0) + 1
                RETURN n.id
            """
            try:
                await self._cypher(query)
            except Exception as e:
                logger.debug(f"Failed to record access for {node_id}: {e}")
    
    # =========================================================================
    # SEARCH
    # =========================================================================
    
    async def search_nodes(
        self,
        keywords: list[str],
        limit: int = 10,
    ) -> list[BaseNode]:
        """Search nodes by keywords in label and context."""
        if not keywords:
            return []
        
        # Build regex pattern
        pattern = "(?i)(" + "|".join(self._escape(kw) for kw in keywords) + ")"
        
        query = f"""
            MATCH (n)
            WHERE n.label =~ '{pattern}' OR n.context =~ '{pattern}'
            RETURN n
            LIMIT {limit}
        """
        results = await self._cypher(query)
        return [self._parse_node(r) for r in results]
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    async def get_stats(self) -> dict[str, int]:
        """Get graph statistics."""
        stats = {}
        
        for node_type in NodeType:
            query = f"MATCH (n:{node_type.value}) RETURN count(n)"
            results = await self._cypher(query)
            count = results[0] if results else 0
            if isinstance(count, dict):
                count = count.get('value', count.get('count', 0))
            stats[f"nodes_{node_type.value.lower()}"] = int(count) if count else 0
        
        # Total edges
        query = "MATCH ()-[r]->() RETURN count(r)"
        results = await self._cypher(query)
        count = results[0] if results else 0
        if isinstance(count, dict):
            count = count.get('value', count.get('count', 0))
        stats["edges_total"] = int(count) if count else 0
        
        return stats
