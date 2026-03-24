"""
Scheduler Runner - Main scheduler loop.

Runs as a background task, checking jobs every minute.
Executes jobs when their cron schedules match.

Usage:
    # Run standalone
    python -m paaw.scheduler.runner
    
    # Or start with main app
    await scheduler.start()
"""

import asyncio
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import structlog
from croniter import croniter

from paaw.scheduler.executor import JobExecutor
from paaw.scheduler.notifier import Notifier
from paaw.scheduler.parser import load_all_jobs, JobDefinition

logger = structlog.get_logger()


class SchedulerRunner:
    """
    Main scheduler that runs jobs on their cron schedules.
    
    - Checks every minute for due jobs
    - Executes jobs in isolated contexts
    - Sends alerts when significant findings
    - Per-job locking prevents duplicate runs
    """
    
    def __init__(self, jobs_dir: Path | None = None):
        self.jobs_dir = jobs_dir or Path(__file__).parent.parent.parent / "jobs"
        self.executor: JobExecutor | None = None
        self.notifier: Notifier | None = None
        self._running = False
        self._task: asyncio.Task | None = None
        
        # Track last run time per job to prevent duplicate runs
        self._last_run: dict[str, datetime] = {}
    
    async def initialize(self):
        """Initialize scheduler components."""
        self.executor = JobExecutor()
        await self.executor.initialize()
        
        self.notifier = Notifier(self.executor.db)
        
        logger.info("Scheduler initialized", jobs_dir=str(self.jobs_dir))
    
    async def start(self):
        """Start the scheduler loop."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        await self.initialize()
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler started")
    
    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self.executor:
            await self.executor.cleanup()
        
        logger.info("Scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop - runs every minute."""
        while self._running:
            try:
                await self._check_and_run_jobs()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            
            # Sleep until next minute
            await asyncio.sleep(60)
    
    async def _check_and_run_jobs(self):
        """Check all jobs and run any that are due."""
        now = datetime.now()
        jobs = load_all_jobs(self.jobs_dir)
        
        for job in jobs:
            if not job.is_active():
                continue
            
            if not job.cron:
                continue
            
            if self._is_due(job, now):
                # Run job in background (don't block other jobs)
                asyncio.create_task(self._run_job(job))
    
    def _is_due(self, job: JobDefinition, now: datetime) -> bool:
        """Check if a job is due to run."""
        if not job.cron:
            return False
        
        try:
            # Get job's timezone
            tz = ZoneInfo(job.timezone) if job.timezone else ZoneInfo("UTC")
            now_tz = now.astimezone(tz)
            
            # Check if we already ran this minute
            last_run = self._last_run.get(job.id)
            if last_run:
                # Same minute = already ran
                if last_run.strftime("%Y-%m-%d %H:%M") == now_tz.strftime("%Y-%m-%d %H:%M"):
                    return False
            
            # Check if cron matches current time
            from datetime import timedelta
            cron = croniter(job.cron, now_tz - timedelta(minutes=1))
            next_run = cron.get_next(datetime)
            
            # Due if next run is within this minute
            return next_run.strftime("%Y-%m-%d %H:%M") == now_tz.strftime("%Y-%m-%d %H:%M")
            
        except Exception as e:
            logger.error(f"Cron check failed for {job.id}: {e}")
            return False
    
    async def _run_job(self, job: JobDefinition):
        """Run a single job."""
        logger.info(f"Running job: {job.id}")
        
        # Mark as run for this minute
        self._last_run[job.id] = datetime.now()
        
        try:
            result = await self.executor.execute(job)
            
            # Send alert if needed (fallback - LLM should have already notified via MCP)
            if result.should_alert and self.notifier:
                await self.notifier.store_web_alert(
                    user_id="user_default",
                    job_name=job.name,
                    message=result.alert_message,
                )
            
            logger.info(
                f"Job completed: {job.id}",
                status=result.status,
                alert_sent=result.should_alert,
            )
            
        except Exception as e:
            logger.error(f"Job failed: {job.id}", error=str(e))
    
    async def run_job_now(self, job_id: str) -> dict:
        """Manually trigger a job (for testing or manual runs)."""
        jobs = load_all_jobs(self.jobs_dir)
        
        for job in jobs:
            if job.id == job_id:
                result = await self.executor.execute(job)
                
                # Store web alert as fallback (LLM notifies via MCP)
                if result.should_alert and self.notifier:
                    await self.notifier.store_web_alert(
                        user_id="user_default",
                        job_name=job.name,
                        message=result.alert_message,
                    )
                
                return {
                    "status": result.status,
                    "summary": result.summary,
                    "alert_sent": result.should_alert,
                    "duration": result.duration_seconds,
                }
        
        return {"error": f"Job not found: {job_id}"}


# Allow running standalone
async def main():
    """Run scheduler standalone."""
    import signal
    
    scheduler = SchedulerRunner()
    
    # Handle shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(scheduler.stop()))
    
    await scheduler.start()
    
    # Keep running until stopped
    while scheduler._running:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
