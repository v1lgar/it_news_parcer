import asyncio
import os
import structlog
from app.services.orchestrator import ParsingService
from app.db.base import init_db

logger = structlog.get_logger()

async def run_scheduler():
    interval_hours = float(os.getenv("PARSING_INTERVAL_HOURS", "1"))
    interval_seconds = interval_hours * 3600
    tags_env = os.getenv("PARSING_TAGS", "")
    tags = [t.strip() for t in tags_env.split(",") if t.strip()] if tags_env else None
    
    logger.info("Initializing database...")
    await init_db()
    
    service = ParsingService()
    
    while True:
        try:
            await service.run_all(tags=tags)
            logger.info("Scheduler sleeping", next_run_in_hours=interval_hours)
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Scheduler stopping...")
            break
        except Exception as e:
            logger.error("Scheduler error", error=str(e))
            await asyncio.sleep(60) # Wait a bit before retrying on error

if __name__ == "__main__":
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        pass
