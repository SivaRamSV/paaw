"""
Job Creator - Creates job.md files from chat requests.

When a user asks PAAW to do something recurring, this module:
1. Creates the job.md file in jobs/
2. Syncs the job to the graph
3. Optionally runs it immediately
"""

import re
from datetime import datetime
from pathlib import Path

import structlog

from paaw.models import JobRequest

logger = structlog.get_logger()

# Common schedule patterns to cron
SCHEDULE_TO_CRON = {
    # Daily patterns
    "every day at 8am": "0 8 * * *",
    "every day at 9am": "0 9 * * *",
    "every morning": "0 8 * * *",
    "every morning at 8": "0 8 * * *",
    "every morning at 9": "0 9 * * *",
    "daily": "0 9 * * *",
    "daily at 8am": "0 8 * * *",
    "daily at 9am": "0 9 * * *",
    
    # Hourly patterns
    "every hour": "0 * * * *",
    "hourly": "0 * * * *",
    "every 2 hours": "0 */2 * * *",
    "every 4 hours": "0 */4 * * *",
    "every 6 hours": "0 */6 * * *",
    
    # Weekly patterns
    "every monday": "0 9 * * 1",
    "every monday at 9am": "0 9 * * 1",
    "every friday": "0 9 * * 5",
    "weekly": "0 9 * * 1",
    
    # Other
    "every minute": "* * * * *",  # For testing
}


def parse_schedule_to_cron(schedule: str) -> str:
    """Convert natural language schedule to cron expression."""
    if not schedule:
        return "0 9 * * *"  # Default: daily at 9am
    
    schedule_lower = schedule.lower().strip()
    
    # Check exact matches first
    if schedule_lower in SCHEDULE_TO_CRON:
        return SCHEDULE_TO_CRON[schedule_lower]
    
    # Try partial matches
    for pattern, cron in SCHEDULE_TO_CRON.items():
        if pattern in schedule_lower:
            return cron
    
    # Try to parse "at Xam/pm" pattern
    time_match = re.search(r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?', schedule_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        period = time_match.group(3)
        
        if period == 'pm' and hour < 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        # Determine frequency
        if 'every day' in schedule_lower or 'daily' in schedule_lower:
            return f"{minute} {hour} * * *"
        elif 'monday' in schedule_lower:
            return f"{minute} {hour} * * 1"
        elif 'friday' in schedule_lower:
            return f"{minute} {hour} * * 5"
        else:
            return f"{minute} {hour} * * *"  # Default to daily
    
    # If it looks like a cron expression already, use it
    if re.match(r'^[\d\*\/\-\,]+\s+[\d\*\/\-\,]+\s+[\d\*\/\-\,]+\s+[\d\*\/\-\,]+\s+[\d\*\/\-\,]+$', schedule):
        return schedule
    
    logger.warning(f"Could not parse schedule '{schedule}', using default")
    return "0 9 * * *"


def slugify(text: str) -> str:
    """Convert text to a valid job ID/folder name."""
    # Lowercase and replace spaces/special chars with underscores
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug[:50]  # Limit length


def generate_job_md(
    job_id: str,
    name: str,
    goal: str,
    skill: str,
    schedule: str,
    cron: str,
    notify_channel: str = "",
    context: str = "",
) -> str:
    """Generate the content of a job.md file."""
    
    # Build the notification section
    notify_section = ""
    if notify_channel:
        if notify_channel.isdigit():
            notify_section = f"Post results to Discord channel ID: {notify_channel}"
        elif notify_channel.startswith("#"):
            notify_section = f"Post results to Discord channel: {notify_channel}"
        else:
            notify_section = notify_channel
    else:
        notify_section = "Respond in the chat interface"
    
    return f"""# {name}

## Meta
created: {datetime.utcnow().strftime('%Y-%m-%d')}
created_by: chat
status: active

## Uses Skill
{skill}

## Goal
{goal}

## What To Find
Based on the goal, find relevant and timely information.

## Delivery
- Format: Clear, concise summary with key points
- Length: Under 2000 characters
- Only alert on: Significant findings related to the goal

## Schedule
cron: {cron}
timezone: Asia/Kolkata

## How To Notify
{notify_section}

## Context
{context or 'Created via chat request. ' + (f'Original schedule request: "{schedule}"' if schedule else '')}
"""


class JobCreator:
    """Creates jobs from chat requests."""
    
    def __init__(self, jobs_dir: Path | None = None):
        self.jobs_dir = jobs_dir or Path(__file__).parent.parent.parent / "jobs"
    
    async def create_job(
        self,
        request: JobRequest,
        notify_channel: str = "",
        user_context: str = "",
    ) -> dict:
        """
        Create a new job from a JobRequest.
        
        Returns dict with:
        - success: bool
        - job_id: str
        - job_path: str
        - cron: str
        - error: str (if failed)
        """
        try:
            # Generate job ID from description
            job_id = slugify(request.description or f"{request.skill}_job")
            
            # Ensure unique by adding timestamp if exists
            job_dir = self.jobs_dir / job_id
            if job_dir.exists():
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                job_id = f"{job_id}_{timestamp}"
                job_dir = self.jobs_dir / job_id
            
            # Parse schedule to cron
            cron = parse_schedule_to_cron(request.schedule or "")
            
            # Generate job name from description
            name = request.description or f"{request.skill.replace('_', ' ').title()} Job"
            if len(name) > 50:
                name = name[:47] + "..."
            
            # Generate job.md content
            content = generate_job_md(
                job_id=job_id,
                name=name,
                goal=request.description or f"Execute {request.skill} skill as scheduled",
                skill=request.skill,
                schedule=request.schedule or "",
                cron=cron,
                notify_channel=notify_channel,
                context=user_context,
            )
            
            # Create directory and write file
            job_dir.mkdir(parents=True, exist_ok=True)
            job_file = job_dir / "job.md"
            job_file.write_text(content)
            
            logger.info(
                "Created job from chat",
                job_id=job_id,
                skill=request.skill,
                cron=cron,
                path=str(job_file),
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "job_path": str(job_file),
                "cron": cron,
                "name": name,
            }
            
        except Exception as e:
            logger.error("Failed to create job", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
    
    async def sync_job_to_graph(self, job_id: str, db) -> bool:
        """Sync a newly created job to the graph."""
        try:
            from paaw.mental_model.sync import sync_capabilities
            counts = await sync_capabilities(db)
            logger.info("Synced new job to graph", job_id=job_id, **counts)
            return True
        except Exception as e:
            logger.error("Failed to sync job to graph", error=str(e))
            return False
