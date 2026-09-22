from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from services.data_service import data_service

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdateRequest(BaseModel):
    primary_dept: Optional[str] = None
    secondary_dept: Optional[str] = None
    secondary_type: Optional[str] = None
    theme: Optional[str] = None

class CustomBlockRequest(BaseModel):
    day: str
    time_slot: str
    title: str
    note: Optional[str] = ""
    color: Optional[str] = "amber"

class CustomBlockDeleteRequest(BaseModel):
    day: str
    time_slot: str

class PassedCourseRequest(BaseModel):
    code: str
    grade: Optional[str] = "CC"
    name: Optional[str] = ""

class AllPassedCoursesRequest(BaseModel):
    passed_courses: Dict[str, Any]

@router.get("")
def get_profile():
    return data_service.get_profile()

@router.put("")
def update_profile(req: ProfileUpdateRequest):
    return data_service.update_profile(req.model_dump(exclude_unset=True))

@router.post("/custom-block")
def set_custom_block(req: CustomBlockRequest):
    return data_service.set_custom_block(
        day=req.day,
        time_slot=req.time_slot,
        title=req.title,
        note=req.note or "",
        color=req.color or "amber"
    )

@router.delete("/custom-block")
def delete_custom_block(req: CustomBlockDeleteRequest):
    return data_service.delete_custom_block(day=req.day, time_slot=req.time_slot)

@router.post("/passed-courses")
def add_passed_course(req: PassedCourseRequest):
    return data_service.set_passed_course(req.code, req.grade or "CC", req.name or "")

@router.put("/passed-courses")
def set_all_passed_courses(req: AllPassedCoursesRequest):
    return data_service.set_all_passed_courses(req.passed_courses)

@router.delete("/passed-courses/{code}")
def delete_passed_course(code: str):
    return data_service.remove_passed_course(code)
