"""
Onboarding Flow - First-time user experience.

Philosophy: EMERGENT STRUCTURE
- Only thing we know for certain: we're talking to a human (User)
- Everything else (domains, people, goals) emerges from conversation
- No hardcoded categories - the LLM discovers structure organically

Flow:
1. Detect new user (no User node in graph)
2. Create minimal User node with just their name
3. Let natural conversation build the rest via <entity> and <memory> tags
"""

import logging
import re
from dataclasses import dataclass

from paaw.mental_model.graph import GraphDB
from paaw.mental_model.models import NodeType

logger = logging.getLogger(__name__)


@dataclass
class OnboardingResult:
    """Result of onboarding process."""
    user_id: str
    user_name: str
    summary: str


class OnboardingFlow:
    """
    Handles onboarding for new users.
    
    Philosophy:
    - Keep it minimal - just establish WHO we're talking to
    - Everything else emerges from natural conversation
    - The LLM uses <entity> tags to build structure organically
    """
    
    def __init__(self, graph_db: GraphDB, llm=None):
        self.db = graph_db
        self.llm = llm
    
    async def needs_onboarding(self, user_id: str = "user_default") -> bool:
        """Check if user needs onboarding (no User node exists)."""
        return not await self.db.user_exists(user_id)
    
    def get_greeting(self) -> str:
        """Get the onboarding greeting message."""
        return """Hey! 👋 I'm PAAW, your personal AI assistant.

Unlike other AIs that forget everything, I actually remember you. Every conversation helps me understand you better.

**What should I call you?** And tell me a bit about yourself - whatever's on your mind! 🐾"""
    
    async def process_introduction(
        self,
        user_response: str,
        user_id: str = "user_default",
    ) -> OnboardingResult:
        """
        Process the user's self-introduction.
        
        Only creates the User node. Everything else (domains, people, etc.)
        will be created organically via <entity> tags during normal conversation.
        
        Args:
            user_response: The user's response
            user_id: The user node ID to create
            
        Returns:
            OnboardingResult with minimal info
        """
        logger.info("Processing onboarding response...")
        
        # Extract just the name from the response
        name = self._extract_name(user_response)
        
        # Create minimal User node
        await self.db.create_node(
            id=user_id,
            node_type=NodeType.USER,
            label=name,
            context=f"User introduced themselves: {user_response[:200]}...",
            key_facts=[],
            attributes={},
        )
        
        logger.info(f"Created User node: {user_id} ({name})")
        
        summary = f"Nice to meet you, **{name}**! I'll learn more about you as we chat. 🐾"
        
        return OnboardingResult(
            user_id=user_id,
            user_name=name,
            summary=summary,
        )
    
    def _extract_name(self, text: str) -> str:
        """
        Extract the user's name from their introduction.
        
        Simple heuristics - looks for common patterns:
        - "I'm [Name]"
        - "My name is [Name]"
        - "I am [Name]"
        - "Call me [Name]"
        - "[Name] here"
        """
        text_lower = text.lower()
        
        patterns = [
            r"(?:i'm|i am|my name is|call me|i go by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"^([A-Z][a-z]+)(?:\s+here|\s*,)",
            r"(?:name(?:'s| is)?)\s+([A-Z][a-z]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Capitalize properly
                return name.title()
        
        # Fallback: look for any capitalized word at the start
        words = text.split()
        for word in words[:5]:  # Check first 5 words
            clean = re.sub(r'[^\w]', '', word)
            if clean and clean[0].isupper() and len(clean) > 1:
                return clean
        
        # Last resort
        return "Friend"
    
    def get_confirmation_prompt(self, result: OnboardingResult) -> str:
        """Get the confirmation message to show the user."""
        return f"""Great to meet you, {result.user_name}! 

I'll remember everything you share with me. What's on your mind today?"""
