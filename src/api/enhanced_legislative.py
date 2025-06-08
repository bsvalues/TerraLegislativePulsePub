from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.base import get_db
from models.legislation import Bill, Document, BillHistory
from pydantic import BaseModel

router = APIRouter()

class CommitteeActivity(BaseModel):
    committee: str
    date: datetime
    minutes_url: Optional[str]
    video_url: Optional[str]

class Hearing(BaseModel):
    type: str
    date: datetime
    location: str
    transcript_url: Optional[str]

class FiscalImpact(BaseModel):
    type: str
    impact: str
    amount: float
    analysis_url: Optional[str]

class EnhancedBillResponse(BaseModel):
    id: int
    source: str
    source_id: str
    title: str
    status: Optional[str]
    last_action: Optional[str]
    published_date: datetime
    updated_at: datetime
    relevance_score: float
    impact_score: float
    categories: List[str]
    committee_activity: List[CommitteeActivity]
    hearings: List[Hearing]
    fiscal_impact: List[FiscalImpact]
    
    class Config:
        orm_mode = True

@router.get("/bills", response_model=List[EnhancedBillResponse])
async def get_bills(
    db: Session = Depends(get_db),
    source: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    min_relevance: Optional[float] = None,
    min_impact: Optional[float] = None,
    committee: Optional[str] = None,
    has_hearing: Optional[bool] = None,
    has_fiscal_impact: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get bills with enhanced filtering options"""
    query = db.query(Bill)
    
    if source:
        query = query.filter(Bill.source == source)
    if status:
        query = query.filter(Bill.status == status)
    if category:
        query = query.filter(Bill.categories.contains([category]))
    if min_relevance:
        query = query.filter(Bill.relevance_score >= min_relevance)
    if min_impact:
        query = query.filter(Bill.impact_score >= min_impact)
    if committee:
        query = query.filter(Bill.committee_activity.contains([{"committee": committee}]))
    if has_hearing:
        query = query.filter(Bill.hearings != [])
    if has_fiscal_impact:
        query = query.filter(Bill.fiscal_impact != [])
    if start_date:
        query = query.filter(Bill.published_date >= start_date)
    if end_date:
        query = query.filter(Bill.published_date <= end_date)
    
    return query.order_by(Bill.impact_score.desc(), Bill.relevance_score.desc()).offset(offset).limit(limit).all()

@router.get("/bills/{bill_id}", response_model=EnhancedBillResponse)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific bill"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/committees")
async def get_committees(db: Session = Depends(get_db)):
    """Get all committees with their activity"""
    committees = {}
    for bill in db.query(Bill).all():
        for activity in bill.committee_activity:
            if activity["committee"] not in committees:
                committees[activity["committee"]] = {
                    "bill_count": 0,
                    "recent_activity": []
                }
            committees[activity["committee"]]["bill_count"] += 1
            committees[activity["committee"]]["recent_activity"].append({
                "bill_id": bill.id,
                "bill_title": bill.title,
                "date": activity["date"]
            })
    
    # Sort recent activity by date
    for committee in committees.values():
        committee["recent_activity"].sort(key=lambda x: x["date"], reverse=True)
        committee["recent_activity"] = committee["recent_activity"][:5]  # Keep only 5 most recent
    
    return committees

@router.get("/hearings")
async def get_hearings(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get all upcoming and recent hearings"""
    hearings = []
    for bill in db.query(Bill).all():
        for hearing in bill.hearings:
            if (not start_date or hearing["date"] >= start_date) and \
               (not end_date or hearing["date"] <= end_date):
                hearings.append({
                    "bill_id": bill.id,
                    "bill_title": bill.title,
                    "type": hearing["type"],
                    "date": hearing["date"],
                    "location": hearing["location"],
                    "transcript_url": hearing["transcript_url"]
                })
    
    return sorted(hearings, key=lambda x: x["date"])

@router.get("/fiscal-impact")
async def get_fiscal_impact(
    db: Session = Depends(get_db),
    min_amount: Optional[float] = None,
    impact_type: Optional[str] = None
):
    """Get bills with fiscal impact"""
    fiscal_impacts = []
    for bill in db.query(Bill).all():
        for impact in bill.fiscal_impact:
            if (not min_amount or abs(impact["amount"]) >= min_amount) and \
               (not impact_type or impact["type"] == impact_type):
                fiscal_impacts.append({
                    "bill_id": bill.id,
                    "bill_title": bill.title,
                    "type": impact["type"],
                    "impact": impact["impact"],
                    "amount": impact["amount"],
                    "analysis_url": impact["analysis_url"]
                })
    
    return sorted(fiscal_impacts, key=lambda x: abs(x["amount"]), reverse=True)

@router.get("/dashboard/enhanced-stats")
async def get_enhanced_dashboard_stats(db: Session = Depends(get_db)):
    """Get enhanced dashboard statistics"""
    total_bills = db.query(Bill).count()
    bills_by_category = {}
    bills_by_status = {}
    total_fiscal_impact = 0
    upcoming_hearings = []
    
    for bill in db.query(Bill).all():
        # Count by category
        for category in bill.categories:
            bills_by_category[category] = bills_by_category.get(category, 0) + 1
        
        # Count by status
        bills_by_status[bill.status] = bills_by_status.get(bill.status, 0) + 1
        
        # Calculate fiscal impact
        for impact in bill.fiscal_impact:
            total_fiscal_impact += impact["amount"]
        
        # Get upcoming hearings
        for hearing in bill.hearings:
            if hearing["date"] > datetime.utcnow():
                upcoming_hearings.append({
                    "bill_id": bill.id,
                    "bill_title": bill.title,
                    "type": hearing["type"],
                    "date": hearing["date"],
                    "location": hearing["location"]
                })
    
    # Sort upcoming hearings
    upcoming_hearings.sort(key=lambda x: x["date"])
    
    return {
        "total_bills": total_bills,
        "bills_by_category": bills_by_category,
        "bills_by_status": bills_by_status,
        "total_fiscal_impact": total_fiscal_impact,
        "upcoming_hearings": upcoming_hearings[:5]  # Show only 5 upcoming hearings
    } 