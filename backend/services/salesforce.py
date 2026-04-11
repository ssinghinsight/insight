import json
import os
import httpx
from datetime import datetime, timezone, timedelta
from simple_salesforce import Salesforce
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# Access tokens live ~8 h; refresh proactively after 7 h
_TOKEN_MAX_AGE = timedelta(hours=7)


def get_sf_client(db) -> Salesforce:
    """Return an authenticated Salesforce client using the stored OAuth token.
    Refreshes the access token automatically if it is stale.
    Raises HTTP 401 if the user has not completed the OAuth flow yet.
    """
    from models import SalesforceAuth

    auth = db.query(SalesforceAuth).first()
    if not auth:
        raise HTTPException(
            status_code=401,
            detail="Salesforce not connected. Visit /api/auth/salesforce/login to authorise.",
        )

    if _token_is_stale(auth.token_issued_at):
        auth = _refresh_access_token(db, auth)

    return Salesforce(access_token=auth.access_token, instance_url=auth.instance_url)


def _token_is_stale(issued_at: datetime | None) -> bool:
    if not issued_at:
        return True
    # issued_at may be naive (stored without tz); treat as UTC
    if issued_at.tzinfo is None:
        issued_at = issued_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - issued_at > _TOKEN_MAX_AGE


def _refresh_access_token(db, auth):
    client_id = os.getenv("SF_OAUTH_CLIENT_ID")
    client_secret = os.getenv("SF_OAUTH_CLIENT_SECRET")
    domain = os.getenv("SF_DOMAIN", "login")
    token_url = f"https://{domain}.salesforce.com/services/oauth2/token"

    try:
        resp = httpx.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": auth.refresh_token,
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Salesforce token refresh failed: {exc.response.text}")

    payload = resp.json()
    auth.access_token = payload["access_token"]
    auth.instance_url = payload.get("instance_url", auth.instance_url)
    auth.token_issued_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(auth)
    return auth


def sync_accounts(db) -> int:
    from models import Company

    sf = get_sf_client(db)

    # Derive owner ID from the stored auth record
    from models import SalesforceAuth
    auth = db.query(SalesforceAuth).first()
    owner_id = auth.sf_user_id if auth else None

    owner_filter = f"WHERE OwnerId = '{owner_id}'" if owner_id else ""
    soql = f"""
        SELECT Id, Name, Website, Priority__c, Industry, AnnualRevenue,
               Description, LastActivityDate
        FROM Account
        {owner_filter}
        ORDER BY Priority__c DESC NULLS LAST
    """
    result = sf.query_all(soql)
    records = result.get("records", [])

    synced = 0
    for rec in records:
        account_id = rec["Id"]
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
        for t in sf.query(task_soql).get("records", []):
            notes.append({
                "type": "task",
                "subject": t.get("Subject"),
                "description": t.get("Description"),
                "date": t.get("ActivityDate"),
                "status": t.get("Status"),
            })
    except Exception:
        pass

    # Notes
    try:
        note_soql = f"""
            SELECT Title, Body, CreatedDate
            FROM Note
            WHERE ParentId = '{account_id}'
            ORDER BY CreatedDate DESC
            LIMIT 5
        """
        for n in sf.query(note_soql).get("records", []):
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
