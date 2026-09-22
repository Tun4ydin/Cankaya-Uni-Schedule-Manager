import os
import json
from config import COURSES_CACHE_FILE, STUDENT_PROFILE_FILE, ROOT_DIR
from data_manager import DataManager, Course, Section, ScheduleSlot

class DataService:
    def __init__(self):
        self.dm = DataManager(cache_filepath=COURSES_CACHE_FILE)
        self.dm.PROFILE_CACHE_FILE = STUDENT_PROFILE_FILE
        self.dm.load_student_profile()

    def get_departments(self):
        depts = []
        for code, name in sorted(self.dm.DEPARTMENT_NAMES.items()):
            depts.append({"code": code, "name": name})
        return depts

    def search_courses(self, query="", dept_filter=None, type_filter=None, primary_dept=None, secondary_dept=None, secondary_type=None):
        self.dm.load_student_profile()
        results = self.dm.search_courses(
            query=query,
            dept_filter=dept_filter,
            type_filter=type_filter,
            primary_dept=primary_dept,
            secondary_dept=secondary_dept,
            secondary_type=secondary_type
        )
        
        from prerequisite_manager import PrerequisiteManager
        passed_courses = self.dm.get_passed_courses()
        normalized_passed = {self.dm.normalize_code(k): v for k, v in passed_courses.items()}

        output = []
        for course, course_type, type_label in results:
            cr, ec = self.dm.get_course_credits(course.code)
            sections_data = []
            for sec_no, sec in sorted(course.sections.items(), key=lambda s: str(s[0])):
                sections_data.append({
                    "section_no": sec.section_no,
                    "instructor": sec.instructor,
                    "classroom": sec.classroom or "",
                    "slots": [
                        {
                            **s.to_dict(),
                            "classroom": s.classroom or sec.classroom or ""
                        } for s in sec.slots
                    ]
                })

            norm_code = self.dm.normalize_code(course.code)
            passed_entry = normalized_passed.get(norm_code)
            is_passed = passed_entry is not None
            grade = ""
            if is_passed:
                grade = passed_entry.get("grade", "") if isinstance(passed_entry, dict) else str(passed_entry)

            prereq_eval = PrerequisiteManager.check_prerequisites(norm_code, normalized_passed)
            missing_formatted = []
            for m in prereq_eval.get("missing_prereqs", []):
                if isinstance(m, (tuple, list, set)):
                    missing_formatted.append("(" + " veya ".join(m) + ")")
                else:
                    missing_formatted.append(str(m))

            prerequisites_data = {
                "can_take": prereq_eval.get("can_take", True),
                "has_prereqs": prereq_eval.get("has_prereqs", False),
                "rule_description": prereq_eval.get("rule_description", "Ön koşulsuz"),
                "satisfied_prereqs": prereq_eval.get("satisfied_prereqs", []),
                "missing_prereqs": missing_formatted,
                "message": prereq_eval.get("message", "")
            }

            output.append({
                "code": course.code,
                "dept_code": course.dept_code,
                "course_type": course_type,
                "type_label": type_label,
                "credit": cr,
                "ects": ec,
                "sections_count": len(course.sections),
                "sections": sections_data,
                "passed_info": {
                    "is_passed": is_passed,
                    "grade": grade
                },
                "prerequisites": prerequisites_data
            })
        return output

    def get_course_detail(self, code: str, primary_dept=None, secondary_dept=None, secondary_type=None):
        self.dm.load_student_profile()
        norm_code = self.dm.normalize_code(code)
        course = self.dm.courses.get(norm_code)
        
        info = self.dm.get_course_info(norm_code)
        course_type, type_label = self.dm.classify_course(
            norm_code,
            primary_dept=primary_dept,
            secondary_dept=secondary_dept,
            secondary_type=secondary_type
        )
        prereq_info = self.dm.check_course_prerequisites(norm_code)
        missing_formatted = []
        for m in prereq_info.get("missing_prereqs", []):
            if isinstance(m, (tuple, list, set)):
                missing_formatted.append("(" + " veya ".join(m) + ")")
            else:
                missing_formatted.append(str(m))
        prereq_info["missing_prereqs"] = missing_formatted

        cr, ec = self.dm.get_course_credits(norm_code)

        # Check passed status
        passed_dict = self.dm.get_passed_courses()
        passed_entry = None
        for p_code, p_info in passed_dict.items():
            if self.dm.normalize_code(p_code) == norm_code:
                passed_entry = p_info
                break

        passed_info = {
            "is_passed": passed_entry is not None,
            "grade": passed_entry.get("grade", "") if isinstance(passed_entry, dict) else (str(passed_entry) if passed_entry else "")
        }

        sections_data = []
        if course:
            for sec_no, sec in sorted(course.sections.items(), key=lambda s: str(s[0])):
                sections_data.append({
                    "section_no": sec.section_no,
                    "instructor": sec.instructor,
                    "classroom": sec.classroom or "",
                    "slots": [
                        {
                            **s.to_dict(),
                            "classroom": s.classroom or sec.classroom or ""
                        } for s in sec.slots
                    ]
                })

        return {
            "code": norm_code,
            "name": info.get("name", norm_code),
            "dept_code": info.get("dept_code", Course.extract_dept_code(norm_code)),
            "dept_name": info.get("dept_name", ""),
            "level": info.get("level", 1),
            "credit": cr,
            "ects": ec,
            "description": info.get("description", ""),
            "course_type": course_type,
            "type_label": type_label,
            "course_url": info.get("course_url", ""),
            "dept_url": info.get("dept_url", ""),
            "ebs_url": info.get("ebs_url", ""),
            "search_url": info.get("search_url", ""),
            "passed_info": passed_info,
            "prerequisites": prereq_info,
            "sections": sections_data
        }

    def get_profile(self):
        self.dm.load_student_profile()
        return self.dm.student_profile

    def update_profile(self, data: dict):
        self.dm.load_student_profile()
        if "primary_dept" in data:
            self.dm.student_profile["primary_dept"] = data["primary_dept"]
        if "secondary_dept" in data:
            self.dm.student_profile["secondary_dept"] = data["secondary_dept"]
        if "secondary_type" in data:
            self.dm.student_profile["secondary_type"] = data["secondary_type"]
        if "theme" in data:
            self.dm.student_profile["theme"] = data["theme"]
        
        self.dm.save_student_profile()
        return self.dm.student_profile

    def set_custom_block(self, day, time_slot, title, note="", color="amber"):
        self.dm.set_custom_schedule_block(day, time_slot, title, note, color)
        return self.dm.get_custom_schedule_blocks()

    def delete_custom_block(self, day, time_slot):
        self.dm.delete_custom_schedule_block(day, time_slot)
        return self.dm.get_custom_schedule_blocks()

    def set_passed_course(self, code, grade="CC", name=""):
        self.dm.add_passed_course(code, grade, name)
        return self.dm.get_passed_courses()

    def remove_passed_course(self, code):
        self.dm.remove_passed_course(code)
        return self.dm.get_passed_courses()

    def set_all_passed_courses(self, passed_dict: dict):
        self.dm.set_passed_courses(passed_dict)
        return self.dm.get_passed_courses()

    def get_classrooms(self):
        res = {}
        for code, course in self.dm.courses.items():
            norm_code = self.dm.normalize_code(code)
            c_dict = {}
            for sec_no, sec in course.sections.items():
                s_dict = {
                    "classroom": sec.classroom or "",
                    "slots": {}
                }
                for slot in sec.slots:
                    s_dict["slots"][f"{slot.day}:{slot.time_slot}"] = slot.classroom or sec.classroom or ""
                c_dict[str(sec_no)] = s_dict
            res[norm_code] = c_dict
        return res

# Global service instance
data_service = DataService()
