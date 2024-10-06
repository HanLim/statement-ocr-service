from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .models import Statement


class StatementDetailCreate(BaseModel):
    total_debit: float
    total_credit: float
    no_debit: int
    no_credit: int


class StatementTransactionCreate(BaseModel):
    transaction_date: datetime
    amount: float



class StatementCreate(BaseModel):
    address: str
    name: str
    statement_date: datetime
    detail: StatementDetailCreate
    transactions: List[StatementTransactionCreate]


class StatementListResponse(BaseModel):
    id: int
    statement_date: datetime
    created_at: datetime


class StatementDetailResponse(BaseModel):
    id: int
    total_debit: float
    total_credit: float
    no_debit: int
    no_credit: int


class StatementTransactionResponse(BaseModel):
    id: int
    transaction_date: datetime
    amount: float


class StatementResponse(BaseModel):
    id: int
    address: str
    name: str
    statement_date: datetime
    created_at: datetime
    detail: List[StatementDetailResponse]
    transactions: List[StatementTransactionResponse]

    @staticmethod
    def serialize(statement: Statement) -> "StatementResponse":
        detail = [
            StatementDetailResponse(
                id=detail.id,
                total_debit=detail.total_debit,
                total_credit=detail.total_credit,
                no_debit=detail.no_debit,
                no_credit=detail.no_credit
            ) for detail in statement.detail
        ]

        transactions = [
            StatementTransactionResponse(
                id=transaction.id,
                transaction_date=transaction.transaction_date,
                amount=transaction.amount
            ) for transaction in statement.transactions
        ]

        return StatementResponse(
            id=statement.id,
            address=statement.address,
            name=statement.name,
            statement_date=statement.statement_date,
            created_at=statement.created_at,
            detail=detail,
            transactions=transactions
        )
