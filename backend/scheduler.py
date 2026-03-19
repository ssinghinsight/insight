import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Daily at 6:00 AM UTC — enrich all companies
    scheduler.add_job(
        _run_enrichment,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_enrichment",
        replace_existing=True,
    )

    # Daily at 7:00 AM UTC — send digest email
    scheduler.add_job(
        _send_digest,
        trigger=CronTrigger(hour=7, minute=0),
        id="daily_digest",
        replace_existing=True,
    )

    return scheduler


async def _run_enrichment():
    from services.enricher import run_all_companies
    print("[scheduler] Starting daily enrichment...")
    count = await run_all_companies()
    print(f"[scheduler] Enriched {count} companies.")


async def _send_digest():
    from database import db_session
    from services.email_digest import send_digest
    print("[scheduler] Sending daily digest...")
    with db_session() as db:
        result = send_digest(db)
    print(f"[scheduler] Digest result: {result}")
