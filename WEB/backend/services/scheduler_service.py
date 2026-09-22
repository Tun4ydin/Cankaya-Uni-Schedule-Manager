from scheduler_engine import SchedulerEngine
from services.data_service import data_service

class SchedulerService:
    def __init__(self):
        self.engine = SchedulerEngine()

    def generate_schedule_combinations(self, selected_courses, locked_sections=None, allowed_instructors=None, preferences=None, custom_blocks=None):
        """
        selected_courses: list of course codes e.g. ["CENG111", "MATH157"]
        locked_sections: dict e.g. {"CENG111": "1"} (if user wants a specific section)
        allowed_instructors: dict e.g. {"CENG111": ["Prof. Dr. ..."]}
        preferences: dict e.g. {"free_friday": True, "no_morning": False, "free_monday": False}
        custom_blocks: dict of custom blocks e.g. { "Pazartesi:12:00 - 12:50": {...} }
        """
        if locked_sections is None:
            locked_sections = {}
        if allowed_instructors is None:
            allowed_instructors = {}
        if preferences is None:
            preferences = {}
        if custom_blocks is None:
            custom_blocks = data_service.get_profile().get("custom_schedule_blocks", {})

        # Build course_sections_dict
        course_sections_dict = {}
        for code in selected_courses:
            norm_code = data_service.dm.normalize_code(code)
            course = data_service.dm.courses.get(norm_code)
            if not course:
                continue

            candidate_sections = list(course.sections.values())

            # Filter by allowed instructors if specified for this course
            allowed_inst = allowed_instructors.get(norm_code) or allowed_instructors.get(code)
            if allowed_inst is not None:
                candidate_sections = [s for s in candidate_sections if s.instructor in allowed_inst]

            # If user locked a section for this course, only include that section if it's among candidate_sections
            if norm_code in locked_sections and locked_sections[norm_code] != "auto":
                target_sec_no = str(locked_sections[norm_code])
                sec = course.sections.get(target_sec_no)
                if sec and sec in candidate_sections:
                    course_sections_dict[norm_code] = [sec]
                else:
                    course_sections_dict[norm_code] = candidate_sections
            else:
                course_sections_dict[norm_code] = candidate_sections

        raw_combinations = self.engine.generate_combinations(
            course_sections_dict,
            preferences=preferences,
            custom_blocks=custom_blocks
        )

        # Format combinations for frontend consumption
        formatted_combinations = []
        for combo in raw_combinations:
            combo_sections = []
            total_credits = 0
            total_ects = 0
            total_hours = 0
            days_used = set()

            for sec in combo:
                cr, ec = data_service.dm.get_course_credits(sec.course_code)
                total_credits += cr
                total_ects += ec
                total_hours += len(sec.slots)

                for s in sec.slots:
                    days_used.add(s.day)

                combo_sections.append({
                    "course_code": sec.course_code,
                    "section_no": sec.section_no,
                    "instructor": sec.instructor,
                    "classroom": sec.classroom or "",
                    "credit": cr,
                    "ects": ec,
                    "slots": [
                        {
                            **s.to_dict(),
                            "classroom": s.classroom or sec.classroom or ""
                        } for s in sec.slots
                    ]
                })

            formatted_combinations.append({
                "sections": combo_sections,
                "total_credits": total_credits,
                "total_ects": total_ects,
                "total_hours": total_hours,
                "days_count": len(days_used),
                "days_used": sorted(list(days_used))
            })

        return {
            "total_combinations": len(formatted_combinations),
            "combinations": formatted_combinations
        }

    def check_conflicts(self, sections_data, custom_blocks=None):
        """
        sections_data: list of dicts with course_code and section_no, or list of Section objects.
        """
        if custom_blocks is None:
            custom_blocks = data_service.get_profile().get("custom_schedule_blocks", {})

        actual_sections = []
        for item in sections_data:
            c_code = data_service.dm.normalize_code(item["course_code"])
            s_no = str(item["section_no"])
            course = data_service.dm.courses.get(c_code)
            if course and s_no in course.sections:
                actual_sections.append(course.sections[s_no])

        conflicts = self.engine.find_all_conflicts(actual_sections, custom_blocks=custom_blocks)
        
        # Serialize conflicts dict key (day, time_slot)
        output = []
        for (day, time_slot), detail in conflicts.items():
            output.append({
                "day": day,
                "time_slot": time_slot,
                "sections": [sec.to_dict() for sec in detail["sections"]],
                "custom_block": detail["custom_block"]
            })
        return output

# Global scheduler service
scheduler_service = SchedulerService()
