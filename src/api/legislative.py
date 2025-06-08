from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from models.base import get_db
from models.legislation import Bill, Document, BillHistory
from pydantic import BaseModel

router = APIRouter()

class BillResponse(BaseModel):
    id: int
    source: str
    source_id: str
    title: str
    status: Optional[str]
    last_action: Optional[str]
    published_date: datetime
    updated_at: datetime
    relevance_score: float
    categories: List[str]
    
    class Config:
        orm_mode = True

@router.get("/bills", response_model=List[BillResponse])
async def get_bills(
    db: Session = Depends(get_db),
    source: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    min_relevance: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get bills with filtering options"""
    query = db.query(Bill)
    
    if source:
        query = query.filter(Bill.source == source)
    if status:
        query = query.filter(Bill.status == status)
    if category:
        query = query.filter(Bill.categories.contains([category]))
    if min_relevance:
        query = query.filter(Bill.relevance_score >= min_relevance)
    if start_date:
        query = query.filter(Bill.published_date >= start_date)
    if end_date:
        query = query.filter(Bill.published_date <= end_date)
    
    return query.order_by(Bill.relevance_score.desc(), Bill.published_date.desc()).offset(offset).limit(limit).all()

@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific bill"""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/bills/{bill_id}/history", response_model=List[BillHistoryResponse])
async def get_bill_history(bill_id: int, db: Session = Depends(get_db)):
    """Get the history of actions for a specific bill"""
    return db.query(BillHistory).filter(BillHistory.bill_id == bill_id).order_by(BillHistory.action_date.desc()).all()

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available bill categories"""
    categories = set()
    for bill in db.query(Bill).all():
        categories.update(bill.categories)
    return sorted(list(categories))

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_bills = db.query(Bill).count()
    bills_by_category = {}
    bills_by_status = {}
    
    for bill in db.query(Bill).all():
        # Count by category
        for category in bill.categories:
            bills_by_category[category] = bills_by_category.get(category, 0) + 1
        
        # Count by status
        bills_by_status[bill.status] = bills_by_status.get(bill.status, 0) + 1
    
    recent_bills = db.query(Bill).order_by(Bill.published_date.desc()).limit(5).all()
    
    return {
        "total_bills": total_bills,
        "bills_by_category": bills_by_category,
        "bills_by_status": bills_by_status,
        "recent_bills": recent_bills
    } 