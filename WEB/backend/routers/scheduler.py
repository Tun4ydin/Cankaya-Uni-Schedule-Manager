from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from services.scheduler_service import scheduler_service

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

class CombinationRequest(BaseModel):
    courses: List[str] = Field(..., description="List of course codes e.g. ['CENG111', 'MATH157']")
    locked_sections: Optional[Dict[str, str]] = Field(default_factory=dict, description="Locked section numbers per course e.g. {'CENG111': '1'}")
    allowed_instructors: Optional[Dict[str, List[str]]] = Field(default_factory=dict, description="Allowed instructor names per course")
    preferences: Optional[Dict[str, bool]] = Field(default_factory=dict, description="free_friday, free_monday, no_morning")
    custom_blocks: Optional[Dict[str, Any]] = Field(default=None, description="Custom timetable blocks")

class ConflictRequest(BaseModel):
    sections: List[Dict[str, Any]] = Field(..., description="List of dicts with course_code and section_no")
    custom_blocks: Optional[Dict[str, Any]] = Field(default=None)

@router.post("/combinations")
def get_combinations(req: CombinationRequest):
    return scheduler_service.generate_schedule_combinations(
        selected_courses=req.courses,
        locked_sections=req.locked_sections,
        allowed_instructors=req.allowed_instructors,
        preferences=req.preferences,
        custom_blocks=req.custom_blocks
    )

@router.post("/conflicts")
def check_conflicts(req: ConflictRequest):
    return scheduler_service.check_conflicts(
        sections_data=req.sections,
        custom_blocks=req.custom_blocks
    )
