"""
PAAW Scheduler - Background job execution.

Jobs are defined in jobs/{name}/job.md files.
Scheduler runs them on their cron schedules.
Results stored as Trail nodes, findings as Memory nodes.
Alerts sent via configured channels (Discord, etc.)

Key principle: Jobs are NOT conversations.
They run in isolated contexts and notify users separately.
"""

from paaw.scheduler.runner import SchedulerRunner
from paaw.scheduler.executor import JobExecutor
from paaw.scheduler.parser import parse_job_md, JobDefinition

__all__ = [
    "SchedulerRunner",
    "JobExecutor",
    "parse_job_md",
    "JobDefinition",
]
