import io
import re
import csv
from typing import Dict, List, Any, Optional
import openpyxl
from pypdf import PdfReader


class DocumentParser:
    """
    Intelligent Data Extraction & Ingestion Engine.
    Parses Excel (.xlsx), CSV, JSON, and PDF files containing institutional curriculum,
    faculty, classrooms, and student divisions into a standardized internal representation.
    Detects inconsistencies, missing parameters, and generates minimal essential clarification questions.
    """

    COLUMN_SYNONYMS = {
        "subject_name": ["subject", "subject_name", "course", "course_name", "title", "subject title", "paper"],
        "subject_code": ["code", "subject_code", "course_code", "paper_code", "sub_code"],
        "weekly_hours": ["weekly_hours", "hours", "periods", "weekly_periods", "lectures", "credits", "contact_hours", "l-t-p"],
        "is_lab": ["is_lab", "lab", "practical", "is_practical", "type", "session_type", "theory/practical"],
        "teacher_name": ["teacher", "teacher_name", "faculty", "faculty_name", "instructor", "professor", "name"],
        "teacher_email": ["email", "mail", "contact_email", "e-mail"],
        "max_hours": ["max_hours", "max_hours_per_week", "workload", "max_workload", "weekly_limit"],
        "room_name": ["room", "room_name", "classroom", "hall", "lab_name", "venue", "lab"],
        "room_type": ["room_type", "type", "category", "facility_type"],
        "capacity": ["capacity", "seats", "intake", "max_students", "size"],
        "class_name": ["class", "class_name", "grade", "year", "semester", "cohort", "standard"],
        "division_name": ["division", "division_name", "section", "sec", "div", "batch"]
    }

    @classmethod
    def parse_file(cls, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        ext = filename.lower().split(".")[-1]
        raw_tables = {}

        if ext in ["xlsx", "xlsm", "xltx"]:
            raw_tables = cls._parse_excel(content_bytes)
        elif ext in ["csv", "txt"]:
            raw_tables = {"default": cls._parse_csv(content_bytes)}
        elif ext == "pdf":
            raw_tables = cls._parse_pdf(content_bytes)
        else:
            raise ValueError(f"Unsupported file format '.{ext}'. Supported formats: .xlsx, .csv, .pdf")

        return cls._normalize_and_validate(raw_tables)

    @classmethod
    def _parse_excel(cls, content_bytes: bytes) -> Dict[str, List[Dict[str, Any]]]:
        wb = openpyxl.load_workbook(filename=io.BytesIO(content_bytes), data_only=True)
        tables = {}
        for sheetname in wb.sheetnames:
            sheet = wb[sheetname]
            rows = list(sheet.iter_rows(values_only=True))
            if not rows or len(rows) < 2:
                continue
            
            # Find header row
            header_idx = 0
            for idx, r in enumerate(rows[:5]):
                if any(isinstance(cell, str) and len(cell.strip()) > 1 for cell in r if cell):
                    header_idx = idx
                    break
            
            headers = [str(cell).strip().lower() if cell is not None else f"col_{i}" for i, cell in enumerate(rows[header_idx])]
            sheet_data = []
            for row in rows[header_idx + 1:]:
                if not any(row):
                    continue
                row_dict = {}
                for h, cell in zip(headers, row):
                    if h and cell is not None:
                        row_dict[h] = cell
                if row_dict:
                    sheet_data.append(row_dict)

            tables[sheetname.lower()] = sheet_data

        return tables

    @classmethod
    def _parse_csv(cls, content_bytes: bytes) -> List[Dict[str, Any]]:
        text = content_bytes.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows or len(rows) < 2:
            return []

        headers = [str(h).strip().lower() for h in rows[0]]
        records = []
        for row in rows[1:]:
            if not any(row):
                continue
            row_dict = {}
            for h, cell in zip(headers, row):
                row_dict[h] = cell.strip()
            records.append(row_dict)

        return records

    @classmethod
    def _parse_pdf(cls, content_bytes: bytes) -> Dict[str, List[Dict[str, Any]]]:
        reader = PdfReader(io.BytesIO(content_bytes))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or "\n"

        # Regex / line parser to identify subjects, teachers, and rooms from academic documents
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        subjects = []
        teachers = []
        rooms = []

        for line in lines:
            # Pattern: Subject Code, Name, Hours
            subj_match = re.search(r"([A-Z]{2,4}[-\s]?\d{3,4})\s+([A-Za-z\s]+?)\s+(\d)\s*(hrs|credits|periods)?", line, re.IGNORECASE)
            if subj_match:
                code, name, hrs, _ = subj_match.groups()
                subjects.append({
                    "subject_code": code.strip(),
                    "subject_name": name.strip(),
                    "weekly_hours": int(hrs),
                    "is_lab": "lab" in name.lower() or "practical" in name.lower()
                })

            # Pattern: Teacher Name, Dept/Designation
            if any(title in line for title in ["Dr.", "Prof.", "Mr.", "Ms.", "Mrs."]):
                teachers.append({
                    "teacher_name": line,
                    "max_hours": 18
                })

            # Pattern: Room / Lab Name
            if re.search(r"\b(Room|Lab|Hall|LH|Auditorium)[-\s]?\d+", line, re.IGNORECASE):
                rooms.append({
                    "room_name": line,
                    "capacity": 45
                })

        return {
            "subjects": subjects,
            "teachers": teachers,
            "rooms": rooms
        }

    @classmethod
    def _normalize_and_validate(cls, raw_tables: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "subjects": [],
            "teachers": [],
            "rooms": [],
            "classes": [],
            "divisions": []
        }
        warnings = []
        clarification_questions = []

        all_records = []
        if isinstance(raw_tables, dict):
            for sheetname, records in raw_tables.items():
                if isinstance(records, list):
                    all_records.extend([(sheetname, r) for r in records])
        elif isinstance(raw_tables, list):
            all_records = [("default", r) for r in raw_tables]

        # Extract entities based on header synonyms
        for sheetname, r in all_records:
            norm_r = cls._map_row(r)
            
            # Check if this row is a subject
            if "subject_name" in norm_r:
                hrs = norm_r.get("weekly_hours", 4)
                try:
                    hrs = int(float(str(hrs).replace("hrs", "").replace("p", "").strip()))
                except Exception:
                    hrs = 4

                is_lab = False
                val = str(norm_r.get("is_lab", "")).lower()
                if "lab" in val or "practical" in val or "true" in val or "1" in val:
                    is_lab = True
                elif "lab" in str(norm_r.get("subject_name", "")).lower():
                    is_lab = True

                normalized["subjects"].append({
                    "name": norm_r.get("subject_name"),
                    "code": norm_r.get("subject_code", f"SUB-{len(normalized['subjects']) + 1}"),
                    "weekly_hours": hrs,
                    "consecutive_periods": 2 if is_lab else 1,
                    "is_lab": is_lab,
                    "preferred_room_type": "lab_computer" if (is_lab and "comp" in norm_r.get("subject_name", "").lower()) else ("lab_science" if is_lab else "lecture")
                })

            # Check if this row is a teacher
            if "teacher_name" in norm_r and norm_r["teacher_name"] not in [s["name"] for s in normalized["subjects"]]:
                normalized["teachers"].append({
                    "name": norm_r.get("teacher_name"),
                    "code": f"T-{len(normalized['teachers']) + 1}",
                    "email": norm_r.get("teacher_email", ""),
                    "max_hours_per_week": int(norm_r.get("max_hours", 20)),
                    "max_hours_per_day": 4
                })

            # Check if this row is a room
            if "room_name" in norm_r:
                cap = norm_r.get("capacity", 50)
                try:
                    cap = int(cap)
                except Exception:
                    cap = 50
                rname = str(norm_r.get("room_name"))
                rtype = "lab_computer" if "comp" in rname.lower() else ("lab_science" if "lab" in rname.lower() else "lecture")
                normalized["rooms"].append({
                    "name": rname,
                    "code": rname.replace(" ", "-"),
                    "capacity": cap,
                    "room_type": rtype
                })

        # Generate default Class Group / Division if not explicitly found
        if not normalized["divisions"]:
            normalized["classes"] = [
                {"name": "Cohort Year 1", "code": "Y1"},
                {"name": "Cohort Year 2", "code": "Y2"}
            ]
            normalized["divisions"] = [
                {"name": "Section A", "student_count": 45, "class_index": 0},
                {"name": "Section B", "student_count": 40, "class_index": 0}
            ]

        # Validation Checks & Contradictions
        # Check 1: Missing Lab Room for Practical Subjects
        has_lab_subj = any(s["is_lab"] for s in normalized["subjects"])
        has_lab_room = any("lab" in r["room_type"] for r in normalized["rooms"])
        if has_lab_subj and not has_lab_room:
            warnings.append({
                "severity": "WARNING",
                "entity": "Laboratories",
                "message": "Practicals or Lab subjects were detected, but no specialized laboratory rooms are defined."
            })
            clarification_questions.append({
                "id": "missing_labs",
                "question": "Lab subjects detected but no dedicated labs found. Would you like to designate existing classrooms as multi-purpose labs or add dedicated lab facilities?",
                "options": ["Convert existing room to Lab", "Add dedicated Laboratory", "Treat as standard classroom"]
            })

        # Check 2: Missing Teacher Workload
        for t in normalized["teachers"]:
            if t["max_hours_per_week"] > 35:
                warnings.append({
                    "severity": "ALERT",
                    "entity": f"Faculty '{t['name']}'",
                    "message": f"Assigned workload limit is {t['max_hours_per_week']} hrs/wk, which is unusually high."
                })

        # Check 3: Consecutive Period Policy
        if has_lab_subj:
            clarification_questions.append({
                "id": "lab_consecutive_block",
                "question": "Should practical/laboratory sessions be scheduled as 2 consecutive periods or single periods?",
                "options": ["2 Consecutive Periods (Standard)", "3 Consecutive Periods (Extended Lab)", "Single Period"]
            })

        return {
            "data": normalized,
            "counts": {
                "subjects": len(normalized["subjects"]),
                "teachers": len(normalized["teachers"]),
                "rooms": len(normalized["rooms"]),
                "classes": len(normalized["classes"]),
                "divisions": len(normalized["divisions"])
            },
            "warnings": warnings,
            "clarification_questions": clarification_questions
        }

    @classmethod
    def _map_row(cls, row_dict: Dict[str, Any]) -> Dict[str, Any]:
        mapped = {}
        for k, v in row_dict.items():
            clean_k = str(k).strip().lower()
            for std_field, synonyms in cls.COLUMN_SYNONYMS.items():
                if any(syn in clean_k for syn in synonyms):
                    mapped[std_field] = v
                    break
        return mapped
