from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..statement.models import Statement
from ..statement.serializers import *
from ..utils import PdfToImageConverter, StatementExtractor

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
    statement = StatementCreate.create(statement_data, db)
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