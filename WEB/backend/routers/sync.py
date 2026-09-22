from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from services.sync_service import sync_service

router = APIRouter(prefix="/api/sync", tags=["sync"])

class StartSyncRequest(BaseModel):
    sync_courses: Optional[bool] = True
    sync_curricula: Optional[bool] = True
    dept_list: Optional[List[str]] = None

@router.post("/start")
def start_sync(req: StartSyncRequest):
    return sync_service.start_sync(
        sync_courses=req.sync_courses if req.sync_courses is not None else True,
        sync_curricula=req.sync_curricula if req.sync_curricula is not None else True,
        dept_list=req.dept_list
    )

@router.get("/status")
def get_sync_status():
    return sync_service.get_status()

@router.post("/cancel")
def cancel_sync():
    return sync_service.cancel()
