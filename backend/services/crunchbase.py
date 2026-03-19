import os
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")
BASE_URL = "https://api.crunchbase.com/api/v4"


async def fetch_crunchbase_signals(company_name: str, website: str | None, company_id: str, db) -> list:
    from models import Signal

    if not CRUNCHBASE_API_KEY:
        return []

    signals = []

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # Autocomplete to find the entity permalink
            autocomplete_resp = await client.get(
                f"{BASE_URL}/autocompletes",
                params={
                    "query": company_name,
                    "collection_ids": "organizations",
                    "limit": 1,
                    "user_key": CRUNCHBASE_API_KEY,
                },
            )
            autocomplete_resp.raise_for_status()
            auto_data = autocomplete_resp.json()

            entities = auto_data.get("entities", [])
            if not entities:
                return []

            permalink = entities[0].get("identifier", {}).get("permalink")
            if not permalink:
                return []

            # Fetch org details
            org_resp = await client.get(
                f"{BASE_URL}/entities/organizations/{permalink}",
                params={
                    "user_key": CRUNCHBASE_API_KEY,
                    "field_ids": "short_description,funding_total,last_funding_type,"
                                 "last_funding_at,num_employees_enum,founded_on,location_identifiers",
                },
            )
            org_resp.raise_for_status()
            org_data = org_resp.json()

            props = org_data.get("properties", {})

            funding_total = props.get("funding_total", {})
            last_funding_at = props.get("last_funding_at")
            last_funding_type = props.get("last_funding_type", {})

            if last_funding_at:
                funding_value = funding_total.get("value_usd", 0) if funding_total else 0
                round_name = last_funding_type.get("value", "Unknown round") if last_funding_type else "Funding"

                summary = (
                    f"{company_name} raised {_fmt_currency(funding_value)} total funding. "
                    f"Most recent round: {round_name} on {last_funding_at[:10]}."
                )

                signal = Signal(
                    company_id=company_id,
                    source="crunchbase",
                    signal_type="funding_round",
                    title=f"{company_name} — {round_name}",
                    url=f"https://www.crunchbase.com/organization/{permalink}",
                    summary=summary,
                    published_at=_parse_dt(last_funding_at),
                )
                db.add(signal)
                signals.append({
                    "title": signal.title,
                    "summary": summary,
                    "url": signal.url,
                    "funding_total": funding_value,
                    "last_funding_type": round_name,
                    "last_funding_at": last_funding_at,
                })

    except Exception as e:
        print(f"[crunchbase] Error for {company_name}: {e}")

    return signals


def _fmt_currency(value: float | int) -> str:
    if not value:
        return "undisclosed"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        try:
            return datetime.strptime(val[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            return None
