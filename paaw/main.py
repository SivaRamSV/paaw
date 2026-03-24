"""
PAAW Main Entry Point

Starts the PAAW application with all services.
"""

import asyncio
import logging
import signal
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog
import uvloop

from paaw.config import settings

# Use uvloop for better async performance
uvloop.install()

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure rotating file handlers
# PAAW application logs (structlog JSON)
paaw_handler = RotatingFileHandler(
    LOGS_DIR / "paaw.log",
    maxBytes=10 * 1024 * 1024,  # 10MB per file
    backupCount=5,  # Keep 5 backup files (paaw.log.1, paaw.log.2, etc.)
    encoding="utf-8",
)
paaw_handler.setLevel(getattr(logging, settings.log_level, logging.INFO))

# Uvicorn access logs (separate file)
uvicorn_handler = RotatingFileHandler(
    LOGS_DIR / "uvicorn.log",
    maxBytes=10 * 1024 * 1024,  # 10MB per file
    backupCount=5,
    encoding="utf-8",
)
uvicorn_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
uvicorn_handler.setLevel(logging.INFO)

# Console handler for stdout (still useful for dev)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, settings.log_level, logging.INFO))

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Allow all, handlers filter
root_logger.addHandler(console_handler)
root_logger.addHandler(paaw_handler)

# Configure uvicorn loggers to use separate file
for uvicorn_logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
    uv_logger = logging.getLogger(uvicorn_logger_name)
    uv_logger.handlers = []  # Remove default handlers
    uv_logger.addHandler(uvicorn_handler)
    uv_logger.addHandler(console_handler)  # Also show in console
    uv_logger.propagate = False  # Don't propagate to root

# Configure structured logging for PAAW
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def main():
    """Main application entry point."""
    logger.info(
        "Starting PAAW",
        version="0.1.0",
        debug=settings.debug,
        model=settings.llm.default_model,
    )

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def handle_shutdown(sig):
        logger.info("Received shutdown signal", signal=sig.name)
        shutdown_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: handle_shutdown(s))

    try:
        # Import here to avoid circular imports
        from paaw.api.server import create_app, run_server

        # Create FastAPI app
        app = create_app()

        # Run the server
        await run_server(app, shutdown_event)

    except Exception as e:
        logger.error("Fatal error", error=str(e))
        sys.exit(1)

    logger.info("PAAW shutdown complete")


def run():
    """Run the application."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
