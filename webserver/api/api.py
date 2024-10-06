from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..statement.models import Statement, StatementTransaction, StatementDetails
from ..statement.serializers import *

router = APIRouter()


@router.get("/", response_model=List[StatementListResponse])
async def list_statement(db: Session=Depends(get_db)):
    statements = db.query(Statement).all()
    return statements


@router.get("/{statement_id}", response_model=StatementResponse)
async def get_one_statement(statement_id: int, db: Session=Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return StatementResponse.serialize(statement)


@router.post("/")
async def create_statement(statement_data: StatementCreate, db: Session=Depends(get_db)):
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


@router.post("/upload/")
async def upload_statement(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    content_type = file.content_type

    return {
        "filename": filename,
        "content_type": content_type,
        "size": len(content)
    }