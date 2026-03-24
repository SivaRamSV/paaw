"""
Alert Notifier - Web fallback only.

DESIGN PRINCIPLE:
The LLM sends notifications directly via MCP tools.
The job.md has a plain text instruction like:
  "Send me a Discord DM if you find something significant."

The LLM reads this, sees it has discord MCP tools, and uses them.

This module only handles:
- Web alerts (stored in graph for UI) - fallback when LLM doesn't notify

No hardcoded channels. No channel registry. Just let the LLM be smart.
"""

import json
from datetime import datetime
from pathlib import Path

import structlog

logger = structlog.get_logger()


class Notifier:
    """
    Minimal notifier - only stores web alerts as fallback.
    
    Real notifications are sent by the LLM via MCP tools.
    """
    
    def __init__(self, graph_db=None):
        self.db = graph_db
    
    async def store_web_alert(self, user_id: str, job_name: str, message: str) -> bool:
        """
        Store alert in graph for web UI to display.
        
        This is the fallback when LLM doesn't use an MCP to notify.
        """
        if not self.db:
            logger.warning("No DB connection, web alert will be lost")
            return False
        
        try:
            from paaw.mental_model.models import NodeType
            
            alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            await self.db.create_node(
                id=alert_id,
                node_type=NodeType.MEMORY,
                label=f"Alert: {job_name}",
                context=message,
                attributes={
                    "type": "alert",
                    "job_name": job_name,
                    "read": False,
                    "user_id": user_id,
                },
            )
            
            from paaw.mental_model.models import EdgeType
            await self.db.create_edge(user_id, alert_id, EdgeType.HAS_ALERT)
            logger.info(f"Stored web alert: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store web alert: {e}")
            return False
