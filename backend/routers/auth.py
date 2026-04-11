import os
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

_SF_DOMAIN = lambda: os.getenv("SF_DOMAIN", "login")
_TOKEN_URL = lambda: f"https://{_SF_DOMAIN()}.salesforce.com/services/oauth2/token"
_AUTH_URL = lambda: f"https://{_SF_DOMAIN()}.salesforce.com/services/oauth2/authorize"


@router.get("/salesforce/login")
def salesforce_login():
    """Redirect the browser to Salesforce OAuth consent screen."""
    client_id = os.getenv("SF_OAUTH_CLIENT_ID")
    redirect_uri = os.getenv("SF_OAUTH_REDIRECT_URI", "http://localhost:8000/api/auth/salesforce/callback")
    if not client_id:
        raise HTTPException(500, "SF_OAUTH_CLIENT_ID is not configured")
    url = (
        f"{_AUTH_URL()}?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
    )
    return RedirectResponse(url)


@router.get("/salesforce/callback")
def salesforce_callback(code: str, db: Session = Depends(get_db)):
    """Exchange the authorization code for tokens and persist them."""
    from models import SalesforceAuth

    client_id = os.getenv("SF_OAUTH_CLIENT_ID")
    client_secret = os.getenv("SF_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("SF_OAUTH_REDIRECT_URI", "http://localhost:8000/api/auth/salesforce/callback")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    if not client_id or not client_secret:
        raise HTTPException(500, "SF_OAUTH_CLIENT_ID / SF_OAUTH_CLIENT_SECRET not configured")

    # Exchange code for tokens
    try:
        resp = httpx.post(
            _TOKEN_URL(),
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Salesforce token exchange failed: {exc.response.text}")

    payload = resp.json()
    access_token = payload["access_token"]
    refresh_token = payload.get("refresh_token", "")
    instance_url = payload["instance_url"]

    # Parse the user ID out of the identity URL
    # e.g. https://login.salesforce.com/id/00D.../005...
    identity_url = payload.get("id", "")
    sf_user_id = identity_url.rstrip("/").split("/")[-1] if identity_url else None

    # Upsert — single-user app keeps one row
    auth = db.query(SalesforceAuth).first()
    now = datetime.now(timezone.utc)
    if auth:
        auth.access_token = access_token
        auth.refresh_token = refresh_token
        auth.instance_url = instance_url
        auth.sf_user_id = sf_user_id
        auth.token_issued_at = now
    else:
        auth = SalesforceAuth(
            access_token=access_token,
            refresh_token=refresh_token,
            instance_url=instance_url,
            sf_user_id=sf_user_id,
            token_issued_at=now,
        )
        db.add(auth)
    db.commit()

    return RedirectResponse(f"{frontend_url}?sf_connected=true")


@router.get("/salesforce/status")
def salesforce_status(db: Session = Depends(get_db)):
    """Return whether Salesforce is currently connected."""
    from models import SalesforceAuth

    auth = db.query(SalesforceAuth).first()
    if not auth:
        return {"connected": False}
    return {
        "connected": True,
        "sf_user_id": auth.sf_user_id,
        "instance_url": auth.instance_url,
        "token_issued_at": auth.token_issued_at.isoformat() if auth.token_issued_at else None,
    }


@router.delete("/salesforce")
def salesforce_disconnect(db: Session = Depends(get_db)):
    """Remove stored Salesforce tokens."""
    from models import SalesforceAuth

    auth = db.query(SalesforceAuth).first()
    if auth:
        db.delete(auth)
        db.commit()
    return {"disconnected": True}
