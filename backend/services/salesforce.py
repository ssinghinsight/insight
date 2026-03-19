import json
import os
from datetime import datetime, timezone
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()


def get_sf_client() -> Salesforce:
    return Salesforce(
        username=os.getenv("SF_USERNAME"),
        password=os.getenv("SF_PASSWORD"),
        security_token=os.getenv("SF_SECURITY_TOKEN"),
        domain=os.getenv("SF_DOMAIN", "login"),
    )


def sync_accounts(db) -> int:
    from models import Company

    sf = get_sf_client()
    owner_id = os.getenv("SF_OWNER_ID")

    soql = f"""
        SELECT Id, Name, Website, Priority__c, Industry, AnnualRevenue,
               Description, LastActivityDate
        FROM Account
        WHERE OwnerId = '{owner_id}'
        ORDER BY Priority__c DESC NULLS LAST
    """
    result = sf.query_all(soql)
    records = result.get("records", [])

    synced = 0
    for rec in records:
        account_id = rec["Id"]

        # Pull last 10 activity notes for this account
        activity_notes = _fetch_activity_notes(sf, account_id)

        existing = db.query(Company).filter(Company.id == account_id).first()
        if existing:
            existing.name = rec.get("Name", "")
            existing.website = rec.get("Website")
            existing.industry = rec.get("Industry")
            existing.priority = _parse_priority(rec.get("Priority__c"))
            existing.annual_revenue = rec.get("AnnualRevenue")
            existing.description = rec.get("Description")
            existing.last_sf_activity = _parse_date(rec.get("LastActivityDate"))
            existing.sf_activity_notes = json.dumps(activity_notes)
        else:
            company = Company(
                id=account_id,
                name=rec.get("Name", ""),
                website=rec.get("Website"),
                industry=rec.get("Industry"),
                priority=_parse_priority(rec.get("Priority__c")),
                annual_revenue=rec.get("AnnualRevenue"),
                description=rec.get("Description"),
                last_sf_activity=_parse_date(rec.get("LastActivityDate")),
                sf_activity_notes=json.dumps(activity_notes),
                created_at=datetime.now(timezone.utc),
            )
            db.add(company)

        synced += 1

    db.commit()
    return synced


def _fetch_activity_notes(sf: Salesforce, account_id: str) -> list:
    notes = []

    # Tasks
    try:
        task_soql = f"""
            SELECT Subject, Description, ActivityDate, Status, Type
            FROM Task
            WHERE WhatId = '{account_id}'
            ORDER BY ActivityDate DESC
            LIMIT 10
        """
        task_result = sf.query(task_soql)
        for t in task_result.get("records", []):
            notes.append({
                "type": "task",
                "subject": t.get("Subject"),
                "description": t.get("Description"),
                "date": t.get("ActivityDate"),
                "status": t.get("Status"),
            })
    except Exception:
        pass

    # Notes (ContentNote or Note object)
    try:
        note_soql = f"""
            SELECT Title, Body, CreatedDate
            FROM Note
            WHERE ParentId = '{account_id}'
            ORDER BY CreatedDate DESC
            LIMIT 5
        """
        note_result = sf.query(note_soql)
        for n in note_result.get("records", []):
            notes.append({
                "type": "note",
                "subject": n.get("Title"),
                "description": n.get("Body"),
                "date": n.get("CreatedDate"),
            })
    except Exception:
        pass

    return notes


def _parse_priority(val) -> int | None:
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _parse_date(val: str | None):
    if not val:
        return None
    try:
        return datetime.strptime(val[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
