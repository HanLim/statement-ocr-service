from pydantic import BaseModel
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from .models import Statement, StatementDetails, StatementTransaction

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

    @staticmethod
    def create(statement_data: "StatementCreate", db: Session) -> "Statement":
        statement = Statement(
            address=statement_data.address,
            name=statement_data.name,
            statement_date=statement_data.statement_date,
        )

        detail = StatementDetails(
            total_debit=statement_data.detail.total_debit,
            total_credit=statement_data.detail.total_credit,
            no_debit=statement_data.detail.no_debit,
            no_credit=statement_data.detail.no_credit
        )
        
        statement.detail = detail

        for transaction in statement_data.transactions:
            new_transaction = StatementTransaction(
                transaction_date=transaction.transaction_date,
                amount=transaction.amount
            )
            statement.transactions.append(new_transaction)

        db.add(statement)
        db.commit()
        db.refresh(statement)

        return statement


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
    detail: StatementDetailResponse
    transactions: List[StatementTransactionResponse]

    @staticmethod
    def serialize(statement: "Statement") -> "StatementResponse":
        detail = StatementDetailResponse(
            id=statement.detail.id,
            total_debit=statement.detail.total_debit,
            total_credit=statement.detail.total_credit,
            no_debit=statement.detail.no_debit,
            no_credit=statement.detail.no_credit
        )

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
