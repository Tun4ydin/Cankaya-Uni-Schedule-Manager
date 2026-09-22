import requests
import re
import time
from bs4 import BeautifulSoup

class CankayaScraper:
    BASE_URL = "https://www.cankaya.edu.tr/ogrenci_isleri/kodprogramlar.php"
    
    DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        })

    def fetch_department_codes(self):
        """Fetches available department/course codes from the dropdown menu."""
        try:
            resp = self.session.get(self.BASE_URL, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            select = soup.find('select', {'name': 'derskod'})
            if not select:
                return []
            
            codes = []
            for opt in select.find_all('option'):
                val = opt.get('value', '').strip()
                text = opt.text.strip()
                if val and val != '0':
                    codes.append({'code': val, 'name': text})
            return codes
        except Exception as e:
            print(f"Error fetching department codes: {e}")
            return []

    def parse_schedule_table(self, html_text, dept_code, year_grade):
        """Parses the weekly schedule table returned for a given department code and year."""
        soup = BeautifulSoup(html_text, 'html.parser')
        table = soup.find('table')
        if not table:
            return []

        rows = table.find_all('tr')
        if not rows:
            return []

        headers = [th.text.strip() for th in rows[0].find_all(['td', 'th'])]
        schedule_entries = []

        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            time_slot = cells[0].text.strip()

            for day_idx, cell in enumerate(cells[1:], start=1):
                if day_idx >= len(headers):
                    continue

                day_name = headers[day_idx].strip()
                fonts = cell.find_all('font')

                for font in fonts:
                    for br in font.find_all(['br', 'p']):
                        br.replace_with('\n')
                    
                    text_content = font.get_text()
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    if not lines:
                        continue

                    header_line = lines[0]
                    instructor = lines[1] if len(lines) > 1 else "Belirsiz"
                    classroom = ""

                    # 1. Check if lines has 3 or more items (line 0: course-sec, line 1: instructor, line 2+: classroom)
                    if len(lines) >= 3:
                        classroom = " ".join(lines[2:]).strip()

                    # 2. Check header_line for parentheses e.g. "CENG111 - 1 (LA01)"
                    paren_match = re.search(r'\(([^)]+)\)', header_line)
                    if paren_match:
                        if not classroom:
                            classroom = paren_match.group(1).strip()
                        header_line = header_line.replace(paren_match.group(0), '').strip()

                    parts = [p.strip() for p in header_line.split('-') if p.strip()]
                    if len(parts) >= 3:
                        course_code = parts[0]
                        section = parts[1]
                        if not classroom:
                            classroom = parts[2]
                    elif len(parts) == 2:
                        course_code = parts[0]
                        if '/' in parts[1]:
                            sec_parts = parts[1].split('/')
                            section = sec_parts[0].strip()
                            if not classroom:
                                classroom = sec_parts[1].strip()
                        else:
                            section = parts[1]
                    else:
                        course_code = header_line
                        section = "1"

                    course_code = re.sub(r'\s+', '', course_code)

                    # 3. Check instructor line for classroom e.g. "Doç. Dr. X (LA01)"
                    inst_paren = re.search(r'\(([^)]+)\)', instructor)
                    if inst_paren and not classroom:
                        classroom = inst_paren.group(1).strip()
                        instructor = instructor.replace(inst_paren.group(0), '').strip()

                    # 4. Check title attribute of font or cell
                    if not classroom:
                        title_val = font.get('title', '') or cell.get('title', '')
                        if title_val:
                            classroom = title_val.strip()

                    # Clean classroom prefix like "Derslik:" or "Sınıf:"
                    if classroom:
                        classroom = re.sub(r'^(Derslik|Sınıf|Oda|Room|Classroom)\s*[:\-]?\s*', '', classroom, flags=re.IGNORECASE).strip()

                    schedule_entries.append({
                        "dept_code": dept_code,
                        "year_grade": str(year_grade),
                        "course_code": course_code,
                        "section": section,
                        "instructor": instructor,
                        "classroom": classroom,
                        "day": day_name,
                        "time_slot": time_slot
                    })

        return schedule_entries

    def fetch_course_classroom_links(self):
        """Fetches all course schedule links from https://www.cankaya.edu.tr/dersler/"""
        try:
            resp = self.session.get("https://www.cankaya.edu.tr/dersler/", timeout=10)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            for a in soup.find_all('a'):
                href = a.get('href', '').strip()
                if href and 'DersProgram' in href and href.endswith('.html'):
                    links.append(href)
            return list(set(links))
        except Exception as e:
            print(f"Error fetching course classroom links: {e}")
            return []

    def parse_course_schedule_html(self, html_text):
        """Parses individual course schedule page (e.g. CENG-111.html) for classrooms."""
        soup = BeautifulSoup(html_text, 'html.parser')
        table = soup.find('table')
        if not table:
            return []

        rows = table.find_all('tr')
        if not rows:
            return []

        headers = [th.get_text(strip=True) for th in rows[0].find_all(['td', 'th'])]
        entries = []

        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            time_slot = cells[0].get_text(strip=True)

            for day_idx, cell in enumerate(cells[1:], start=1):
                if day_idx >= len(headers):
                    continue
                day_name = headers[day_idx].strip()

                for tag in cell.find_all(['br', 'p']):
                    tag.replace_with('\n')

                lines = [l.strip() for l in cell.get_text().split('\n') if l.strip() and l.strip() != '\xa0']
                i = 0
                while i < len(lines):
                    line = lines[i]
                    m = re.search(r"^([A-ZÇĞİÖŞÜa-zçğıöşü\s\-]+?\d+)\s*[-/]\s*(\d+)", line)
                    if m:
                        c_code = re.sub(r"[\s\-]", "", m.group(1)).upper()
                        s_no = m.group(2)
                        classroom = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1]
                            if not re.search(r"^[A-ZÇĞİÖŞÜa-zçğıöşü\s\-]+?\d+\s*[-/]\s*\d+", next_line):
                                classroom = next_line
                                i += 1
                        entries.append({
                            "course_code": c_code,
                            "section": s_no,
                            "day": day_name,
                            "time_slot": time_slot,
                            "classroom": classroom
                        })
                    i += 1

        return entries

    def fetch_all_classrooms(self, progress_callback=None, cancel_check=None, max_workers=15):
        """Fetches all course classroom schedules in parallel."""
        links = self.fetch_course_classroom_links()
        if not links:
            return []

        from concurrent.futures import ThreadPoolExecutor
        results = []
        total = len(links)
        completed = 0

        def fetch_one(url):
            nonlocal completed
            if cancel_check and cancel_check():
                return []
            try:
                resp = self.session.get(url, timeout=7)
                if resp.status_code == 200:
                    entries = self.parse_course_schedule_html(resp.text)
                    return entries
            except Exception:
                pass
            finally:
                completed += 1
                if progress_callback and completed % 20 == 0:
                    progress_callback(completed, total, f"Derslik bilgileri alınıyor ({completed}/{total})")
            return []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_results = list(executor.map(fetch_one, links))

        for batch in batch_results:
            results.extend(batch)

        return results

    def fetch_all_schedules(self, progress_callback=None, dept_list=None, cancel_check=None):
        """
        Scrapes all course schedules across specified departments and grade years,
        and enriches them with classroom information.
        progress_callback: function(current, total, message)
        cancel_check: function() -> bool (returns True if cancelled)
        """
        if dept_list is None:
            dept_info_list = self.fetch_department_codes()
            dept_codes = [d['code'] for d in dept_info_list]
        else:
            dept_codes = dept_list

        total_steps = len(dept_codes) * 6
        current_step = 0
        all_entries = []

        for dept_idx, code in enumerate(dept_codes):
            if cancel_check and cancel_check():
                break

            for year in range(1, 7):
                if cancel_check and cancel_check():
                    break

                current_step += 1
                if progress_callback:
                    msg = f"Ders verileri çekiliyor: {code} ({year}. Sınıf)"
                    progress_callback(current_step, total_steps, msg)

                payload = {
                    'derskod': code,
                    'dersno': str(year),
                    'finalsubmit': 'FINAL SUBMIT',
                    'sonfinal': '$thestates'
                }

                try:
                    resp = self.session.post(self.BASE_URL, data=payload, timeout=12)
                    if resp.status_code == 200:
                        entries = self.parse_schedule_table(resp.text, code, year)
                        all_entries.extend(entries)
                except Exception as e:
                    print(f"Error scraping {code} year {year}: {e}")

                time.sleep(0.02)

        # Merge classroom information
        if not (cancel_check and cancel_check()):
            if progress_callback:
                progress_callback(total_steps, total_steps, "Derslik bilgileri taranıyor...")
            try:
                classroom_entries = self.fetch_all_classrooms(
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )
                if classroom_entries:
                    # Build lookup maps
                    slot_lookup = {}
                    sec_lookup = {}
                    for ce in classroom_entries:
                        c = ce["course_code"]
                        s = ce["section"]
                        d = ce["day"]
                        t = ce["time_slot"]
                        room = ce.get("classroom", "")
                        if room:
                            slot_lookup[(c, s, d, t)] = room
                            if (c, s) not in sec_lookup:
                                sec_lookup[(c, s)] = room

                    for entry in all_entries:
                        c = entry["course_code"]
                        s = entry["section"]
                        d = entry["day"]
                        t = entry["time_slot"]
                        if not entry.get("classroom"):
                            entry["classroom"] = slot_lookup.get((c, s, d, t), sec_lookup.get((c, s), ""))
            except Exception as e:
                print(f"Error enriching classrooms: {e}")

        return all_entries
