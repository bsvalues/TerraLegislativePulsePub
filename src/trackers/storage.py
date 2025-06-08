from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.legislation import Bill, Document, BillHistory

class TrackerStorage:
    def __init__(self, db: Session):
        self.db = db
    
    async def store_bills(self, bills: List[Dict[str, Any]]) -> None:
        for bill_data in bills:
            try:
                # Check if bill exists
                existing_bill = self.db.query(Bill).filter_by(
                    source=bill_data["source"],
                    source_id=bill_data.get("bill_id") or bill_data.get("guid")
                ).first()
                
                if existing_bill:
                    # Update existing bill
                    existing_bill.title = bill_data["title"]
                    existing_bill.status = bill_data.get("status")
                    existing_bill.last_action = bill_data.get("last_action")
                    existing_bill.updated_at = datetime.utcnow()
                else:
                    # Create new bill
                    new_bill = Bill(
                        source=bill_data["source"],
                        source_id=bill_data.get("bill_id") or bill_data.get("guid"),
                        title=bill_data["title"],
                        status=bill_data.get("status"),
                        last_action=bill_data.get("last_action"),
                        published_date=datetime.fromisoformat(bill_data.get("published_date", datetime.utcnow().isoformat())),
                        updated_at=datetime.utcnow()
                    )
                    self.db.add(new_bill)
                
                # Store documents if present
                if "documents" in bill_data:
                    await self.store_documents(bill_data["documents"], existing_bill or new_bill)
                
                # Store history if present
                if "history" in bill_data:
                    await self.store_history(bill_data["history"], existing_bill or new_bill)
                
                self.db.commit()
                
            except IntegrityError:
                self.db.rollback()
                continue
    
    async def store_documents(self, documents: List[Dict[str, Any]], bill: Bill) -> None:
        for doc_data in documents:
            try:
                existing_doc = self.db.query(Document).filter_by(
                    bill_id=bill.id,
                    url=doc_data["url"]
                ).first()
                
                if not existing_doc:
                    new_doc = Document(
                        bill_id=bill.id,
                        title=doc_data["title"],
                        url=doc_data["url"],
                        document_type=doc_data.get("document_type"),
                        published_date=datetime.fromisoformat(doc_data.get("published_date", datetime.utcnow().isoformat()))
                    )
                    self.db.add(new_doc)
                    self.db.commit()
                    
            except IntegrityError:
                self.db.rollback()
                continue
    
    async def store_history(self, history_items: List[Dict[str, Any]], bill: Bill) -> None:
        for history_data in history_items:
            try:
                existing_history = self.db.query(BillHistory).filter_by(
                    bill_id=bill.id,
                    action=history_data["action"],
                    action_date=datetime.fromisoformat(history_data["action_date"])
                ).first()
                
                if not existing_history:
                    new_history = BillHistory(
                        bill_id=bill.id,
                        action=history_data["action"],
                        action_date=datetime.fromisoformat(history_data["action_date"]),
                        description=history_data.get("description")
                    )
                    self.db.add(new_history)
                    self.db.commit()
                    
            except IntegrityError:
                self.db.rollback()
                continue 