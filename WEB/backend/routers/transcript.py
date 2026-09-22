from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.transcript_service import transcript_service
from services.data_service import data_service

router = APIRouter(prefix="/api/transcript", tags=["transcript"])

class TranscriptTextRequest(BaseModel):
    text: str

class ApplyTranscriptRequest(BaseModel):
    primary_dept: Optional[str] = None
    secondary_dept: Optional[str] = None
    secondary_type: Optional[str] = None
    passed_courses: Dict[str, Any]

@router.post("/parse-text")
def parse_text(req: TranscriptTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Transkript metni boş olamaz")
    return transcript_service.parse_transcript_text(req.text)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Dosya içeriği boş")
    return transcript_service.parse_transcript_file(content, file.filename or "transcript.pdf")

@router.post("/apply")
def apply_transcript(req: ApplyTranscriptRequest):
    # Update profile with detected departments and passed courses
    update_data = {}
    if req.primary_dept:
        update_data["primary_dept"] = req.primary_dept
    if req.secondary_dept:
        update_data["secondary_dept"] = req.secondary_dept
    if req.secondary_type:
        update_data["secondary_type"] = req.secondary_type
    
    if update_data:
        data_service.update_profile(update_data)
    
    if req.passed_courses:
        data_service.set_all_passed_courses(req.passed_courses)

    return {
        "status": "success",
        "profile": data_service.get_profile(),
        "curriculum_progress": data_service.get_curriculum_progress(req.primary_dept)
    }
