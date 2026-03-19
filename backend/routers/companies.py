from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas import CompanyOut, CompanyList, SyncResult

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=list[CompanyList])
def list_companies(
    priority: Optional[int] = Query(None, ge=1, le=5),
    industry: Optional[str] = None,
    has_cracking_brief: Optional[bool] = None,
    sort: str = Query("priority", enum=["priority", "last_activity", "name"]),
    db: Session = Depends(get_db),
):
    from models import Company, Signal
    from sqlalchemy import func

    q = db.query(Company)

    if priority is not None:
        q = q.filter(Company.priority == priority)
    if industry:
        q = q.filter(Company.industry.ilike(f"%{industry}%"))
    if has_cracking_brief is True:
        q = q.filter(Company.cracking_brief.isnot(None), Company.cracking_brief != "[]")
    elif has_cracking_brief is False:
        q = q.filter((Company.cracking_brief.is_(None)) | (Company.cracking_brief == "[]"))

    if sort == "priority":
        q = q.order_by(Company.priority.desc().nullslast())
    elif sort == "last_activity":
        q = q.order_by(Company.last_sf_activity.desc().nullslast())
    elif sort == "name":
        q = q.order_by(Company.name)

    companies = q.all()

    # Attach signal counts
    signal_counts = {
        cid: count
        for cid, count in db.query(Signal.company_id, func.count(Signal.id))
        .group_by(Signal.company_id)
        .all()
    }

    result = []
    for c in companies:
        result.append(CompanyList(
            id=c.id,
            name=c.name,
            website=c.website,
            industry=c.industry,
            priority=c.priority,
            last_sf_activity=c.last_sf_activity,
            ai_summary=c.ai_summary,
            has_cracking_brief=bool(c.cracking_brief and c.cracking_brief != "[]"),
            enriched_at=c.enriched_at,
            signal_count=signal_counts.get(c.id, 0),
        ))

    return result


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: str, db: Session = Depends(get_db)):
    from models import Company

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/sync", response_model=SyncResult)
def sync_companies(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from services.salesforce import sync_accounts

    try:
        count = sync_accounts(db)
        return SyncResult(synced=count, message=f"Synced {count} accounts from Salesforce.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Salesforce sync failed: {e}")


@router.post("/{company_id}/enrich")
async def enrich_one(company_id: str, db: Session = Depends(get_db)):
    from services.enricher import enrich_company
    from models import Company

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    await enrich_company(company_id)
    return {"status": "ok", "message": f"Enrichment complete for {company.name}"}
