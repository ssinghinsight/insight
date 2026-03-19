import os
import json
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
DIGEST_RECIPIENT = os.getenv("DIGEST_RECIPIENT_EMAIL", "")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


def _build_html(companies: list, signals_by_company: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("digest.html")
    return template.render(
        companies=companies,
        signals_by_company=signals_by_company,
        generated_at=datetime.now(timezone.utc).strftime("%B %d, %Y"),
    )


def send_digest(db) -> dict:
    from models import Company, Signal, DigestLog

    if not SENDGRID_API_KEY or not DIGEST_RECIPIENT:
        return {"status": "skipped", "message": "Missing SendGrid config."}

    # Sort: Priority-5 first, then descending
    companies = (
        db.query(Company)
        .order_by(Company.priority.desc().nullslast())
        .all()
    )

    signals_by_company = {}
    for company in companies:
        signals = (
            db.query(Signal)
            .filter(Signal.company_id == company.id)
            .order_by(Signal.published_at.desc())
            .limit(5)
            .all()
        )
        cracking = []
        if company.cracking_brief:
            try:
                cracking = json.loads(company.cracking_brief)
            except json.JSONDecodeError:
                pass
        signals_by_company[company.id] = {
            "signals": signals,
            "cracking": cracking,
        }

    html = _build_html(companies, signals_by_company)

    message = Mail(
        from_email="digest@insight-sourcing.app",
        to_emails=DIGEST_RECIPIENT,
        subject=f"Insight Sourcing Digest — {datetime.now(timezone.utc).strftime('%b %d')}",
        html_content=html,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        log = DigestLog(
            recipient_email=DIGEST_RECIPIENT,
            company_count=len(companies),
            status="sent",
        )
        db.add(log)
        db.commit()
        return {"status": "sent", "message": f"Digest sent to {DIGEST_RECIPIENT}."}
    except Exception as e:
        log = DigestLog(
            recipient_email=DIGEST_RECIPIENT,
            company_count=len(companies),
            status="failed",
            error=str(e),
        )
        db.add(log)
        db.commit()
        return {"status": "failed", "message": str(e)}


def preview_digest(db) -> str:
    from models import Company, Signal

    companies = (
        db.query(Company)
        .order_by(Company.priority.desc().nullslast())
        .all()
    )
    signals_by_company = {}
    for company in companies:
        signals = (
            db.query(Signal)
            .filter(Signal.company_id == company.id)
            .order_by(Signal.published_at.desc())
            .limit(5)
            .all()
        )
        cracking = []
        if company.cracking_brief:
            try:
                cracking = json.loads(company.cracking_brief)
            except json.JSONDecodeError:
                pass
        signals_by_company[company.id] = {
            "signals": signals,
            "cracking": cracking,
        }

    return _build_html(companies, signals_by_company)
