import io
from typing import Dict, List, Any
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


class ExportService:
    """
    Exports generated timetables into professionally styled Excel workbooks (.xlsx)
    with per-division sheets, faculty schedules, and room utilization grids.
    """

    @classmethod
    def generate_excel(
        cls,
        scenario_name: str,
        institution_name: str,
        days: List[str],
        periods_per_day: int,
        divisions: List[Dict[str, Any]],
        teachers: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        entries: List[Dict[str, Any]]
    ) -> bytes:
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        subj_map = {s["id"]: s for s in subjects}
        teacher_map = {t["id"]: t for t in teachers}
        room_map = {r["id"]: r for r in rooms}

        # Styles
        title_font = Font(name="Calibri", size=16, bold=True, color="1E293B")
        subtitle_font = Font(name="Calibri", size=11, italic=True, color="64748B")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell_font = Font(name="Calibri", size=10, color="0F172A")
        sub_font = Font(name="Calibri", size=9, color="475569")
        
        header_fill = PatternFill(start_color="4338CA", end_color="4338CA", fill_type="solid")
        day_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
        card_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # 1. Sheets for each Division
        for div in divisions:
            sheet_title = f"{div['name']}"[:31]  # Excel 31 char limit
            ws = wb.create_sheet(title=sheet_title)

            # Title
            ws["A1"] = f"{institution_name} — {scenario_name}"
            ws["A1"].font = title_font
            ws["A2"] = f"Class Timetable: {div['name']} (Students: {div.get('student_count', 40)})"
            ws["A2"].font = subtitle_font

            # Headers
            ws.cell(row=4, column=1, value="Day / Period").font = header_font
            ws.cell(row=4, column=1).fill = header_fill
            ws.cell(row=4, column=1).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=4, column=1).border = thin_border

            for p in range(periods_per_day):
                col_idx = p + 2
                c = ws.cell(row=4, column=col_idx, value=f"Period {p + 1}")
                c.font = header_font
                c.fill = header_fill
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = thin_border

            # Populate Days & Cells
            div_entries = [e for e in entries if e["division_id"] == div["id"]]
            entry_grid = {(e["day_index"], e["slot_index"]): e for e in div_entries}

            for d_idx, day_name in enumerate(days):
                r_idx = d_idx + 5
                day_cell = ws.cell(row=r_idx, column=1, value=day_name)
                day_cell.font = Font(name="Calibri", size=11, bold=True, color="312E81")
                day_cell.fill = day_fill
                day_cell.alignment = Alignment(horizontal="center", vertical="center")
                day_cell.border = thin_border
                ws.row_dimensions[r_idx].height = 42

                for p_idx in range(periods_per_day):
                    col_idx = p_idx + 2
                    cell = ws.cell(row=r_idx, column=col_idx)
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                    entry = entry_grid.get((d_idx, p_idx))
                    if entry:
                        s = subj_map.get(entry["subject_id"], {})
                        t = teacher_map.get(entry["teacher_id"], {})
                        rm = room_map.get(entry["room_id"], {})
                        
                        s_name = s.get("name", "Subject")
                        t_name = t.get("name", "Teacher")
                        rm_name = rm.get("name", "Room")

                        cell.value = f"{s_name}\n({t_name} • {rm_name})"
                        cell.font = cell_font
                        cell.fill = card_fill
                    else:
                        cell.value = "—"
                        cell.font = sub_font

            # Adjust column widths
            ws.column_dimensions["A"].width = 16
            for p in range(periods_per_day):
                col_letter = get_column_letter(p + 2)
                ws.column_dimensions[col_letter].width = 24

        # 2. Sheet for Faculty Overview
        ws_fac = wb.create_sheet(title="Faculty Master")
        ws_fac["A1"] = f"{institution_name} — Faculty Workload & Allocation"
        ws_fac["A1"].font = title_font
        ws_fac.cell(row=3, column=1, value="Faculty Name").font = header_font
        ws_fac.cell(row=3, column=1).fill = header_fill
        ws_fac.cell(row=3, column=2, value="Code").font = header_font
        ws_fac.cell(row=3, column=2).fill = header_fill
        ws_fac.cell(row=3, column=3, value="Assigned Periods/Wk").font = header_font
        ws_fac.cell(row=3, column=3).fill = header_fill
        ws_fac.cell(row=3, column=4, value="Max Allowed").font = header_font
        ws_fac.cell(row=3, column=4).fill = header_fill
        ws_fac.cell(row=3, column=5, value="Utilization %").font = header_font
        ws_fac.cell(row=3, column=5).fill = header_fill

        for idx, t in enumerate(teachers):
            r_idx = idx + 4
            t_entries = [e for e in entries if e["teacher_id"] == t["id"]]
            assigned = len(t_entries)
            limit = t.get("max_hours_per_week", 20)
            util = round((assigned / max(1, limit)) * 100, 1)

            ws_fac.cell(row=r_idx, column=1, value=t.get("name")).font = cell_font
            ws_fac.cell(row=r_idx, column=2, value=t.get("code")).font = sub_font
            ws_fac.cell(row=r_idx, column=3, value=assigned).alignment = Alignment(horizontal="center")
            ws_fac.cell(row=r_idx, column=4, value=limit).alignment = Alignment(horizontal="center")
            ws_fac.cell(row=r_idx, column=5, value=f"{util}%").alignment = Alignment(horizontal="center")

        ws_fac.column_dimensions["A"].width = 28
        ws_fac.column_dimensions["B"].width = 14
        ws_fac.column_dimensions["C"].width = 22
        ws_fac.column_dimensions["D"].width = 16
        ws_fac.column_dimensions["E"].width = 16

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream.getvalue()
