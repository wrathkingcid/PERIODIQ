from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.institution import Institution
from app.models.academic import Division
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.services.shift_planner import ShiftPlanner

router = APIRouter(prefix="/shifts", tags=["Intelligent Shift Planning"])


@router.post("/institutions/{institution_id}/analyze")
def analyze_shifts(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    divisions = [
        {"id": d.id, "class_group_id": d.class_group_id, "name": d.name, "student_count": d.student_count}
        for d in db.query(Division).filter(Division.institution_id == institution_id).all()
    ]
    subjects = [
        {"id": s.id, "class_group_id": s.class_group_id, "weekly_hours": s.weekly_hours, "is_lab": s.is_lab, "consecutive_periods": s.consecutive_periods}
        for s in db.query(Subject).filter(Subject.institution_id == institution_id).all()
    ]
    teachers = [
        {"id": t.id, "name": t.name, "max_hours_per_week": t.max_hours_per_week}
        for t in db.query(Teacher).filter(Teacher.institution_id == institution_id).all()
    ]
    rooms = [
        {"id": r.id, "name": r.name, "room_type": r.room_type, "capacity": r.capacity}
        for r in db.query(Room).filter(Room.institution_id == institution_id).all()
    ]

    analysis = ShiftPlanner.analyze_capacity(
        days_count=len(inst.working_days),
        periods_per_day=inst.periods_per_day,
        period_duration_minutes=inst.period_duration_minutes,
        day_start_time=inst.day_start_time,
        divisions=divisions,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms,
        institution_type=inst.type
    )

    return analysis
