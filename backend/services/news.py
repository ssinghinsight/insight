import os
import httpx
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
BASE_URL = "https://newsapi.org/v2/everything"


async def fetch_news(company_name: str, company_id: str, db) -> list:
    from models import Signal

    if not NEWS_API_KEY:
        return []

    from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    params = {
        "q": f'"{company_name}"',
        "from": from_date,
        "sortBy": "relevancy",
        "pageSize": 5,
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"[news] Error fetching news for {company_name}: {e}")
        return []

    signals = []
    for article in data.get("articles", []):
        signal = Signal(
            company_id=company_id,
            source="news",
            signal_type="article",
            title=article.get("title"),
            url=article.get("url"),
            summary=article.get("description"),
            published_at=_parse_dt(article.get("publishedAt")),
        )
        db.add(signal)
        signals.append({
            "title": signal.title,
            "url": signal.url,
            "summary": signal.summary,
            "published_at": article.get("publishedAt"),
        })

    return signals


def _parse_dt(val: str | None):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
