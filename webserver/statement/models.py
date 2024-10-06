from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float

from ..database import Base

class Statement(Base):
    __tablename__ = "statement"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    name = Column(String)
    statement_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())

    detail = relationship("StatementDetails", back_populates="statement", uselist=False)
    transactions = relationship("StatementTransaction", back_populates="statement")


class StatementDetails(Base):
    __tablename__ = "statement_details"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey('statement.id'), unique=True)
    created_at = Column(DateTime, default=datetime.now())
    
    total_debit = Column(Float, default=0)
    total_credit = Column(Float, default=0)
    no_debit = Column(Integer, default=0)
    no_credit = Column(Integer, default=0)

    statement = relationship("Statement", back_populates="detail")


class StatementTransaction(Base):
    __tablename__ = "statement_transactions"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey('statement.id'))
    transaction_date = Column(DateTime)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now())
    
    statement = relationship("Statement", back_populates="transactions")


