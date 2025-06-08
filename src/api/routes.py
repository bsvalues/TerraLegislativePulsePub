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
    
    class Config:
        orm_mode = True

class DocumentResponse(BaseModel):
    id: int
    bill_id: int
    title: str
    url: str
    document_type: Optional[str]
    published_date: datetime
    
    class Config:
        orm_mode = True

class BillHistoryResponse(BaseModel):
    id: int
    bill_id: int
    action: str
    action_date: datetime
    description: Optional[str]
    
    class Config:
        orm_mode = True

@router.get("/bills", response_model=List[BillResponse])
async def get_bills(
    db: Session = Depends(get_db),
    source: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    query = db.query(Bill)
    
    if source:
        query = query.filter(Bill.source == source)
    if status:
        query = query.filter(Bill.status == status)
    if start_date:
        query = query.filter(Bill.published_date >= start_date)
    if end_date:
        query = query.filter(Bill.published_date <= end_date)
    
    return query.order_by(Bill.published_date.desc()).offset(offset).limit(limit).all()

@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/bills/{bill_id}/documents", response_model=List[DocumentResponse])
async def get_bill_documents(bill_id: int, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.bill_id == bill_id).all()

@router.get("/bills/{bill_id}/history", response_model=List[BillHistoryResponse])
async def get_bill_history(bill_id: int, db: Session = Depends(get_db)):
    return db.query(BillHistory).filter(BillHistory.bill_id == bill_id).order_by(BillHistory.action_date.desc()).all()

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_bills = db.query(Bill).count()
    bills_by_source = db.query(Bill.source, db.func.count(Bill.id)).group_by(Bill.source).all()
    recent_bills = db.query(Bill).order_by(Bill.published_date.desc()).limit(5).all()
    
    return {
        "total_bills": total_bills,
        "bills_by_source": dict(bills_by_source),
        "recent_bills": recent_bills
    } 