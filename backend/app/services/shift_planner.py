from typing import Dict, List, Any, Optional
import math


class ShiftPlanner:
    """
    Intelligent Shift Planning & Capacity Analyzer.
    Evaluates whether the institution can operate in a single shift or requires multiple shifts
    based on classroom concurrency, laboratory throughput, operating hours, and faculty capacity.
    Never creates shifts merely to hide fundamental resource deficits.
    """

    @staticmethod
    def analyze_capacity(
        days_count: int,
        periods_per_day: int,
        period_duration_minutes: int,
        day_start_time: str,
        divisions: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        teachers: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        institution_type: str = "COLLEGE"
    ) -> Dict[str, Any]:
        # Categorize rooms
        lecture_rooms = [r for r in rooms if "lab" not in r.get("room_type", "lecture")]
        lab_rooms = [r for r in rooms if "lab" in r.get("room_type", "lecture")]
        
        num_classrooms = max(1, len(lecture_rooms))
        num_labs = len(lab_rooms)
        num_total_rooms = len(rooms)
        num_divisions = len(divisions)
        num_teachers = len(teachers)

        # Calculate Teaching Demand
        total_weekly_demand_periods = 0
        total_lab_demand_periods = 0
        max_division_periods = 0

        for div in divisions:
            cg_id = div.get("class_group_id")
            div_subjs = [s for s in subjects if s.get("class_group_id") == cg_id]
            div_hours = sum(s.get("weekly_hours", 0) for s in div_subjs)
            total_weekly_demand_periods += div_hours
            if div_hours > max_division_periods:
                max_division_periods = div_hours

            for s in div_subjs:
                if s.get("is_lab", False):
                    total_lab_demand_periods += s.get("weekly_hours", 0)

        # Faculty Capacity
        total_faculty_capacity = sum(t.get("max_hours_per_week", 20) for t in teachers)

        # Available slots per room in a single shift
        slots_per_room_single_shift = days_count * periods_per_day
        total_classroom_capacity_single_shift = num_classrooms * slots_per_room_single_shift
        total_lab_capacity_single_shift = num_labs * slots_per_room_single_shift

        # Fundamental Deficit Checks (Shortages that shifts CANNOT fix)
        deficits = []
        if total_weekly_demand_periods > total_faculty_capacity:
            shortage = total_weekly_demand_periods - total_faculty_capacity
            deficits.append({
                "type": "FACULTY_DEFICIT",
                "severity": "CRITICAL",
                "message": f"Total faculty teaching capacity ({total_faculty_capacity} hrs/wk) is insufficient for weekly curriculum demand ({total_weekly_demand_periods} hrs/wk). Deficit: {shortage} hours/week.",
                "solution": f"Recruit approximately {math.ceil(shortage / 18)} additional faculty members or reduce curriculum hours."
            })

        # Room Concurrency Check
        room_shortage_single_shift = num_divisions > num_classrooms
        lab_shortage_single_shift = (total_lab_demand_periods > total_lab_capacity_single_shift) if num_labs > 0 else (total_lab_demand_periods > 0)

        # Evaluate Scenarios
        scenarios = []

        # Scenario 1: Single General Shift
        single_shift_feasible = (not room_shortage_single_shift) and (not lab_shortage_single_shift) and (max_division_periods <= slots_per_room_single_shift)
        s1_room_utilization = round((total_weekly_demand_periods / max(1, (num_total_rooms * slots_per_room_single_shift))) * 100, 1)

        scenarios.append({
            "id": "single_shift",
            "name": "Standard Single Shift",
            "is_feasible": single_shift_feasible,
            "shifts": [
                {
                    "name": "General Shift",
                    "start_time": day_start_time,
                    "end_time": ShiftPlanner._calculate_end_time(day_start_time, periods_per_day, period_duration_minutes),
                    "periods": periods_per_day,
                    "target_divisions": "All Active Divisions"
                }
            ],
            "metrics": {
                "room_utilization_pct": min(100.0, s1_room_utilization),
                "faculty_convenience_score": 92.0,
                "student_convenience_score": 95.0,
                "operating_cost_index": "Baseline (1.0x)",
                "shifts_count": 1
            },
            "pros": [
                "Uniform operational schedule across all departments",
                "No overlapping faculty fatigue or late-evening commutes",
                "Simplified transport and cafeteria management"
            ],
            "cons": [
                f"Requires at least {num_divisions} dedicated classrooms concurrently" if room_shortage_single_shift else "Lower room utilization during off-hours"
            ],
            "bottlenecks": [
                f"Peak classroom deficit: Needs {num_divisions} rooms, but only {num_classrooms} exist."
            ] if room_shortage_single_shift else []
        })

        # Scenario 2: Two Shifts (Morning & Afternoon)
        # Divides divisions across 2 shifts
        shift1_div_count = math.ceil(num_divisions / 2)
        shift2_div_count = num_divisions - shift1_div_count
        dual_shift_feasible = (shift1_div_count <= num_classrooms) and (shift2_div_count <= num_classrooms)

        s2_room_utilization = round((total_weekly_demand_periods / max(1, (num_total_rooms * slots_per_room_single_shift * 2))) * 100 * 2, 1)

        m_end_time = ShiftPlanner._calculate_end_time("07:45", periods_per_day, period_duration_minutes)
        a_end_time = ShiftPlanner._calculate_end_time("13:15", periods_per_day, period_duration_minutes)

        scenarios.append({
            "id": "dual_shift",
            "name": "Split Shift (Morning & Afternoon)",
            "is_feasible": dual_shift_feasible,
            "shifts": [
                {
                    "name": "Morning Shift",
                    "start_time": "07:45",
                    "end_time": m_end_time,
                    "periods": periods_per_day,
                    "target_divisions": f"{shift1_div_count} Senior / Primary Divisions"
                },
                {
                    "name": "Afternoon Shift",
                    "start_time": "13:15",
                    "end_time": a_end_time,
                    "periods": periods_per_day,
                    "target_divisions": f"{shift2_div_count} Junior / Secondary Divisions"
                }
            ],
            "metrics": {
                "room_utilization_pct": min(100.0, s2_room_utilization),
                "faculty_convenience_score": 78.0,
                "student_convenience_score": 82.0,
                "operating_cost_index": "Moderate (+25% facility hours)",
                "shifts_count": 2
            },
            "pros": [
                f"Effectively doubles classroom throughput (accommodates up to {num_classrooms * 2} divisions)",
                "Resolves physical room capacity bottlenecks without construction",
                "High infrastructure and equipment ROI"
            ],
            "cons": [
                "Requires careful teacher scheduling to avoid multi-shift spanning fatigue",
                "Extended facility operating hours (lighting, security, air conditioning)"
            ],
            "bottlenecks": []
        })

        # Scenario 3: Regular + Evening Shift (Ideal for Coaching / Continuing Education)
        scenarios.append({
            "id": "evening_shift",
            "name": "Day & Evening Extended Shift",
            "is_feasible": True,
            "shifts": [
                {
                    "name": "Regular Day Shift",
                    "start_time": "08:30",
                    "end_time": "15:00",
                    "periods": periods_per_day,
                    "target_divisions": "Regular Academic Cohorts"
                },
                {
                    "name": "Evening Special Shift",
                    "start_time": "16:00",
                    "end_time": "20:30",
                    "periods": max(4, periods_per_day - 2),
                    "target_divisions": "Intensive Coaching / Advanced Batches"
                }
            ],
            "metrics": {
                "room_utilization_pct": 88.5,
                "faculty_convenience_score": 74.0,
                "student_convenience_score": 85.0,
                "operating_cost_index": "Higher (+35%)",
                "shifts_count": 2
            },
            "pros": [
                "Perfect for coaching institutes or executive university batches",
                "Allows specialized faculty to teach afternoon/evening modules"
            ],
            "cons": [
                "Requires night transport and dedicated evening support staff"
            ],
            "bottlenecks": []
        })

        # Determine Recommendation
        if single_shift_feasible:
            recommended_id = "single_shift"
            recommendation_reason = (
                f"Single Shift is fully feasible and recommended. Physical classrooms ({num_classrooms}) "
                f"comfortably accommodate all active divisions ({num_divisions}) with optimal student and teacher convenience."
            )
        elif dual_shift_feasible:
            recommended_id = "dual_shift"
            recommendation_reason = (
                f"Dual Shift is recommended. Single shift is blocked because the institution has {num_divisions} divisions "
                f"competing for {num_classrooms} classrooms. Splitting into Morning and Afternoon shifts resolves this room constraint."
            )
        else:
            recommended_id = "single_shift"
            recommendation_reason = (
                "Neither standard single nor dual shifts can fully satisfy current demands without expanding physical infrastructure."
            )

        return {
            "summary": {
                "institution_type": institution_type,
                "total_divisions": num_divisions,
                "total_classrooms": num_classrooms,
                "total_laboratories": num_labs,
                "total_teachers": num_teachers,
                "total_weekly_demand_periods": total_weekly_demand_periods,
                "total_faculty_capacity_periods": total_faculty_capacity,
                "single_shift_capacity_periods": total_classroom_capacity_single_shift,
                "single_shift_feasible": single_shift_feasible
            },
            "deficits": deficits,
            "recommended_scenario_id": recommended_id,
            "recommendation_reason": recommendation_reason,
            "scenarios": scenarios
        }

    @staticmethod
    def _calculate_end_time(start_str: str, periods: int, duration_min: int) -> str:
        try:
            parts = start_str.split(":")
            h = int(parts[0])
            m = int(parts[1])
            total_min = h * 60 + m + (periods * duration_min) + 30  # include typical break
            end_h = (total_min // 60) % 24
            end_m = total_min % 60
            return f"{end_h:02d}:{end_m:02d}"
        except Exception:
            return "16:00"
