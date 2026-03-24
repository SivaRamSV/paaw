"""
Skill Loader - Parse skill.md files into SkillDefinition.

Skills define HOW to accomplish work:
- Persona: Who you are when executing
- How You Work: Approach and methodology
- Tools You Use: What tools are relevant
- Output Format: How to structure results
- Autonomy: What the skill can do independently

Jobs reference skills to define HOW work gets done.
Job = WHAT + WHEN + WHERE
Skill = HOW
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class SkillDefinition:
    """Parsed skill definition from skill.md."""
    
    # Identity
    id: str                          # Directory name (e.g., "web_researcher")
    name: str                        # From # heading
    path: Path                       # Full path to skill.md
    
    # How to behave
    persona: str = ""                # Who you are
    how_you_work: str = ""           # Methodology/approach
    tools_you_use: list[str] = field(default_factory=list)
    output_format: str = ""          # How to structure results
    keywords: list[str] = field(default_factory=list)
    
    # Autonomy settings
    autonomy: dict[str, Any] = field(default_factory=dict)
    needs_approval_for: list[str] = field(default_factory=list)
    
    def to_system_prompt(self) -> str:
        """Convert skill into a system prompt for LLM."""
        tools_list = "\n".join(f"- {tool}" for tool in self.tools_you_use) if self.tools_you_use else "Use available tools as needed."
        
        prompt = f"""## Your Role
{self.persona}

## How You Work
{self.how_you_work}

## Tools Available
{tools_list}

## Output Format
{self.output_format}
"""
        return prompt.strip()


def parse_skill_md(skill_path: Path) -> SkillDefinition | None:
    """
    Parse a skill.md file into a SkillDefinition.
    
    Args:
        skill_path: Path to skill.md file
        
    Returns:
        SkillDefinition or None if parsing fails
    """
    if not skill_path.exists():
        logger.warning(f"Skill file not found: {skill_path}")
        return None
    
    try:
        content = skill_path.read_text()
    except Exception as e:
        logger.error(f"Failed to read skill file: {e}")
        return None
    
    # Extract skill ID from directory name
    skill_id = skill_path.parent.name
    
    # Extract name from # heading
    name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else skill_id.replace("_", " ").title()
    
    skill = SkillDefinition(
        id=skill_id,
        name=name,
        path=skill_path,
    )
    
    # Parse sections
    sections = _extract_sections(content)
    
    # Persona
    if "Persona" in sections:
        skill.persona = sections["Persona"].strip()
    
    # How You Work
    if "How You Work" in sections:
        skill.how_you_work = sections["How You Work"].strip()
    
    # Tools You Use
    if "Tools You Use" in sections:
        skill.tools_you_use = _extract_list_items(sections["Tools You Use"])
    
    # Output Format
    if "Output Format" in sections:
        skill.output_format = sections["Output Format"].strip()
    
    # Keywords
    if "Keywords" in sections:
        keywords_text = sections["Keywords"].strip()
        skill.keywords = [k.strip() for k in keywords_text.split(",")]
    
    # Autonomy (YAML block)
    if "Autonomy" in sections:
        skill.autonomy = _parse_yaml_block(sections["Autonomy"])
    
    # Needs Approval For
    if "Needs Approval For" in sections:
        skill.needs_approval_for = _extract_list_items(sections["Needs Approval For"])
    
    logger.info(f"Parsed skill: {skill.id}", name=skill.name)
    return skill


def _extract_sections(content: str) -> dict[str, str]:
    """Extract ## sections from markdown."""
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content)
            # Start new section
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_content)
    
    return sections


def _extract_list_items(text: str) -> list[str]:
    """Extract - items from text, or lines with content."""
    items = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif line and not line.startswith("#") and not line.startswith("```"):
            # Also capture non-list items if they're meaningful
            pass
    return items


def _parse_yaml_block(text: str) -> dict[str, Any]:
    """Parse simple YAML-like key: value from text."""
    result = {}
    in_code_block = False
    
    for line in text.split("\n"):
        line_stripped = line.strip()
        
        # Track code blocks
        if line_stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        
        if in_code_block and ":" in line_stripped:
            key, value = line_stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Parse boolean/int values
            if value.lower() == "true":
                result[key] = True
            elif value.lower() == "false":
                result[key] = False
            elif value.isdigit():
                result[key] = int(value)
            else:
                result[key] = value
    
    return result


def load_skill(skill_id: str, skills_dir: Path | None = None) -> SkillDefinition | None:
    """
    Load a specific skill by ID.
    
    Args:
        skill_id: The skill directory name (e.g., "web_researcher")
        skills_dir: Path to skills directory (defaults to project root/skills)
        
    Returns:
        SkillDefinition or None if not found
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent.parent.parent / "skills"
    
    skill_path = skills_dir / skill_id / "skill.md"
    return parse_skill_md(skill_path)


def load_all_skills(skills_dir: Path | None = None) -> dict[str, SkillDefinition]:
    """
    Load all skills from the skills directory.
    
    Returns:
        Dict mapping skill_id to SkillDefinition
    """
    if skills_dir is None:
        skills_dir = Path(__file__).parent.parent.parent / "skills"
    
    skills = {}
    
    if not skills_dir.exists():
        logger.warning(f"Skills directory not found: {skills_dir}")
        return skills
    
    for skill_folder in skills_dir.iterdir():
        if not skill_folder.is_dir():
            continue
        
        skill_md = skill_folder / "skill.md"
        if not skill_md.exists():
            continue
        
        skill = parse_skill_md(skill_md)
        if skill:
            skills[skill.id] = skill
    
    logger.info(f"Loaded {len(skills)} skills")
    return skills
