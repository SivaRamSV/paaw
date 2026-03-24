"""
Fast keyword search for mental model nodes.

Strategy:
1. Extract keywords from user message (no LLM, fast)
2. Search nodes by label, context, key_facts
3. Return ranked results

This replaces LLM-based routing with fast local search.
"""

import re
import logging
from dataclasses import dataclass

from paaw.mental_model.graph import GraphDB
from paaw.mental_model.models import BaseNode

logger = logging.getLogger(__name__)

# Common words to ignore in search
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "also", "now",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
    "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
    "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
    "that", "these", "those", "am", "been", "being", "and", "but", "if",
    "or", "because", "as", "until", "while", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below",
    "up", "down", "out", "off", "over", "under", "again", "further",
    "hey", "hi", "hello", "yeah", "yes", "no", "ok", "okay", "thanks",
    "please", "sorry", "well", "like", "just", "really", "actually",
    "gonna", "wanna", "gotta", "kinda", "sorta", "maybe", "probably",
    "definitely", "basically", "literally", "seriously", "honestly",
    "anyway", "anyways", "btw", "lol", "haha", "hmm", "umm", "uh",
}


@dataclass
class SearchResult:
    """A search result with relevance score."""
    node: BaseNode
    score: float
    match_reasons: list[str]


class NodeSearch:
    """
    Fast keyword-based search for mental model nodes.
    
    No LLM calls - pure local text matching.
    """
    
    def __init__(self, graph_db: GraphDB):
        self.db = graph_db
    
    def extract_keywords(self, text: str) -> list[str]:
        """
        Extract meaningful keywords from text.
        
        Returns lowercase keywords, excluding stop words.
        """
        # Normalize text
        text = text.lower()
        
        # Extract words (alphanumeric + some special chars)
        words = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)
        
        # Filter stop words and short words
        keywords = [
            w for w in words 
            if w not in STOP_WORDS and len(w) > 1
        ]
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        
        return unique
    
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Search nodes by keywords extracted from query.
        
        Returns ranked results with match reasons.
        """
        keywords = self.extract_keywords(query)
        
        if not keywords:
            logger.debug(f"No keywords extracted from: {query}")
            return []
        
        logger.debug(f"Searching for keywords: {keywords}")
        
        # Use the graph's search function
        nodes = await self.db.search_nodes(keywords, limit=limit * 2)
        
        # Score and rank results
        results = []
        for node in nodes:
            score, reasons = self._score_node(node, keywords)
            if score > 0:
                results.append(SearchResult(
                    node=node,
                    score=score,
                    match_reasons=reasons,
                ))
        
        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:limit]
    
    def _score_node(
        self,
        node: BaseNode,
        keywords: list[str],
    ) -> tuple[float, list[str]]:
        """
        Score a node's relevance to keywords.
        
        Returns (score, list of match reasons).
        """
        score = 0.0
        reasons = []
        
        label_lower = node.label.lower()
        context_lower = node.context.lower()
        facts_lower = " ".join(node.key_facts).lower()
        
        for kw in keywords:
            # Exact label match (highest score)
            if kw == label_lower:
                score += 10.0
                reasons.append(f"exact label match: {kw}")
            # Partial label match
            elif kw in label_lower:
                score += 5.0
                reasons.append(f"label contains: {kw}")
            
            # Context match
            if kw in context_lower:
                # Count occurrences
                count = context_lower.count(kw)
                score += 2.0 * min(count, 3)  # Cap at 3
                reasons.append(f"context contains: {kw} (x{count})")
            
            # Key facts match
            if kw in facts_lower:
                score += 1.5
                reasons.append(f"key_facts contains: {kw}")
        
        # Boost by access frequency (frequently accessed = more relevant)
        if node.access_count > 0:
            score *= 1.0 + (0.1 * min(node.access_count, 10))
        
        return score, reasons
    
    async def find_by_name(self, name: str) -> BaseNode | None:
        """
        Find a node by exact or close name match.
        
        Useful for finding people, projects by name.
        """
        # Try exact match first
        results = await self.search(name, limit=5)
        
        for result in results:
            if result.node.label.lower() == name.lower():
                return result.node
        
        # Return best match if any
        return results[0].node if results else None
    
    async def find_by_type(
        self,
        node_type: str,
        keywords: list[str] | None = None,
        limit: int = 10,
    ) -> list[BaseNode]:
        """
        Find nodes of a specific type, optionally filtered by keywords.
        """
        # This would be more efficient with a direct Cypher query
        # For now, search and filter
        if keywords:
            query = " ".join(keywords)
            results = await self.search(query, limit=limit * 2)
            return [
                r.node for r in results
                if r.node.type.value.lower() == node_type.lower()
            ][:limit]
        else:
            # Get all nodes of type - needs direct query
            # TODO: Add type-filtered query to GraphDB
            return []


def extract_keywords(text: str) -> list[str]:
    """Convenience function to extract keywords without NodeSearch instance."""
    # Normalize text
    text = text.lower()
    
    # Extract words
    words = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)
    
    # Filter stop words and short words
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    
    return unique
