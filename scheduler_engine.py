class SchedulerEngine:
    DAYS_ORDER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    @staticmethod
    def slots_overlap(slot1, slot2):
        """Checks if two schedule slots overlap in time."""
        if slot1.day != slot2.day:
            return False
        # If time_slot strings match exactly, they overlap
        if slot1.time_slot == slot2.time_slot:
            return True

        # Try parsing hour ranges e.g. "09:00/09:20" or "09:00-09:50"
        t1_start, t1_end = SchedulerEngine.parse_time_range(slot1.time_slot)
        t2_start, t2_end = SchedulerEngine.parse_time_range(slot2.time_slot)

        if t1_start is not None and t2_start is not None:
            return max(t1_start, t2_start) < min(t1_end, t2_end)

        return False

    @staticmethod
    def parse_time_range(time_str):
        """Parses time string like '09:00/09:20' or '09:00-09:50' into float hours e.g. (9.0, 9.33)."""
        try:
            cleaned = time_str.replace('/', '-').strip()
            parts = cleaned.split('-')
            if len(parts) == 2:
                h1, m1 = map(int, parts[0].split(':'))
                h2, m2 = map(int, parts[1].split(':'))
                
                start_val = h1 + m1 / 60.0
                end_val = h2 + m2 / 60.0

                # Çankaya timetable quirk: "09:00/09:20" actually represents the 09:00-09:50 period.
                # If duration is only 20 mins, expand to standard 50-min period slot
                if end_val - start_val < 0.5:
                    end_val = start_val + (50.0 / 60.0)

                return start_val, end_val
        except Exception:
            pass
        return None, None

    @staticmethod
    def sections_overlap(sec1, sec2):
        """Checks if two sections have any overlapping schedule slots."""
        for slot1 in sec1.slots:
            for slot2 in sec2.slots:
                if SchedulerEngine.slots_overlap(slot1, slot2):
                    return True, slot1
        return False, None

    @staticmethod
    def find_all_conflicts(sections_list):
        """
        Takes a list of Section objects and returns all conflicting slot details.
        Returns dict of format: { (day, time_slot): [list of conflicting Section objects] }
        """
        slot_map = {}
        for sec in sections_list:
            for slot in sec.slots:
                key = (slot.day, slot.time_slot)
                if key not in slot_map:
                    slot_map[key] = []
                slot_map[key].append(sec)

        conflicts = {}
        for key, sec_list in slot_map.items():
            distinct_courses = set(sec.course_code for sec in sec_list)
            if len(distinct_courses) > 1:
                conflicts[key] = sec_list

        return conflicts

    def generate_combinations(self, course_sections_dict, preferences=None):
        """
        Generates valid non-conflicting section combinations.
        course_sections_dict: { "CENG111": [Section1, Section2, ...], "MATH119": [...] }
        preferences: dict e.g. {"free_friday": True, "no_morning": False}
        
        Returns: list of combinations. Each combination is a list of Section objects.
        """
        course_codes = list(course_sections_dict.keys())
        if not course_codes:
            return []

        # List of lists of candidate sections per course
        sections_per_course = [course_sections_dict[code] for code in course_codes if course_sections_dict[code]]

        valid_combinations = []

        def backtrack(course_idx, current_combination):
            if course_idx == len(sections_per_course):
                valid_combinations.append(list(current_combination))
                return

            candidate_sections = sections_per_course[course_idx]
            for sec in candidate_sections:
                # Check conflict with already selected sections
                conflict_found = False
                for existing_sec in current_combination:
                    overlap, _ = self.sections_overlap(sec, existing_sec)
                    if overlap:
                        conflict_found = True
                        break

                if not conflict_found:
                    current_combination.append(sec)
                    backtrack(course_idx + 1, current_combination)
                    current_combination.pop()

        backtrack(0, [])

        # Apply preference filters / sorting if provided
        if preferences:
            valid_combinations = self.filter_and_rank_combinations(valid_combinations, preferences)

        return valid_combinations

    def filter_and_rank_combinations(self, combinations, preferences):
        filtered = []

        free_friday = preferences.get("free_friday", False)
        free_monday = preferences.get("free_monday", False)
        no_morning = preferences.get("no_morning", False)

        for combo in combinations:
            # Days occupied
            days_used = set()
            has_morning = False

            for sec in combo:
                for slot in sec.slots:
                    days_used.add(slot.day)
                    start, _ = self.parse_time_range(slot.time_slot)
                    if start is not None and start < 10.0:
                        has_morning = True

            if free_friday and "Cuma" in days_used:
                continue
            if free_monday and "Pazartesi" in days_used:
                continue
            if no_morning and has_morning:
                continue

            filtered.append(combo)

        # Sort combinations by number of free days (most free days first)
        def score_combination(combo):
            days_used = set()
            for sec in combo:
                for slot in sec.slots:
                    days_used.add(slot.day)
            return len(days_used)

        filtered.sort(key=score_combination)
        return filtered
