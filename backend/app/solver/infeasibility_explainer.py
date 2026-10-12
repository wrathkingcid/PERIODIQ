from typing import Dict, List, Any


class InfeasibilityExplainer:
    """
    Analyzes timetable requirements and resource constraints to diagnose
    the exact mathematical bottlenecks when a schedule cannot be satisfied.
    """

    @staticmethod
    def diagnose(
        days_count: int,
        periods_per_day: int,
        class_groups: List[Dict[str, Any]],
        divisions: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        teachers: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        locked_entries: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        total_available_slots_per_class = days_count * periods_per_day
        diagnostics = []
        recommendations = []
        severity = "HIGH"

        # 1. Check Class Schedule Demand vs Total Available Time Slots
        for div in divisions:
            div_id = div["id"]
            div_name = div.get("name", f"Division {div_id}")
            cg_id = div.get("class_group_id")
            
            # Find all subjects for this class group
            div_subjects = [s for s in subjects if s.get("class_group_id") == cg_id]
            total_demanded_hours = sum(s.get("weekly_hours", 0) for s in div_subjects)
            
            if total_demanded_hours > total_available_slots_per_class:
                diagnostics.append({
                    "category": "TIME_SLOT_OVERFLOW",
                    "entity": f"Class Division '{div_name}'",
                    "demanded": total_demanded_hours,
                    "available": total_available_slots_per_class,
                    "message": f"Division '{div_name}' demands {total_demanded_hours} weekly periods, but the timetable only provides {total_available_slots_per_class} slots ({days_count} days × {periods_per_day} periods)."
                })
                recommendations.append(
                    f"Reduce curriculum hours for '{div_name}' by {total_demanded_hours - total_available_slots_per_class} periods, or add an extra period/day or an additional working day."
                )

        # 2. Check Teacher Workload & Availability Deficits
        for teacher in teachers:
            t_id = teacher["id"]
            t_name = teacher.get("name", f"Teacher {t_id}")
            max_weekly = teacher.get("max_hours_per_week", 20)
            blackouts = teacher.get("blackout_slots", [])
            available_slots = total_available_slots_per_class - len(blackouts)
            
            # Find subjects this teacher is competent to teach
            competent_sub_ids = teacher.get("competent_subject_ids", [])
            comp_subjects = [s for s in subjects if s["id"] in competent_sub_ids]
            
            # If this is the ONLY teacher for these subjects, check minimum compulsory teaching demand
            compulsory_hours = 0
            for s in comp_subjects:
                # Count how many other teachers can teach this subject
                co_teachers = [other for other in teachers if s["id"] in other.get("competent_subject_ids", [])]
                if len(co_teachers) == 1:
                    # Sole instructor: all division hours fall strictly on this teacher
                    s_divs = [d for d in divisions if d.get("class_group_id") == s.get("class_group_id")]
                    compulsory_hours += s.get("weekly_hours", 0) * max(1, len(s_divs))
            
            if compulsory_hours > max_weekly:
                diagnostics.append({
                    "category": "TEACHER_MAX_HOURS_EXCEEDED",
                    "entity": f"Faculty '{t_name}'",
                    "demanded": compulsory_hours,
                    "available": max_weekly,
                    "message": f"Faculty '{t_name}' is the sole instructor for subjects requiring {compulsory_hours} periods/week, exceeding their max limit of {max_weekly} periods."
                })
                recommendations.append(
                    f"Assign a co-teacher or assistant faculty for subjects taught by '{t_name}', or increase their max weekly hours limit to at least {compulsory_hours}."
                )
            elif compulsory_hours > available_slots:
                diagnostics.append({
                    "category": "TEACHER_BLACKOUT_SHORTAGE",
                    "entity": f"Faculty '{t_name}'",
                    "demanded": compulsory_hours,
                    "available": available_slots,
                    "message": f"Faculty '{t_name}' requires {compulsory_hours} teaching periods, but blackout/unavailable slots leave only {available_slots} periods available."
                })
                recommendations.append(
                    f"Relax unavailable/blackout slots for '{t_name}' to allow flexible period scheduling."
                )

        # 3. Check Room and Laboratory Type Demands
        room_types = {}
        for r in rooms:
            rtype = r.get("room_type", "lecture")
            room_types[rtype] = room_types.get(rtype, 0) + 1

        lab_demands = {}
        for s in subjects:
            if s.get("is_lab", False):
                rtype = s.get("preferred_room_type", "lab_computer")
                s_divs = [d for d in divisions if d.get("class_group_id") == s.get("class_group_id")]
                hours = s.get("weekly_hours", 0) * max(1, len(s_divs))
                lab_demands[rtype] = lab_demands.get(rtype, 0) + hours

        for rtype, demanded_lab_hours in lab_demands.items():
            avail_rooms = room_types.get(rtype, 0)
            avail_lab_capacity = avail_rooms * total_available_slots_per_class
            if demanded_lab_hours > avail_lab_capacity:
                diagnostics.append({
                    "category": "LABORATORY_CAPACITY_DEFICIT",
                    "entity": f"Room Type '{rtype}'",
                    "demanded": demanded_lab_hours,
                    "available": avail_lab_capacity,
                    "message": f"Total practical/lab demand for '{rtype}' is {demanded_lab_hours} periods/week, but only {avail_rooms} room(s) exist, yielding max {avail_lab_capacity} periods."
                })
                recommendations.append(
                    f"Add at least {(demanded_lab_hours - avail_lab_capacity + total_available_slots_per_class - 1) // total_available_slots_per_class} additional '{rtype}' room(s), or enable a second shift for lab sessions."
                )

        # 4. Check Overall Room Count Bottleneck (Peak Concurrency)
        total_divisions = len(divisions)
        total_rooms = len(rooms)
        if total_divisions > total_rooms:
            diagnostics.append({
                "category": "OVERALL_ROOM_SHORTAGE",
                "entity": "Institution Classrooms",
                "demanded": total_divisions,
                "available": total_rooms,
                "message": f"Institution has {total_divisions} active class divisions running concurrently, but only {total_rooms} total rooms are available."
            })
            recommendations.append(
                f"Activate a multi-shift schedule (e.g. Morning Shift and Afternoon Shift) to share classrooms, or add {total_divisions - total_rooms} more classrooms."
            )

        if not diagnostics:
            diagnostics.append({
                "category": "COMPLEX_COMBINATORIAL_INTERLOCK",
                "entity": "Simultaneous Constraints",
                "demanded": None,
                "available": None,
                "message": "A tight combination of consecutive multi-period lab blocks, specific teacher blackout windows, and locked assignments prevents conflict-free placement."
            })
            recommendations.append("Increase solver time limit to 60-90 seconds.")
            recommendations.append("Unlock some pinned periods or relax teacher blackout windows.")
            recommendations.append("Split multi-period consecutive requirements into single periods where acceptable.")

        return {
            "status": "INFEASIBLE",
            "severity": severity,
            "diagnostic_count": len(diagnostics),
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "possible_solutions": [
                "Adjust shift configuration via the Shift Planner module to spread load across morning and afternoon.",
                "Review Teacher Availability: Reduce blackout periods for specialized faculty.",
                "Verify Room Allocations: Ensure lab subjects match appropriate room types with sufficient capacity.",
                "Check Locked Entries: Unpin overly restrictive manual timetable locks."
            ]
        }
