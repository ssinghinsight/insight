import asyncio
import json
from datetime import datetime, timezone
from database import db_session

BATCH_SIZE = 5
BATCH_DELAY_SECS = 2  # pause between batches to respect rate limits


async def enrich_company(company_id: str) -> None:
    from services.news import fetch_news
    from services.linkedin import fetch_linkedin_signals
    from services.crunchbase import fetch_crunchbase_signals
    from services.ai_analyst import generate_summary, generate_cracking_strategy
    from models import Company, Signal

    with db_session() as db:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            print(f"[enricher] Company {company_id} not found.")
            return

        name = company.name
        website = company.website
        priority = company.priority
        description = company.description
        sf_notes = json.loads(company.sf_activity_notes or "[]")

        # Clear old signals
        db.query(Signal).filter(Signal.company_id == company_id).delete()

        # Fetch all signals concurrently
        news_signals, linkedin_signals, crunchbase_signals = await asyncio.gather(
            fetch_news(name, company_id, db),
            fetch_linkedin_signals(name, website, company_id, db),
            fetch_crunchbase_signals(name, website, company_id, db),
        )

        # Generate AI summary
        ai_summary = await generate_summary(name, description, news_signals)

        # Generate cracking brief only for Priority-5
        cracking_brief = None
        if priority == 5:
            cracking_brief = await generate_cracking_strategy(
                name,
                news_signals,
                linkedin_signals,
                crunchbase_signals,
                sf_notes,
            )

        company.ai_summary = ai_summary
        company.cracking_brief = cracking_brief
        company.enriched_at = datetime.now(timezone.utc)

    print(f"[enricher] Enriched: {name} (priority={priority})")


async def run_all_companies() -> int:
    from models import Company

    with db_session() as db:
        company_ids = [c.id for c in db.query(Company.id).all()]

    total = len(company_ids)
    print(f"[enricher] Starting enrichment for {total} companies...")

    for i in range(0, total, BATCH_SIZE):
        batch = company_ids[i:i + BATCH_SIZE]
        await asyncio.gather(*[enrich_company(cid) for cid in batch])
        if i + BATCH_SIZE < total:
            await asyncio.sleep(BATCH_DELAY_SECS)

    print(f"[enricher] Done. Enriched {total} companies.")
    return total
