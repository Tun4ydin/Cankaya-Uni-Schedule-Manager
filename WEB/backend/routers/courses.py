from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.data_service import data_service

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("")
def list_courses(
    query: str = Query("", description="Course code or instructor name search"),
    dept: Optional[str] = Query(None, description="Department code filter e.g. CENG, MATH"),
    course_type: Optional[str] = Query(None, description="Filter: ZORUNLU, ZORUNLU_CAP, ZORUNLU_YANDAL, SECMELI, TEKNIK_SECMELI, SERBEST_SECMELI"),
    primary_dept: Optional[str] = Query(None),
    secondary_dept: Optional[str] = Query(None),
    secondary_type: Optional[str] = Query(None),
):
    return data_service.search_courses(
        query=query,
        dept_filter=dept,
        type_filter=course_type,
        primary_dept=primary_dept,
        secondary_dept=secondary_dept,
        secondary_type=secondary_type
    )

@router.get("/departments")
def get_departments():
    return data_service.get_departments()

@router.get("/classrooms")
def get_classrooms():
    return data_service.get_classrooms()

@router.get("/{code}")
def get_course_detail(
    code: str,
    primary_dept: Optional[str] = Query(None),
    secondary_dept: Optional[str] = Query(None),
    secondary_type: Optional[str] = Query(None),
):
    detail = data_service.get_course_detail(
        code,
        primary_dept=primary_dept,
        secondary_dept=secondary_dept,
        secondary_type=secondary_type
    )
    if not detail:
        raise HTTPException(status_code=404, detail="Ders bulunamadı")
    return detail
