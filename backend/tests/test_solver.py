import pytest
from app.database import SessionLocal
from app.models.institution import Institution
from app.models.academic import Division
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.solver.cp_sat_engine import TimetableSolver
from app.services.shift_planner import ShiftPlanner


def test_school_solver():
    db = SessionLocal()
    school = db.query(Institution).filter(Institution.code == "GREENWOOD-HS").first()
    assert school is not None, "School must be loaded"

    divisions = [
        {"id": d.id, "class_group_id": d.class_group_id, "name": d.name, "student_count": d.student_count}
        for d in db.query(Division).filter(Division.institution_id == school.id).all()
    ]
    subjects = [
        {
            "id": s.id,
            "class_group_id": s.class_group_id,
            "department_id": s.department_id,
            "name": s.name,
            "code": s.code,
            "weekly_hours": s.weekly_hours,
            "consecutive_periods": s.consecutive_periods,
            "is_lab": s.is_lab,
            "preferred_room_type": s.preferred_room_type,
            "color_code": s.color_code
        }
        for s in db.query(Subject).filter(Subject.institution_id == school.id).all()
    ]
    teachers = [
        {
            "id": t.id,
            "department_id": t.department_id,
            "name": t.name,
            "code": t.code,
            "max_hours_per_day": t.max_hours_per_day,
            "max_hours_per_week": t.max_hours_per_week,
            "competent_subject_ids": t.competent_subject_ids or [],
            "blackout_slots": t.blackout_slots or [],
            "preferred_slots": t.preferred_slots or []
        }
        for t in db.query(Teacher).filter(Teacher.institution_id == school.id).all()
    ]
    rooms = [
        {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "room_type": r.room_type,
            "capacity": r.capacity
        }
        for r in db.query(Room).filter(Room.institution_id == school.id).all()
    ]

    solver = TimetableSolver(
        days=school.working_days,
        periods_per_day=school.periods_per_day,
        divisions=divisions,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms,
        timeout_seconds=20
    )

    result = solver.solve()
    db.close()

    assert result["status"] in ["OPTIMAL", "FEASIBLE"], f"Solver failed: {result}"
    assert len(result["entries"]) > 0, "Entries must not be empty"
    print(f"\n[SUCCESS] Timetable generated! Status: {result['status']}, Quality Score: {result['quality_score']}%, Total Entries: {len(result['entries'])}")


def test_shift_planner():
    db = SessionLocal()
    college = db.query(Institution).filter(Institution.code == "APEX-TECH").first()
    assert college is not None

    divisions = [
        {"id": d.id, "class_group_id": d.class_group_id, "name": d.name, "student_count": d.student_count}
        for d in db.query(Division).filter(Division.institution_id == college.id).all()
    ]
    subjects = [
        {"id": s.id, "class_group_id": s.class_group_id, "weekly_hours": s.weekly_hours, "is_lab": s.is_lab, "consecutive_periods": s.consecutive_periods}
        for s in db.query(Subject).filter(Subject.institution_id == college.id).all()
    ]
    teachers = [
        {"id": t.id, "name": t.name, "max_hours_per_week": t.max_hours_per_week}
        for t in db.query(Teacher).filter(Teacher.institution_id == college.id).all()
    ]
    rooms = [
        {"id": r.id, "name": r.name, "room_type": r.room_type, "capacity": r.capacity}
        for r in db.query(Room).filter(Room.institution_id == college.id).all()
    ]

    analysis = ShiftPlanner.analyze_capacity(
        days_count=len(college.working_days),
        periods_per_day=college.periods_per_day,
        period_duration_minutes=college.period_duration_minutes,
        day_start_time=college.day_start_time,
        divisions=divisions,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms,
        institution_type=college.type
    )
    db.close()

    assert "recommended_scenario_id" in analysis
    assert len(analysis["scenarios"]) > 0
    print(f"\n[SUCCESS] Shift analysis completed! Recommended: {analysis['recommended_scenario_id']}")


if __name__ == "__main__":
    test_school_solver()
    test_shift_planner()
