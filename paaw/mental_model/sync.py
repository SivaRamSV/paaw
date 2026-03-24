"""
Sync capabilities (Skills, Jobs, MCPs) from disk to the mental model graph.

This runs on startup and can be called to refresh capabilities.
In future, PAAW can also write to disk and call sync to update the graph.
"""

import json
import re
from pathlib import Path
from typing import Any

import structlog

from paaw.mental_model.models import NodeType, EdgeType

logger = structlog.get_logger()

# Project root (where skills/, jobs/, mcp/ directories are)
PROJECT_ROOT = Path(__file__).parent.parent.parent


def parse_skill_md(content: str, skill_name: str) -> dict[str, Any]:
    """Parse a skill.md file into node attributes."""
    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else skill_name
    
    # Extract persona section
    persona_match = re.search(r'##\s*Persona\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    persona = persona_match.group(1).strip() if persona_match else ""
    
    # Extract keywords
    keywords_match = re.search(r'##\s*Keywords\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    keywords = []
    if keywords_match:
        keywords = [k.strip() for k in keywords_match.group(1).strip().split(',')]
    
    # Extract tools
    tools_match = re.search(r'##\s*Tools You Use\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    tools = []
    if tools_match:
        tools = re.findall(r'-\s*(\w+)', tools_match.group(1))
    
    # Extract autonomy settings
    autonomy_match = re.search(r'##\s*Autonomy\s*\n```yaml\n(.*?)```', content, re.DOTALL)
    autonomy = {}
    if autonomy_match:
        for line in autonomy_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                value = value.strip()
                # Parse booleans and numbers
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                autonomy[key.strip()] = value
    
    return {
        "title": title,
        "persona": persona,
        "keywords": keywords,
        "tools": tools,
        "autonomy": autonomy,
        "raw_content": content,
    }


def parse_job_md(content: str, job_name: str) -> dict[str, Any]:
    """Parse a job.md file into node attributes."""
    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else job_name
    
    # Extract skill reference
    skill_match = re.search(r'##\s*Skill\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    skill = skill_match.group(1).strip() if skill_match else None
    
    # Extract goal
    goal_match = re.search(r'##\s*Goal\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    goal = goal_match.group(1).strip() if goal_match else ""
    
    # Extract description
    desc_match = re.search(r'##\s*Description\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    # Extract schedule
    schedule_match = re.search(r'##\s*Schedule\s*\n```yaml\n(.*?)```', content, re.DOTALL)
    schedule = {}
    if schedule_match:
        for line in schedule_match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                schedule[key.strip()] = value.strip().strip('"')
    
    # Extract tools allowed
    tools_match = re.search(r'##\s*Tools Allowed\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    tools = []
    if tools_match:
        tools = re.findall(r'-\s*(\w+)', tools_match.group(1))
    
    return {
        "title": title,
        "skill": skill,
        "goal": goal,
        "description": description,
        "schedule": schedule,
        "tools": tools,
        "raw_content": content,
    }


def load_skills() -> list[dict[str, Any]]:
    """Load all skills from skills/ directory."""
    skills_dir = PROJECT_ROOT / "skills"
    skills = []
    
    if not skills_dir.exists():
        logger.warning("Skills directory not found", path=str(skills_dir))
        return skills
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "skill.md"
            if skill_file.exists():
                content = skill_file.read_text()
                skill_data = parse_skill_md(content, skill_dir.name)
                skill_data["id"] = f"skill_{skill_dir.name}"
                skill_data["name"] = skill_dir.name
                skills.append(skill_data)
                logger.debug("Loaded skill", skill=skill_dir.name)
    
    return skills


def load_jobs() -> list[dict[str, Any]]:
    """Load all jobs from jobs/ directory."""
    jobs_dir = PROJECT_ROOT / "jobs"
    jobs = []
    
    if not jobs_dir.exists():
        logger.warning("Jobs directory not found", path=str(jobs_dir))
        return jobs
    
    for job_dir in jobs_dir.iterdir():
        if job_dir.is_dir():
            job_file = job_dir / "job.md"
            if job_file.exists():
                content = job_file.read_text()
                job_data = parse_job_md(content, job_dir.name)
                job_data["id"] = f"job_{job_dir.name}"
                job_data["name"] = job_dir.name
                jobs.append(job_data)
                logger.debug("Loaded job", job=job_dir.name)
    
    return jobs


def load_mcp_servers() -> list[dict[str, Any]]:
    """Load MCP server configurations."""
    mcp_file = PROJECT_ROOT / "mcp" / "servers.json"
    servers = []
    
    if not mcp_file.exists():
        logger.warning("MCP servers.json not found", path=str(mcp_file))
        return servers
    
    try:
        config = json.loads(mcp_file.read_text())
        for name, cfg in config.get("mcpServers", {}).items():
            servers.append({
                "id": f"mcp_{name}",
                "name": name,
                "description": cfg.get("description", ""),
                "command": cfg.get("command", ""),
                "args": cfg.get("args", []),
                "enabled": cfg.get("enabled", False),
                "tools": cfg.get("tools", []),
            })
            logger.debug("Loaded MCP server", server=name, enabled=cfg.get("enabled"))
    except Exception as e:
        logger.error("Failed to load MCP servers", error=str(e))
    
    return servers


async def sync_capabilities(graph_db) -> dict[str, int]:
    """
    Sync all capabilities from disk to the graph.
    
    Creates/updates nodes for:
    - Skills (from skills/*/skill.md)
    - Jobs (from jobs/*/job.md)
    - MCP servers (from mcp/servers.json)
    
    Links them to the PAAW assistant node.
    Also REMOVES nodes for jobs/skills that no longer exist on disk.
    
    Returns counts of synced items.
    """
    counts = {"skills": 0, "jobs": 0, "mcp_servers": 0, "deleted": 0}
    
    # Load from disk
    skills = load_skills()
    jobs = load_jobs()
    mcp_servers = load_mcp_servers()
    
    # Get current IDs from disk
    disk_job_ids = {job["id"] for job in jobs}
    disk_skill_ids = {skill["id"] for skill in skills}
    # Only keep enabled MCPs in the graph - disabled or deleted ones should be removed
    disk_mcp_ids_enabled = {mcp["id"] for mcp in mcp_servers if mcp.get("enabled", False)}
    # Track all MCPs that exist in config (for logging purposes)
    disk_mcp_ids_all = {mcp["id"] for mcp in mcp_servers}
    
    # Cleanup: Remove jobs that no longer exist on disk
    try:
        # Return full node to get the properties/id
        existing_jobs = await graph_db._cypher(
            "MATCH (j) WHERE j.id STARTS WITH 'job_' RETURN j"
        )
        for result in existing_jobs:
            # Get job_id from the node properties
            if isinstance(result, dict):
                props = result.get("properties", result)
                job_id = props.get("id", "")
            else:
                job_id = str(result).strip('"')
            
            if job_id and job_id not in disk_job_ids:
                await graph_db.delete_node(job_id)
                counts["deleted"] += 1
                logger.info(f"Deleted orphan job from graph: {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup orphan jobs: {e}")
    
    # Cleanup: Remove skills that no longer exist on disk
    try:
        existing_skills = await graph_db._cypher(
            "MATCH (s) WHERE s.id STARTS WITH 'skill_' AND NOT s.attributes.type = 'mcp_server' RETURN s"
        )
        for result in existing_skills:
            if isinstance(result, dict):
                props = result.get("properties", result)
                skill_id = props.get("id", "")
            else:
                skill_id = str(result).strip('"')
            
            if skill_id and skill_id not in disk_skill_ids:
                await graph_db.delete_node(skill_id)
                counts["deleted"] += 1
                logger.info(f"Deleted orphan skill from graph: {skill_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup orphan skills: {e}")
    
    # Cleanup: Remove MCPs that no longer exist or are disabled
    try:
        existing_mcps = await graph_db._cypher(
            "MATCH (m) WHERE m.id STARTS WITH 'mcp_' RETURN m"
        )
        for result in existing_mcps:
            if isinstance(result, dict):
                props = result.get("properties", result)
                mcp_id = props.get("id", "")
            else:
                mcp_id = str(result).strip('"')
            
            # Remove if MCP is deleted from config OR disabled
            if mcp_id and mcp_id not in disk_mcp_ids_enabled:
                await graph_db.delete_node(mcp_id)
                counts["deleted"] += 1
                if mcp_id in disk_mcp_ids_all:
                    logger.info(f"Deleted disabled MCP from graph: {mcp_id}")
                else:
                    logger.info(f"Deleted removed MCP from graph: {mcp_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup orphan MCPs: {e}")
    
    # Sync Skills
    for skill in skills:
        try:
            # Check if node exists
            existing = await graph_db.get_node(skill["id"])
            
            if existing:
                # Update existing node (update_node doesn't support label change)
                await graph_db.update_node(
                    skill["id"],
                    context=skill["persona"],
                    attributes={
                        "label": skill["title"],  # Store as attribute
                        "keywords": skill["keywords"],
                        "tools": skill["tools"],
                        "autonomy": skill["autonomy"],
                    }
                )
            else:
                # Create new node
                await graph_db.create_node(
                    id=skill["id"],
                    node_type=NodeType.SKILL,
                    label=skill["title"],
                    context=skill["persona"],
                    key_facts=skill["keywords"][:5] if skill["keywords"] else [],
                    attributes={
                        "keywords": skill["keywords"],
                        "tools": skill["tools"],
                        "autonomy": skill["autonomy"],
                    }
                )
                # Link to PAAW
                await graph_db.create_edge(
                    from_id="assistant_paaw",
                    to_id=skill["id"],
                    edge_type=EdgeType.HAS_SKILL,
                    context=f"PAAW has the {skill['title']} skill"
                )
            
            counts["skills"] += 1
            
        except Exception as e:
            logger.error("Failed to sync skill", skill=skill["id"], error=str(e))
    
    # Sync Jobs
    for job in jobs:
        try:
            existing = await graph_db.get_node(job["id"])
            
            if existing:
                # Update existing node
                await graph_db.update_node(
                    job["id"],
                    context=job["description"],
                    attributes={
                        "label": job["title"],
                        "goal": job["goal"],
                        "schedule": job["schedule"],
                        "tools": job["tools"],
                        "skill": job["skill"],
                    }
                )
            else:
                await graph_db.create_node(
                    id=job["id"],
                    node_type=NodeType.JOB,
                    label=job["title"],
                    context=job["description"],
                    key_facts=[job["goal"]] if job["goal"] else [],
                    attributes={
                        "goal": job["goal"],
                        "schedule": job["schedule"],
                        "tools": job["tools"],
                        "skill": job["skill"],
                    }
                )
                # Link to PAAW
                await graph_db.create_edge(
                    from_id="assistant_paaw",
                    to_id=job["id"],
                    edge_type=EdgeType.HAS_JOB,
                    context=f"PAAW manages the {job['title']} job"
                )
                
                # Link to skill if specified
                if job["skill"]:
                    skill_id = f"skill_{job['skill']}"
                    try:
                        await graph_db.create_edge(
                            from_id=job["id"],
                            to_id=skill_id,
                            edge_type=EdgeType.USES_SKILL,
                            context=f"Job uses {job['skill']} skill"
                        )
                    except Exception:
                        pass  # Skill may not exist yet
            
            counts["jobs"] += 1
            
        except Exception as e:
            logger.error("Failed to sync job", job=job["id"], error=str(e))
    
    # Sync MCP Servers (as Tool nodes - using SKILL type for now)
    for mcp in mcp_servers:
        if not mcp["enabled"]:
            continue  # Skip disabled servers
            
        try:
            existing = await graph_db.get_node(mcp["id"])
            
            if existing:
                # Update existing node
                await graph_db.update_node(
                    mcp["id"],
                    context=mcp["description"],
                    attributes={
                        "label": f"MCP: {mcp['name']}",
                        "type": "mcp_server",
                        "command": mcp["command"],
                        "tools": mcp["tools"],
                        "enabled": mcp["enabled"],
                    }
                )
            else:
                await graph_db.create_node(
                    id=mcp["id"],
                    node_type=NodeType.SKILL,  # Using SKILL type for MCP tools
                    label=f"MCP: {mcp['name']}",
                    context=mcp["description"],
                    key_facts=mcp["tools"],
                    attributes={
                        "type": "mcp_server",
                        "command": mcp["command"],
                        "tools": mcp["tools"],
                        "enabled": mcp["enabled"],
                    }
                )
                # Link to PAAW
                await graph_db.create_edge(
                    from_id="assistant_paaw",
                    to_id=mcp["id"],
                    edge_type=EdgeType.HAS_SKILL,
                    context=f"PAAW can use {mcp['name']} MCP server"
                )
            
            counts["mcp_servers"] += 1
            
        except Exception as e:
            logger.error("Failed to sync MCP server", mcp=mcp["id"], error=str(e))
    
    logger.info(
        "Capabilities synced",
        skills=counts["skills"],
        jobs=counts["jobs"],
        mcp_servers=counts["mcp_servers"],
        deleted=counts["deleted"],
    )
    
    return counts
