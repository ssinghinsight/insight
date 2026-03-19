from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas import SignalOut

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("/{company_id}", response_model=list[SignalOut])
def get_signals(
    company_id: str,
    source: Optional[str] = Query(None, enum=["news", "linkedin", "crunchbase"]),
    db: Session = Depends(get_db),
):
    from models import Signal, Company

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    q = db.query(Signal).filter(Signal.company_id == company_id)
    if source:
        q = q.filter(Signal.source == source)

    return q.order_by(Signal.published_at.desc()).all()
