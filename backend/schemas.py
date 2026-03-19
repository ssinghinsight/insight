from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class SignalOut(BaseModel):
    id: int
    company_id: str
    source: str
    signal_type: str
    title: Optional[str]
    url: Optional[str]
    summary: Optional[str]
    published_at: Optional[datetime]
    fetched_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CompanyOut(BaseModel):
    id: str
    name: str
    website: Optional[str]
    industry: Optional[str]
    priority: Optional[int]
    annual_revenue: Optional[float]
    description: Optional[str]
    last_sf_activity: Optional[date]
    ai_summary: Optional[str]
    cracking_brief: Optional[str]
    enriched_at: Optional[datetime]
    signals: List[SignalOut] = []

    model_config = {"from_attributes": True}


class CompanyList(BaseModel):
    id: str
    name: str
    website: Optional[str]
    industry: Optional[str]
    priority: Optional[int]
    last_sf_activity: Optional[date]
    ai_summary: Optional[str]
    has_cracking_brief: bool
    enriched_at: Optional[datetime]
    signal_count: int = 0

    model_config = {"from_attributes": True}


class SyncResult(BaseModel):
    synced: int
    message: str


class DigestResult(BaseModel):
    status: str
    message: str
