import os
import sys

# Base directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.dirname(BACKEND_DIR)
ROOT_DIR = os.path.dirname(WEB_DIR)

# Ensure ROOT_DIR is in sys.path so we can import scheduler_engine, data_manager, prerequisite_manager, transcript_parser
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Data file paths
COURSES_CACHE_FILE = os.path.join(ROOT_DIR, "cankaya_courses.json")
COURSE_DETAILS_FILE = os.path.join(ROOT_DIR, "cankaya_course_details.json")
CURRICULA_FILE = os.path.join(ROOT_DIR, "cankaya_official_curricula.json")
PREREQUISITES_FILE = os.path.join(ROOT_DIR, "cankaya_official_prerequisites.json")
STUDENT_PROFILE_FILE = os.path.join(ROOT_DIR, "student_profile.json")
