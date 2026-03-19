from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True)  # Salesforce Account ID
    name = Column(String, nullable=False)
    website = Column(String)
    industry = Column(String)
    priority = Column(Integer)  # 1–5 from Priority__c
    annual_revenue = Column(Float)
    description = Column(Text)
    last_sf_activity = Column(Date)
    sf_activity_notes = Column(Text)  # JSON array of past Salesforce tasks/notes
    ai_summary = Column(Text)
    cracking_brief = Column(Text)  # GPT-4o outreach strategy (Priority-5 only)
    enriched_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    signals = relationship("Signal", back_populates="company", cascade="all, delete-orphan")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    source = Column(String)       # 'news', 'linkedin', 'crunchbase'
    signal_type = Column(String)  # 'article', 'leadership_change', 'funding_round', 'conference'
    title = Column(Text)
    url = Column(String)
    summary = Column(Text)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="signals")


class DigestLog(Base):
    __tablename__ = "digest_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    recipient_email = Column(String)
    company_count = Column(Integer)
    status = Column(String)  # 'sent', 'failed'
    error = Column(Text)
