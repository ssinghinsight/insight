import os
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_LINKEDIN_HOST", "fresh-linkedin-profile-data.p.rapidapi.com")

EXEC_KEYWORDS = ["CEO", "CFO", "CTO", "COO", "CMO", "CPO", "President", "VP ", "Vice President",
                 "Head of", "Chief", "Director", "joined", "appointed", "named", "promoted"]


async def fetch_linkedin_signals(company_name: str, website: str | None, company_id: str, db) -> list:
    from models import Signal

    if not RAPIDAPI_KEY:
        return []

    # Search for company on LinkedIn
    domain = _extract_domain(website) if website else None
    query = domain or company_name

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }

    signals = []

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # Search for company
            search_resp = await client.get(
                "https://fresh-linkedin-profile-data.p.rapidapi.com/search-companies",
                headers=headers,
                params={"keywords": company_name, "page": "1"},
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()

            companies = search_data.get("data", [])
            if not companies:
                return []

            company_url = companies[0].get("linkedin_url", "")
            if not company_url:
                return []

            # Get recent posts / updates
            posts_resp = await client.get(
                "https://fresh-linkedin-profile-data.p.rapidapi.com/get-company-posts",
                headers=headers,
                params={"linkedin_url": company_url, "type": "posts"},
            )
            posts_resp.raise_for_status()
            posts_data = posts_resp.json()

            for post in posts_data.get("data", [])[:10]:
                text = post.get("text", "")
                if any(kw.lower() in text.lower() for kw in EXEC_KEYWORDS):
                    signal = Signal(
                        company_id=company_id,
                        source="linkedin",
                        signal_type="leadership_change",
                        title=f"Leadership signal at {company_name}",
                        url=post.get("post_url"),
                        summary=text[:500],
                        published_at=_parse_dt(post.get("posted_at")),
                    )
                    db.add(signal)
                    signals.append({
                        "title": signal.title,
                        "summary": signal.summary,
                        "url": signal.url,
                    })

    except Exception as e:
        print(f"[linkedin] Error for {company_name}: {e}")

    return signals


def _extract_domain(url: str) -> str:
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return url.split("/")[0]


def _parse_dt(val) -> datetime | None:
    if not val:
        return None
    try:
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, tz=timezone.utc)
        return datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
