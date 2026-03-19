import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


async def generate_summary(company_name: str, description: str | None, news_signals: list) -> str:
    news_text = "\n".join(
        f"- {s['title']}: {s.get('summary', '')}" for s in news_signals[:3]
    )
    prompt = (
        f"Company: {company_name}\n"
        f"Description: {description or 'No description available.'}\n"
        f"Recent news:\n{news_text or 'No recent news.'}\n\n"
        "Write a 3-sentence analyst summary of this company. Focus on: "
        "what they do, recent momentum or notable developments, and their market position."
    )

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ai] Summary error for {company_name}: {e}")
        return ""


async def generate_cracking_strategy(
    company_name: str,
    news_signals: list,
    linkedin_signals: list,
    crunchbase_signals: list,
    sf_activity_notes: list,
) -> str:
    def fmt_signals(signals: list, key: str = "title") -> str:
        if not signals:
            return "None available."
        return "\n".join(f"- {s.get(key, '')} — {s.get('summary', '')[:200]}" for s in signals[:5])

    def fmt_notes(notes: list) -> str:
        if not notes:
            return "No prior outreach recorded."
        lines = []
        for n in notes[:5]:
            date = n.get("date", "")
            subject = n.get("subject", "")
            desc = n.get("description", "")[:150] if n.get("description") else ""
            lines.append(f"- [{date}] {subject}: {desc}")
        return "\n".join(lines)

    prompt = f"""You are a senior business development professional helping a colleague get a meeting with a hard-to-reach company.

Company: {company_name}

Recent news:
{fmt_signals(news_signals)}

Leadership changes:
{fmt_signals(linkedin_signals, key='title')}

Funding activity:
{fmt_signals(crunchbase_signals)}

Past outreach attempts (CRM notes — do NOT suggest these again):
{fmt_notes(sf_activity_notes)}

Generate exactly 3 outreach strategies. For each, provide:
1. Hook: A specific, signal-based reason to reach out right now (tie it to a real data point above)
2. Target: The right person to contact at {company_name} and why them specifically
3. Opening line: A compelling, non-generic first sentence for your outreach

Format as JSON array with keys: hook, target, opening_line"""

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        # Normalize: model may return {"strategies": [...]} or [...]
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return json.dumps(parsed)
        for key in ("strategies", "outreach_strategies", "results"):
            if key in parsed:
                return json.dumps(parsed[key])
        return raw
    except Exception as e:
        print(f"[ai] Cracking strategy error for {company_name}: {e}")
        return "[]"
