from fastapi import APIRouter

from .api import api

router = APIRouter()

router.include_router(api.router, prefix='/statements', tags=["statements"])