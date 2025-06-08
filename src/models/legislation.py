from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    status = Column(String)
    last_action = Column(String)
    published_date = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    relevance_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    categories = Column(JSON, default=list)
    committee_activity = Column(JSON, default=list)
    hearings = Column(JSON, default=list)
    fiscal_impact = Column(JSON, default=list)
    
    # Relationships
    documents = relationship("Document", back_populates="bill")
    history = relationship("BillHistory", back_populates="bill")
    
    __table_args__ = (
        # Ensure we don't duplicate bills from the same source
        UniqueConstraint('source', 'source_id', name='uix_source_source_id'),
    )

    def __repr__(self):
        return f"<Bill(id={self.id}, title='{self.title}', status='{self.status}')>"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    published_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    bill = relationship("Bill", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.type}')>"

class BillHistory(Base):
    __tablename__ = "bill_history"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    action = Column(String, nullable=False)
    action_date = Column(DateTime, nullable=False)
    actor = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    bill = relationship("Bill", back_populates="history")
    
    def __repr__(self):
        return f"<BillHistory(id={self.id}, action='{self.action}', date='{self.action_date}')>" 