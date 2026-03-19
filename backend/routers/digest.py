from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import DigestResult

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("/preview", response_class=HTMLResponse)
def preview_digest(db: Session = Depends(get_db)):
    from services.email_digest import preview_digest as build_preview
    return build_preview(db)


@router.post("/send", response_model=DigestResult)
def send_digest(db: Session = Depends(get_db)):
    from services.email_digest import send_digest as do_send
    result = do_send(db)
    return DigestResult(status=result["status"], message=result["message"])
