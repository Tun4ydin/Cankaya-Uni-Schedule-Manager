import os
import tempfile
from transcript_parser import TranscriptParser
from prerequisite_manager import PrerequisiteManager
from services.data_service import data_service

class TranscriptService:
    def __init__(self):
        PrerequisiteManager.reload_official_prerequisites()

    def parse_transcript_text(self, text: str):
        result = TranscriptParser.parse_text(text)
        # Calculate progress with the parsed courses
        curriculum_progress = data_service.dm.get_curriculum_progress(
            primary_dept=result.get("primary_dept") or data_service.get_profile().get("primary_dept", "CENG"),
            passed_courses=result.get("passed_courses", {})
        )
        result["curriculum_progress"] = curriculum_progress
        return result

    def parse_transcript_file(self, file_bytes: bytes, filename: str):
        ext = os.path.splitext(filename)[1].lower()
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            result = TranscriptParser.parse_file(tmp_path)
            curriculum_progress = data_service.dm.get_curriculum_progress(
                primary_dept=result.get("primary_dept") or data_service.get_profile().get("primary_dept", "CENG"),
                passed_courses=result.get("passed_courses", {})
            )
            result["curriculum_progress"] = curriculum_progress
            return result
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def check_prerequisites(self, course_code: str, passed_courses: dict = None):
        if passed_courses is None:
            passed_courses = data_service.get_profile().get("passed_courses", {})
        return PrerequisiteManager.check_prerequisites(course_code, passed_courses)

transcript_service = TranscriptService()
