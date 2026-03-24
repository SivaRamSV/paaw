"""
Onboarding Extractor - Extract structured data from freeform introduction.

Uses LLM to parse user's self-introduction into structured data
that can be stored in the mental model graph.
"""

import json
import logging
from dataclasses import dataclass, field

from litellm import acompletion

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    """Extracted user information."""
    name: str
    location: str | None = None
    timezone: str | None = None
    languages: list[str] | None = None
    response_style: str | None = None
    context: str | None = None
    key_facts: list[str] | None = None


@dataclass
class PersonInfo:
    """Extracted person information."""
    label: str  # Name
    relationship: str | None = None
    context: str | None = None
    key_facts: list[str] | None = None


@dataclass
class DomainInfo:
    """Extracted domain information."""
    label: str  # Domain name (Work, Health, etc.)
    context: str | None = None
    key_facts: list[str] | None = None


@dataclass
class ProjectInfo:
    """Extracted project information."""
    label: str
    status: str | None = None
    context: str | None = None
    key_facts: list[str] | None = None


@dataclass
class GoalInfo:
    """Extracted goal information."""
    label: str
    status: str | None = None
    target_date: str | None = None
    context: str | None = None
    key_facts: list[str] | None = None


@dataclass
class OnboardingData:
    """All data extracted from onboarding."""
    user: UserInfo
    people: list[PersonInfo] = field(default_factory=list)
    domains: list[DomainInfo] = field(default_factory=list)
    projects: list[ProjectInfo] = field(default_factory=list)
    goals: list[GoalInfo] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)


EXTRACTION_PROMPT = '''You are extracting structured information from a user's self-introduction.

The user said:
"""
{user_text}
"""

Extract all the information you can into this JSON structure. Be thorough - capture everything mentioned.
If something isn't mentioned, use null. Don't make things up.

Return ONLY valid JSON (no markdown, no explanation):

{{
  "user": {{
    "name": "Their name",
    "location": "City/Country if mentioned",
    "timezone": "Timezone if mentioned or can be inferred from location",
    "languages": ["Languages they speak"],
    "response_style": "Any communication preferences mentioned",
    "context": "1-2 sentence summary of who they are",
    "key_facts": ["Important facts about them"]
  }},
  "people": [
    {{
      "label": "Person's name",
      "relationship": "How they relate (wife, boss, friend, etc.)",
      "context": "What we learned about this person",
      "key_facts": ["Facts about them"]
    }}
  ],
  "domains": [
    {{
      "label": "Domain name (Work, Health, Family, Hobbies, Finance, etc.)",
      "context": "What's happening in this area of their life",
      "key_facts": ["Key facts about this domain"]
    }}
  ],
  "projects": [
    {{
      "label": "Project name",
      "status": "active/planned/paused/completed",
      "context": "What the project is about",
      "key_facts": ["Key facts"]
    }}
  ],
  "goals": [
    {{
      "label": "Goal description",
      "status": "active/achieved/abandoned",
      "target_date": "If mentioned",
      "context": "Details about the goal",
      "key_facts": ["Key facts"]
    }}
  ],
  "observations": [
    "Patterns or preferences you noticed (e.g., 'Seems to be a night owl', 'Values family time')"
  ]
}}

Remember:
- Extract EVERYTHING mentioned, even small details
- For people, capture their name and relationship
- Infer domains from context (if they mention work stress, create a Work domain)
- Be specific in context fields
- Observations are YOUR interpretations of their personality/patterns'''


class OnboardingExtractor:
    """
    Extracts structured data from user's self-introduction using LLM.
    """
    
    def __init__(self, model: str = "anthropic/claude-sonnet-4-20250514"):
        self.model = model
    
    async def extract(self, user_text: str) -> OnboardingData:
        """
        Extract structured onboarding data from user's introduction.
        
        Args:
            user_text: The user's freeform self-introduction
            
        Returns:
            OnboardingData with all extracted information
        """
        prompt = EXTRACTION_PROMPT.format(user_text=user_text)
        
        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for structured extraction
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            data = json.loads(content)
            
            return self._parse_response(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {content}")
            # Return minimal data with just the name extracted
            return self._fallback_extraction(user_text)
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return self._fallback_extraction(user_text)
    
    def _parse_response(self, data: dict) -> OnboardingData:
        """Parse the JSON response into OnboardingData."""
        # Parse user
        user_data = data.get("user", {})
        user = UserInfo(
            name=user_data.get("name", "User"),
            location=user_data.get("location"),
            timezone=user_data.get("timezone"),
            languages=user_data.get("languages"),
            response_style=user_data.get("response_style"),
            context=user_data.get("context"),
            key_facts=user_data.get("key_facts"),
        )
        
        # Parse people
        people = []
        for p in data.get("people", []):
            if p.get("label"):
                people.append(PersonInfo(
                    label=p["label"],
                    relationship=p.get("relationship"),
                    context=p.get("context"),
                    key_facts=p.get("key_facts"),
                ))
        
        # Parse domains
        domains = []
        for d in data.get("domains", []):
            if d.get("label"):
                domains.append(DomainInfo(
                    label=d["label"],
                    context=d.get("context"),
                    key_facts=d.get("key_facts"),
                ))
        
        # Parse projects
        projects = []
        for p in data.get("projects", []):
            if p.get("label"):
                projects.append(ProjectInfo(
                    label=p["label"],
                    status=p.get("status"),
                    context=p.get("context"),
                    key_facts=p.get("key_facts"),
                ))
        
        # Parse goals
        goals = []
        for g in data.get("goals", []):
            if g.get("label"):
                goals.append(GoalInfo(
                    label=g["label"],
                    status=g.get("status"),
                    target_date=g.get("target_date"),
                    context=g.get("context"),
                    key_facts=g.get("key_facts"),
                ))
        
        # Parse observations
        observations = data.get("observations", [])
        
        return OnboardingData(
            user=user,
            people=people,
            domains=domains,
            projects=projects,
            goals=goals,
            observations=observations,
        )
    
    def _fallback_extraction(self, user_text: str) -> OnboardingData:
        """Fallback extraction when LLM parsing fails."""
        # Try to extract at least a name
        import re
        
        name = "User"
        # Look for common patterns like "I'm X" or "My name is X"
        patterns = [
            r"(?:I'm|I am|my name is|call me)\s+([A-Z][a-z]+)",
            r"^([A-Z][a-z]+)\s+here",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_text, re.IGNORECASE)
            if match:
                name = match.group(1)
                break
        
        return OnboardingData(
            user=UserInfo(
                name=name,
                context=user_text[:200] if len(user_text) > 200 else user_text,
            ),
        )
