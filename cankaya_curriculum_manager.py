"""
Çankaya Üniversitesi Müfredat Yöneticisi

Çankaya Üniversitesi Bilgi Paketi sisteminden bölüm
müfredatlarını çeker, parse eder, cache'ler ve manuel
ön koşul kurallarını yönetir.

CurriculumWidget ve MainWindow ile uyumludur.

Gereken paketler:
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import json
import os
import re

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional
from urllib.request import Request, urlopen


try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# ============================================================
# CONSTANTS
# ============================================================

BILGI_PAKETI_BASE_URL = (
    "https://bilgipaketi.cankaya.edu.tr/"
    "program-detay"
)

DEFAULT_CACHE_DIR = "curriculum_cache"

DEFAULT_MANUAL_RULES_FILE = (
    "curriculum_manual_rules.json"
)


# ============================================================
# DEPARTMENT CONFIGURATION
# ============================================================

DEPARTMENT_CONFIGS = {
    "CENG": {
        "name": "Bilgisayar Mühendisliği",
        "program_id": "157371",
        "english_name": "Computer Engineering",
        "parser": "bilgi_paketi",
    },

    "CS": {
        "name": "Bilgisayar Bilimleri",
        "program_id": "469410",
        "english_name": "Computer Sciences",
        "parser": "bilgi_paketi",
    },

    "LAW": {
        "name": "Hukuk",
        "program_id": "157347",
        "english_name": "Law",
        "parser": "bilgi_paketi",
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_course_code(code: str) -> str:
    """
    Ders kodunu standart hale getirir.

    Örnek:

        CENG 111  -> CENG111
        CENG-111  -> CENG111
        ceng111   -> CENG111
    """

    if not code:
        return ""

    code = code.replace("\xa0", " ")
    code = code.upper()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        code
    )


def clean_text(value: str) -> str:
    """
    HTML/metin içindeki gereksiz boşlukları temizler.
    """

    if value is None:
        return ""

    value = value.replace(
        "\xa0",
        " "
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def parse_float(value: str) -> Optional[float]:
    """
    Metinden ilk sayısal değeri çıkarır.

    Türkçe ondalık virgülü destekler.
    """

    if value is None:
        return None

    value = clean_text(value)

    if not value:
        return None

    value = value.replace(
        ",",
        "."
    )

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        value
    )

    if not match:
        return None

    try:
        return float(
            match.group(0)
        )
    except ValueError:
        return None


def extract_course_codes(text: str) -> List[str]:
    """
    Metin içerisindeki ders kodlarını bulur.

    Örnekler:

        CENG 111
        CENG-111
        CENG111
        MATH 158
    """

    if not text:
        return []

    text = text.replace(
        "\xa0",
        " "
    )

    pattern = (
        r"\b"
        r"([A-ZÇĞİÖŞÜ]{2,8})"
        r"[\s\-]?"
        r"(\d{3})"
        r"\b"
    )

    result = []

    for match in re.finditer(
        pattern,
        text.upper()
    ):

        code = normalize_course_code(
            f"{match.group(1)} {match.group(2)}"
        )

        if (
            code
            and code not in result
        ):
            result.append(code)

    return result


def extract_first_course_code(text: str) -> str:
    codes = extract_course_codes(text)

    if codes:
        return codes[0]

    return ""


def remove_course_codes(text: str) -> str:
    """
    Metinden ders kodlarını çıkarır.
    """

    if not text:
        return ""

    result = re.sub(
        r"\b[A-ZÇĞİÖŞÜ]{2,8}"
        r"[\s\-]?\d{3}\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    return clean_text(result)


def detect_course_type(text: str) -> str:
    """
    Dersin zorunlu/seçmeli türünü tespit eder.
    """

    text = clean_text(
        text
    ).lower()

    if (
        "serbest seçmeli" in text
        or "free elective" in text
    ):
        return "Serbest Seçmeli"

    if (
        "bölüm dışı seçmeli" in text
        or "non-departmental elective" in text
    ):
        return "Bölüm Dışı Seçmeli"

    if (
        "zorunlu" in text
        or "mecburi" in text
        or "compulsory" in text
        or "mandatory" in text
    ):
        return "Zorunlu"

    if (
        "seçmeli" in text
        or "elective" in text
    ):
        return "Seçmeli"

    return ""


def detect_semester(text: str) -> Optional[int]:
    """
    Metinden dönem numarasını çıkarır.

    1-8 arası dönemleri destekler.
    """

    text = clean_text(
        text
    ).lower()

    mappings = {
        "birinci dönem": 1,
        "ikinci dönem": 2,
        "üçüncü dönem": 3,
        "dördüncü dönem": 4,
        "beşinci dönem": 5,
        "altıncı dönem": 6,
        "yedinci dönem": 7,
        "sekizinci dönem": 8,

        "1. dönem": 1,
        "2. dönem": 2,
        "3. dönem": 3,
        "4. dönem": 4,
        "5. dönem": 5,
        "6. dönem": 6,
        "7. dönem": 7,
        "8. dönem": 8,

        "1. yarıyıl": 1,
        "2. yarıyıl": 2,
        "3. yarıyıl": 3,
        "4. yarıyıl": 4,
        "5. yarıyıl": 5,
        "6. yarıyıl": 6,
        "7. yarıyıl": 7,
        "8. yarıyıl": 8,

        "1st semester": 1,
        "2nd semester": 2,
        "3rd semester": 3,
        "4th semester": 4,
        "5th semester": 5,
        "6th semester": 6,
        "7th semester": 7,
        "8th semester": 8,

        "fall semester": 1,
        "spring semester": 2,
    }

    for key, semester in mappings.items():

        if key in text:
            return semester

    # --------------------------------------------------------
    # Türkçe:
    # 1. yıl 1. dönem
    # --------------------------------------------------------

    match = re.search(
        r"([1-4])\s*\.\s*yıl\s*"
        r"([12])\s*\.\s*dönem",
        text
    )

    if match:

        year = int(
            match.group(1)
        )

        period = int(
            match.group(2)
        )

        return (
            (year - 1) * 2
        ) + period

    # --------------------------------------------------------
    # Türkçe:
    # 1. yıl ... 1. dönem
    # --------------------------------------------------------

    match = re.search(
        r"([1-4])\s*\.\s*yıl.*?"
        r"([12])\s*\.\s*dönem",
        text
    )

    if match:

        year = int(
            match.group(1)
        )

        period = int(
            match.group(2)
        )

        return (
            (year - 1) * 2
        ) + period

    # --------------------------------------------------------
    # English:
    # 1st year ... 1st semester
    # --------------------------------------------------------

    match = re.search(
        r"([1-4])(?:st|nd|rd|th)"
        r"\s+year.*?"
        r"([12])(?:st|nd)"
        r"\s+semester",
        text
    )

    if match:

        year = int(
            match.group(1)
        )

        period = int(
            match.group(2)
        )

        return (
            (year - 1) * 2
        ) + period

    return None


def semester_to_year(
    semester: Optional[int]
) -> Optional[int]:

    if semester is None:
        return None

    return (
        (semester - 1) // 2
    ) + 1


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class CurriculumCourse:

    code: str
    name: str

    department: str = ""

    semester: Optional[int] = None
    year: Optional[int] = None

    course_type: str = ""

    credits: Optional[float] = None
    ects: Optional[float] = None

    prerequisite_text: str = ""

    prerequisites: List[str] = field(
        default_factory=list
    )

    equivalent_courses: List[str] = field(
        default_factory=list
    )

    source_url: str = ""

    manual_prerequisites: List[str] = field(
        default_factory=list
    )

    manual_note: str = ""

    def get_all_prerequisites(self) -> List[str]:
        """
        Resmi + manuel ön koşulları birleştirir.
        """

        result = []

        combined = (
            self.prerequisites
            + self.manual_prerequisites
        )

        for code in combined:

            normalized = normalize_course_code(
                code
            )

            if (
                normalized
                and normalized not in result
            ):
                result.append(
                    normalized
                )

        return result

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):

        return cls(
            code=data.get(
                "code",
                ""
            ),

            name=data.get(
                "name",
                ""
            ),

            department=data.get(
                "department",
                ""
            ),

            semester=data.get(
                "semester"
            ),

            year=data.get(
                "year"
            ),

            course_type=data.get(
                "course_type",
                ""
            ),

            credits=data.get(
                "credits"
            ),

            ects=data.get(
                "ects"
            ),

            prerequisite_text=data.get(
                "prerequisite_text",
                ""
            ),

            prerequisites=data.get(
                "prerequisites",
                []
            ),

            equivalent_courses=data.get(
                "equivalent_courses",
                []
            ),

            source_url=data.get(
                "source_url",
                ""
            ),

            manual_prerequisites=data.get(
                "manual_prerequisites",
                []
            ),

            manual_note=data.get(
                "manual_note",
                ""
            ),
        )


@dataclass
class Curriculum:

    department_code: str
    department_name: str
    source_url: str

    courses: List[CurriculumCourse] = field(
        default_factory=list
    )

    fetched_at: str = ""

    def get_course(
        self,
        code: str
    ) -> Optional[CurriculumCourse]:

        normalized = normalize_course_code(
            code
        )

        for course in self.courses:

            if (
                normalize_course_code(
                    course.code
                )
                == normalized
            ):
                return course

        return None

    def get_courses_by_semester(
        self,
        semester: int
    ) -> List[CurriculumCourse]:

        return [
            course
            for course in self.courses
            if course.semester == semester
        ]

    def to_dict(self):

        return {
            "department_code":
                self.department_code,

            "department_name":
                self.department_name,

            "source_url":
                self.source_url,

            "fetched_at":
                self.fetched_at,

            "courses": [
                course.to_dict()
                for course in self.courses
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data
    ):

        return cls(
            department_code=data.get(
                "department_code",
                ""
            ),

            department_name=data.get(
                "department_name",
                ""
            ),

            source_url=data.get(
                "source_url",
                ""
            ),

            fetched_at=data.get(
                "fetched_at",
                ""
            ),

            courses=[
                CurriculumCourse.from_dict(
                    course
                )

                for course in data.get(
                    "courses",
                    []
                )
            ],
        )


# ============================================================
# HTTP CLIENT
# ============================================================

class CurriculumHttpClient:

    USER_AGENT = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140 Safari/537.36"
    )

    @classmethod
    def get(
        cls,
        url: str,
        timeout: int = 30
    ) -> str:

        # ----------------------------------------------------
        # requests
        # ----------------------------------------------------

        try:

            import requests

            response = requests.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent":
                        cls.USER_AGENT,

                    "Accept":
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,*/*;q=0.8",

                    "Accept-Language":
                        "tr-TR,tr;q=0.9,en;q=0.8",

                    "Cache-Control":
                        "no-cache",
                }
            )

            response.raise_for_status()

            if not response.encoding:

                response.encoding = (
                    response.apparent_encoding
                    or "utf-8"
                )

            return response.text

        except ImportError:

            # ------------------------------------------------
            # urllib fallback
            # ------------------------------------------------

            request = Request(
                url,
                headers={
                    "User-Agent":
                        cls.USER_AGENT,

                    "Accept-Language":
                        "tr-TR,tr;q=0.9,en;q=0.8",
                }
            )

            with urlopen(
                request,
                timeout=timeout
            ) as response:

                raw = response.read()

                try:

                    return raw.decode(
                        "utf-8"
                    )

                except UnicodeDecodeError:

                    encoding = (
                        response.headers
                        .get_content_charset()
                        or "latin-1"
                    )

                    return raw.decode(
                        encoding,
                        errors="replace"
                    )


# ============================================================
# BILGI PAKETI PARSER
# ============================================================

class BilgiPaketiCurriculumParser:
    """
    Çankaya Üniversitesi Bilgi Paketi HTML parser'ı.
    """

    def __init__(
        self,
        department_code: str,
        department_name: str,
        source_url: str
    ):

        self.department_code = (
            department_code
        )

        self.department_name = (
            department_name
        )

        self.source_url = (
            source_url
        )

    def parse(
        self,
        html: str
    ) -> Curriculum:

        if BeautifulSoup is None:

            raise RuntimeError(
                "beautifulsoup4 kurulu değil.\n\n"
                "Kurulum:\n"
                "pip install beautifulsoup4"
            )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        curriculum = Curriculum(
            department_code=
                self.department_code,

            department_name=
                self.department_name,

            source_url=
                self.source_url,
        )

        tables = soup.find_all(
            "table"
        )

        for table in tables:

            self._parse_table(
                table,
                curriculum
            )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not curriculum.courses:

            self._parse_text_blocks(
                soup,
                curriculum
            )

        curriculum.courses = (
            self._deduplicate_courses(
                curriculum.courses
            )
        )

        return curriculum

    # ========================================================
    # TABLE
    # ========================================================

    def _parse_table(
        self,
        table,
        curriculum
    ):

        rows = table.find_all(
            "tr"
        )

        if not rows:
            return

        headers = self._detect_headers(
            rows
        )

        current_semester = None
        current_year = None

        for row in rows:

            cells = row.find_all(
                ["td", "th"]
            )

            if not cells:
                continue

            row_text = clean_text(
                row.get_text(
                    " ",
                    strip=True
                )
            )

            semester = detect_semester(
                row_text
            )

            if semester is not None:

                current_semester = semester

                current_year = (
                    semester_to_year(
                        semester
                    )
                )

            course = self._parse_row(
                row,
                headers,
                current_semester,
                current_year
            )

            if course:

                curriculum.courses.append(
                    course
                )

    # ========================================================
    # HEADER
    # ========================================================

    def _detect_headers(
        self,
        rows
    ) -> List[str]:

        best_headers = []
        best_score = 0

        for row in rows[:10]:

            ths = row.find_all(
                "th"
            )

            cells = (
                ths
                if ths
                else row.find_all(
                    ["td", "th"]
                )
            )

            if not cells:
                continue

            current = [
                clean_text(
                    cell.get_text(
                        " ",
                        strip=True
                    )
                ).lower()

                for cell in cells
            ]

            score = 0

            for value in current:

                if any(
                    word in value
                    for word in (
                        "ders kod",
                        "course code",
                        "kod",
                        "code",
                    )
                ):
                    score += 3

                if any(
                    word in value
                    for word in (
                        "ders adı",
                        "ders adi",
                        "course name",
                    )
                ):
                    score += 3

                if any(
                    word in value
                    for word in (
                        "tür",
                        "tur",
                        "type",
                    )
                ):
                    score += 1

                if any(
                    word in value
                    for word in (
                        "kredi",
                        "credit",
                    )
                ):
                    score += 1

                if any(
                    word in value
                    for word in (
                        "akts",
                        "ects",
                    )
                ):
                    score += 1

                if any(
                    word in value
                    for word in (
                        "ön koşul",
                        "önkoşul",
                        "prerequisite",
                    )
                ):
                    score += 2

            if score > best_score:

                best_score = score
                best_headers = current

        return best_headers

    # ========================================================
    # ROW
    # ========================================================

    def _parse_row(
        self,
        row,
        headers,
        semester,
        year
    ) -> Optional[CurriculumCourse]:

        cells = row.find_all(
            ["td", "th"]
        )

        if not cells:
            return None

        values = [
            clean_text(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

            for cell in cells
        ]

        row_text = clean_text(
            " ".join(values)
        )

        if not row_text:
            return None

        row_lower = row_text.lower()

        # ----------------------------------------------------
        # TOPLAM SATIRLARI
        # ----------------------------------------------------

        if (
            row_lower.startswith("toplam")
            or row_lower.startswith("total")
            or "toplam kredi" in row_lower
            or "total credit" in row_lower
        ):
            return None

        # ----------------------------------------------------
        # COURSE CODE
        # ----------------------------------------------------

        course_code = ""

        for cell in cells:

            # Önce linkler
            for link in cell.find_all("a"):

                code = extract_first_course_code(
                    link.get_text(
                        " ",
                        strip=True
                    )
                )

                if code:

                    course_code = code
                    break

            if course_code:
                break

            # Sonra hücrenin tamamı
            code = extract_first_course_code(
                cell.get_text(
                    " ",
                    strip=True
                )
            )

            if code:

                course_code = code
                break

        if not course_code:
            return None

        # ----------------------------------------------------
        # COURSE NAME
        # ----------------------------------------------------

        course_name = ""

        if headers:

            name_index = self._find_header_index(
                headers,
                (
                    "ders adı",
                    "ders adi",
                    "course name",
                )
            )

            if (
                name_index is not None
                and name_index < len(values)
            ):

                candidate = values[
                    name_index
                ]

                if (
                    candidate
                    and not self._looks_like_code(
                        candidate
                    )
                ):
                    course_name = candidate

        # ----------------------------------------------------
        # HEADER YOKSA
        # ----------------------------------------------------

        if not course_name:

            for value in values:

                candidate = clean_text(
                    value
                )

                if not candidate:
                    continue

                if extract_course_codes(
                    candidate
                ):
                    continue

                if self._is_course_type_text(
                    candidate.lower()
                ):
                    continue

                if parse_float(
                    candidate
                ) is not None:
                    continue

                candidate_lower = (
                    candidate.lower()
                )

                if (
                    "ön koşul" in candidate_lower
                    or "önkoşul" in candidate_lower
                    or "prerequisite" in candidate_lower
                ):
                    continue

                if len(candidate) < 2:
                    continue

                course_name = candidate
                break

        course_name = remove_course_codes(
            course_name
        )

        if not course_name:
            return None

        # ----------------------------------------------------
        # COURSE TYPE
        # ----------------------------------------------------

        course_type = ""

        if headers:

            type_index = self._find_header_index(
                headers,
                (
                    "tür",
                    "tur",
                    "type",
                    "ders türü",
                    "course type",
                    "status",
                )
            )

            if (
                type_index is not None
                and type_index < len(values)
            ):

                course_type = detect_course_type(
                    values[type_index]
                )

        if not course_type:

            course_type = detect_course_type(
                row_text
            )

        # ----------------------------------------------------
        # PREREQUISITES
        # ----------------------------------------------------

        prerequisite_text = ""

        if headers:

            prerequisite_index = (
                self._find_header_index(
                    headers,
                    (
                        "ön koşul",
                        "önkoşul",
                        "ön şart",
                        "önşart",
                        "prerequisite",
                    )
                )
            )

            if (
                prerequisite_index is not None
                and prerequisite_index < len(values)
            ):

                prerequisite_text = values[
                    prerequisite_index
                ]

        if not prerequisite_text:

            match = re.search(
                r"(?:ön\s*koşul|"
                r"ön\s*şart|"
                r"prerequisite)"
                r"\s*[:\-]?\s*(.*)",
                row_text,
                flags=re.IGNORECASE
            )

            if match:

                prerequisite_text = clean_text(
                    match.group(1)
                )

        prerequisites = extract_course_codes(
            prerequisite_text
        )

        # ----------------------------------------------------
        # ECTS
        # ----------------------------------------------------

        ects = None

        if headers:

            ects_index = self._find_header_index(
                headers,
                (
                    "akts",
                    "ects",
                    "european credit",
                )
            )

            if (
                ects_index is not None
                and ects_index < len(values)
            ):

                ects = parse_float(
                    values[ects_index]
                )

        # ----------------------------------------------------
        # CREDITS
        # ----------------------------------------------------

        credits = None

        if headers:

            credit_index = (
                self._find_credit_header_index(
                    headers
                )
            )

            if (
                credit_index is not None
                and credit_index < len(values)
            ):

                credits = parse_float(
                    values[credit_index]
                )

        # ----------------------------------------------------
        # NUMERIC FALLBACK
        # ----------------------------------------------------

        numeric_values = []

        for value in values:

            number = parse_float(
                value
            )

            if number is not None:
                numeric_values.append(
                    number
                )

        # ----------------------------------------------------
        # NUMERIC FALLBACK
        # ----------------------------------------------------

        # Eğer kredi / AKTS başlıklarından değer bulunamadıysa
        # satırdaki sayısal değerleri kullan.
        #
        # Genellikle müfredat tablolarında:
        #
        #   ... | Kredi | AKTS
        #   ... | 3     | 5
        #
        # şeklinde bir yapı bulunur.
        #
        # İlk uygun sayıyı kredi,
        # ikinci uygun sayıyı AKTS olarak kabul ediyoruz.
        #
        # Ancak dönem bilgisi de sayısal olabileceği için
        # 1-8 arasındaki dönem değerlerini mümkün olduğunca
        # dışarıda bırakıyoruz.

        if credits is None or ects is None:

            fallback_numbers = []

            for value in values:

                value_clean = clean_text(
                    value
                )

                # Ders kodlarının içindeki sayıları
                # yanlışlıkla kredi olarak alma.
                if extract_course_codes(
                    value_clean
                ):
                    continue

                number = parse_float(
                    value_clean
                )

                if number is None:
                    continue

                fallback_numbers.append(
                    number
                )

            # ------------------------------------------------
            # CREDIT / ECTS TAHMİNİ
            # ------------------------------------------------

            if credits is None and fallback_numbers:

                # Çoğu Çankaya müfredatında kredi değeri
                # 0-10 aralığındadır.
                #
                # En makul ilk değeri seç.
                for number in fallback_numbers:

                    if 0 <= number <= 10:

                        credits = number
                        break

            if ects is None and fallback_numbers:

                # AKTS genellikle krediden büyük veya eşittir.
                # Önce kredi değerinden farklı bir sayı arıyoruz.
                for number in fallback_numbers:

                    if (
                        0 <= number <= 60
                        and (
                            credits is None
                            or number != credits
                        )
                    ):

                        ects = number
                        break

        # ----------------------------------------------------
        # SEMESTER
        # ----------------------------------------------------

        detected_semester = (
            semester
        )

        if detected_semester is None:

            detected_semester = detect_semester(
                row_text
            )

        detected_year = year

        if detected_year is None:

            detected_year = semester_to_year(
                detected_semester
            )

        # ----------------------------------------------------
        # EQUIVALENT COURSES
        # ----------------------------------------------------

        equivalent_courses = []

        equivalent_match = re.search(
            r"(?:eşdeğer|esdeger|"
            r"equivalent)"
            r"\s*[:\-]?\s*(.*)",
            row_text,
            flags=re.IGNORECASE
        )

        if equivalent_match:

            equivalent_text = clean_text(
                equivalent_match.group(1)
            )

            equivalent_courses = (
                extract_course_codes(
                    equivalent_text
                )
            )

        # ----------------------------------------------------
        # COURSE OBJECT
        # ----------------------------------------------------

        course = CurriculumCourse(
            code=normalize_course_code(
                course_code
            ),

            name=clean_text(
                course_name
            ),

            department=(
                self.department_code
            ),

            semester=detected_semester,

            year=detected_year,

            course_type=course_type,

            credits=credits,

            ects=ects,

            prerequisite_text=(
                prerequisite_text
            ),

            prerequisites=(
                prerequisites
            ),

            equivalent_courses=(
                equivalent_courses
            ),

            source_url=(
                self.source_url
            ),
        )

        return course

    # ========================================================
    # HEADER INDEX
    # ========================================================

    @staticmethod
    def _find_header_index(
        headers,
        candidates
    ):

        for index, header in enumerate(
            headers
        ):

            header_lower = clean_text(
                header
            ).lower()

            for candidate in candidates:

                if candidate in header_lower:
                    return index

        return None

    # ========================================================
    # CREDIT HEADER INDEX
    # ========================================================

    @staticmethod
    def _find_credit_header_index(
        headers
    ):

        for index, header in enumerate(
            headers
        ):

            header_lower = clean_text(
                header
            ).lower()

            # AKTS / ECTS kredi değildir.
            if (
                "akts" in header_lower
                or "ects" in header_lower
            ):
                continue

            if any(
                word in header_lower
                for word in (
                    "kredi",
                    "credit",
                    "credits",
                    "yerel kredi",
                    "local credit",
                )
            ):
                return index

        return None

    # ========================================================
    # COURSE CODE CHECK
    # ========================================================

    @staticmethod
    def _looks_like_code(
        value
    ):

        if not value:
            return False

        codes = extract_course_codes(
            value
        )

        normalized = normalize_course_code(
            value
        )

        return (
            len(codes) == 1
            and normalized == codes[0]
        )

    # ========================================================
    # COURSE TYPE CHECK
    # ========================================================

    @staticmethod
    def _is_course_type_text(
        value
    ):

        if not value:
            return False

        value = clean_text(
            value
        ).lower()

        type_keywords = (
            "zorunlu",
            "mecburi",
            "seçmeli",
            "seçmeli",
            "serbest seçmeli",
            "bölüm dışı seçmeli",
            "elective",
            "compulsory",
            "mandatory",
            "free elective",
            "non-departmental elective",
        )

        return any(
            keyword in value
            for keyword in type_keywords
        )

    # ========================================================
    # TEXT FALLBACK
    # ========================================================

    def _parse_text_blocks(
        self,
        soup,
        curriculum
    ):

        """
        Tablo yapısı kullanılamadığı durumlarda sayfadaki
        metin bloklarından dersleri bulmaya çalışır.

        Bu yöntem tablo parser'ına göre daha düşük güvenilirlikte
        bir fallback mekanizmasıdır.
        """

        current_semester = None
        current_year = None

        elements = soup.find_all(
            [
                "p",
                "li",
                "div",
                "span",
                "td",
            ]
        )

        for element in elements:

            text = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            semester = detect_semester(
                text
            )

            if semester is not None:

                current_semester = semester

                current_year = (
                    semester_to_year(
                        semester
                    )
                )

            codes = extract_course_codes(
                text
            )

            if not codes:
                continue

            course_code = codes[0]

            # ------------------------------------------------
            # Kod dışındaki metni ders adı olarak kullan.
            # ------------------------------------------------

            course_name = remove_course_codes(
                text
            )

            course_name = clean_text(
                course_name
            )

            if not course_name:
                continue

            # Çok kısa veya yalnızca teknik bilgi içeren
            # satırları ders olarak kabul etme.
            if len(course_name) < 2:
                continue

            course_type = detect_course_type(
                text
            )

            prerequisite_match = re.search(
                r"(?:ön\s*koşul|"
                r"ön\s*şart|"
                r"prerequisite)"
                r"\s*[:\-]?\s*(.*)",
                text,
                flags=re.IGNORECASE
            )

            prerequisite_text = ""

            if prerequisite_match:

                prerequisite_text = clean_text(
                    prerequisite_match.group(1)
                )

            prerequisites = extract_course_codes(
                prerequisite_text
            )

            # ------------------------------------------------
            # Aynı kod zaten varsa tekrar ekleme.
            # ------------------------------------------------

            existing = curriculum.get_course(
                course_code
            )

            if existing:

                # Eksik bilgileri mevcut kayda tamamla.

                if (
                    not existing.name
                    and course_name
                ):
                    existing.name = course_name

                if (
                    not existing.semester
                    and current_semester
                ):
                    existing.semester = (
                        current_semester
                    )

                if (
                    not existing.year
                    and current_year
                ):
                    existing.year = (
                        current_year
                    )

                for prerequisite in prerequisites:

                    if prerequisite not in (
                        existing.prerequisites
                    ):
                        existing.prerequisites.append(
                            prerequisite
                        )

                continue

            curriculum.courses.append(
                CurriculumCourse(
                    code=normalize_course_code(
                        course_code
                    ),

                    name=course_name,

                    department=(
                        self.department_code
                    ),

                    semester=current_semester,

                    year=current_year,

                    course_type=course_type,

                    prerequisite_text=(
                        prerequisite_text
                    ),

                    prerequisites=(
                        prerequisites
                    ),

                    source_url=(
                        self.source_url
                    ),
                )
            )

    # ========================================================
    # DEDUPLICATION
    # ========================================================

    @staticmethod
    def _deduplicate_courses(
        courses
    ):

        result = []
        seen = {}

        for course in courses:

            code = normalize_course_code(
                course.code
            )

            if not code:
                continue

            # İlk kayıt
            if code not in seen:

                course.code = code

                seen[code] = course
                result.append(course)

                continue

            # ------------------------------------------------
            # Aynı ders tekrar bulunduysa bilgileri birleştir.
            # ------------------------------------------------

            existing = seen[code]

            if (
                not existing.name
                and course.name
            ):
                existing.name = course.name

            if (
                existing.semester is None
                and course.semester is not None
            ):
                existing.semester = (
                    course.semester
                )

            if (
                existing.year is None
                and course.year is not None
            ):
                existing.year = (
                    course.year
                )

            if (
                not existing.course_type
                and course.course_type
            ):
                existing.course_type = (
                    course.course_type
                )

            if (
                existing.credits is None
                and course.credits is not None
            ):
                existing.credits = (
                    course.credits
                )

            if (
                existing.ects is None
                and course.ects is not None
            ):
                existing.ects = (
                    course.ects
                )

            if (
                not existing.prerequisite_text
                and course.prerequisite_text
            ):
                existing.prerequisite_text = (
                    course.prerequisite_text
                )

            # Ön koşulları birleştir.
            for prerequisite in (
                course.prerequisites
            ):

                normalized = normalize_course_code(
                    prerequisite
                )

                if (
                    normalized
                    and normalized
                    not in existing.prerequisites
                ):

                    existing.prerequisites.append(
                        normalized
                    )

            # Eşdeğer dersleri birleştir.
            for equivalent in (
                course.equivalent_courses
            ):

                normalized = normalize_course_code(
                    equivalent
                )

                if (
                    normalized
                    and normalized
                    not in existing.equivalent_courses
                ):

                    existing.equivalent_courses.append(
                        normalized
                    )

        return result


# ============================================================
# MANUAL RULE MANAGER
# ============================================================

class ManualPrerequisiteRules:

    def __init__(
        self,
        filepath=DEFAULT_MANUAL_RULES_FILE
    ):

        self.filepath = filepath

        self.rules = {}

        self.load()

    # ========================================================
    # LOAD
    # ========================================================

    def load(self):

        if not os.path.exists(
            self.filepath
        ):

            self.rules = {}
            return

        try:

            with open(
                self.filepath,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if isinstance(
                data,
                dict
            ):

                self.rules = data

            else:

                self.rules = {}

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):

            self.rules = {}

    # ========================================================
    # SAVE
    # ========================================================

    def save(self):

        directory = os.path.dirname(
            self.filepath
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )

        temporary_file = (
            self.filepath
            + ".tmp"
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.rules,
                file,
                ensure_ascii=False,
                indent=2
            )

        os.replace(
            temporary_file,
            self.filepath
        )

    # ========================================================
    # GET
    # ========================================================

    def get_prerequisites(
        self,
        course_code
    ):

        course_code = normalize_course_code(
            course_code
        )

        values = self.rules.get(
            course_code,
            []
        )

        if not isinstance(
            values,
            list
        ):
            return []

        result = []

        for value in values:

            normalized = normalize_course_code(
                value
            )

            if (
                normalized
                and normalized not in result
            ):
                result.append(
                    normalized
                )

        return result

    # ========================================================
    # ADD
    # ========================================================

    def add(
        self,
        course_code,
        prerequisite
    ):

        course_code = normalize_course_code(
            course_code
        )

        prerequisite = normalize_course_code(
            prerequisite
        )

        if (
            not course_code
            or not prerequisite
        ):
            return False

        if course_code == prerequisite:
            return False

        values = self.rules.setdefault(
            course_code,
            []
        )

        if prerequisite in values:
            return False

        values.append(
            prerequisite
        )

        self.save()

        return True

    # ========================================================
    # REMOVE
    # ========================================================

    def remove(
        self,
        course_code,
        prerequisite
    ):

        course_code = normalize_course_code(
            course_code
        )

        prerequisite = normalize_course_code(
            prerequisite
        )

        values = self.rules.get(
            course_code,
            []
        )

        if prerequisite not in values:
            return False

        values.remove(
            prerequisite
        )

        if not values:

            self.rules.pop(
                course_code,
                None
            )

        self.save()

        return True


# ============================================================
# CURRICULUM MANAGER
# ============================================================

class CankayaCurriculumManager:

    def __init__(
        self,
        cache_dir=DEFAULT_CACHE_DIR,
        manual_rules_file=DEFAULT_MANUAL_RULES_FILE
    ):

        self.cache_dir = cache_dir

        self.manual_rules = (
            ManualPrerequisiteRules(
                manual_rules_file
            )
        )

        self.curriculums = {}

        os.makedirs(
            self.cache_dir,
            exist_ok=True
        )

    # ========================================================
    # DEPARTMENTS
    # ========================================================

    def get_departments(self):

        return DEPARTMENT_CONFIGS.copy()

    # ========================================================
    # URL
    # ========================================================

    def build_url(
        self,
        department_code
    ):

        config = DEPARTMENT_CONFIGS.get(
            department_code
        )

        if not config:
            raise ValueError(
                f"Bilinmeyen bölüm: "
                f"{department_code}"
            )

        return (
            f"{BILGI_PAKETI_BASE_URL}"
            f"?programId={config['program_id']}"
        )

    # ========================================================
    # CACHE FILE
    # ========================================================

    def get_cache_file(
        self,
        department_code
    ):

        safe_code = re.sub(
            r"[^A-Za-z0-9_\-]",
            "_",
            department_code
        )

        return os.path.join(
            self.cache_dir,
            f"{safe_code}.json"
        )

    # ========================================================
    # FETCH
    # ========================================================

    def fetch_curriculum(
        self,
        department_code,
        use_cache=True
    ):

        department_code = (
            department_code.upper()
        )

        config = DEPARTMENT_CONFIGS.get(
            department_code
        )

        if not config:

            raise ValueError(
                f"Bilinmeyen bölüm: "
                f"{department_code}"
            )

        # ----------------------------------------------------
        # CACHE
        # ----------------------------------------------------

        cache_file = self.get_cache_file(
            department_code
        )

        if (
            use_cache
            and os.path.exists(
                cache_file
            )
        ):

            try:

                curriculum = (
                    self.load_cache(
                        department_code
                    )
                )

                self.apply_manual_rules(
                    curriculum
                )

                self.curriculums[
                    department_code
                ] = curriculum

                return curriculum

            except Exception:
                pass

        # ----------------------------------------------------
        # WEB
        # ----------------------------------------------------

        url = self.build_url(
            department_code
        )

        html = CurriculumHttpClient.get(
            url
        )

        parser = BilgiPaketiCurriculumParser(
            department_code,
            config["name"],
            url
        )

        curriculum = parser.parse(
            html
        )

        curriculum.fetched_at = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        self.apply_manual_rules(
            curriculum
        )

        self.save_cache(
            curriculum
        )

        self.curriculums[
            department_code
        ] = curriculum

        return curriculum

    # ========================================================
    # CACHE SAVE
    # ========================================================

    def save_cache(
        self,
        curriculum
    ):

        filepath = self.get_cache_file(
            curriculum.department_code
        )

        temporary_file = (
            filepath
            + ".tmp"
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                curriculum.to_dict(),
                file,
                ensure_ascii=False,
                indent=2
            )

        os.replace(
            temporary_file,
            filepath
        )

    # ========================================================
    # CACHE LOAD
    # ========================================================

    def load_cache(
        self,
        department_code
    ):

        filepath = self.get_cache_file(
            department_code
        )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        return Curriculum.from_dict(
            data
        )

    # ========================================================
    # MANUAL RULES
    # ========================================================

    def apply_manual_rules(
        self,
        curriculum
    ):

        for course in curriculum.courses:

            course.manual_prerequisites = (
                self.manual_rules
                .get_prerequisites(
                    course.code
                )
            )

    def add_manual_prerequisite(
        self,
        course_code,
        prerequisite
    ):

        result = (
            self.manual_rules.add(
                course_code,
                prerequisite
            )
        )

        curriculum = self.curriculums.get(
            self._find_department_for_course(
                course_code
            )
        )

        if curriculum:

            course = curriculum.get_course(
                course_code
            )

            if course:

                course.manual_prerequisites = (
                    self.manual_rules
                    .get_prerequisites(
                        course_code
                    )
                )

        return result

    def remove_manual_prerequisite(
        self,
        course_code,
        prerequisite
    ):

        result = (
            self.manual_rules.remove(
                course_code,
                prerequisite
            )
        )

        curriculum = self.curriculums.get(
            self._find_department_for_course(
                course_code
            )
        )

        if curriculum:

            course = curriculum.get_course(
                course_code
            )

            if course:

                course.manual_prerequisites = (
                    self.manual_rules
                    .get_prerequisites(
                        course_code
                    )
                )

        return result

    # ========================================================
    # FIND DEPARTMENT
    # ========================================================

    def _find_department_for_course(
        self,
        course_code
    ):

        normalized = normalize_course_code(
            course_code
        )

        for department_code, curriculum in (
            self.curriculums.items()
        ):

            if curriculum.get_course(
                normalized
            ):
                return department_code

        return None
