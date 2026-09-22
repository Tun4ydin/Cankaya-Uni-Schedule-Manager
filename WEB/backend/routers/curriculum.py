from fastapi import APIRouter, Query
from typing import Optional
from services.data_service import data_service
from services.transcript_service import transcript_service

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

@router.get("/progress")
def get_progress(primary_dept: Optional[str] = Query(None)):
    dept = primary_dept or data_service.get_profile().get("primary_dept", "CENG")
    return data_service.get_curriculum_progress(primary_dept=dept)

@router.get("/prerequisites/{code}")
def check_prerequisites(code: str):
    return transcript_service.check_prerequisites(code)
