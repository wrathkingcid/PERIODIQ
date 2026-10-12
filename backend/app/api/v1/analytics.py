from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database import get_db
from app.models.institution import Institution
from app.models.academic import Division, ClassGroup
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.models.timetable import TimetableScenario, TimetableEntry
from app.models.audit import AuditLog

router = APIRouter(prefix="/analytics", tags=["Analytics & Heatmaps"])


@router.get("/institutions/{institution_id}/dashboard-summary")
def get_dashboard_summary(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    divisions_count = db.query(Division).filter(Division.institution_id == institution_id).count()
    teachers_count = db.query(Teacher).filter(Teacher.institution_id == institution_id).count()
    rooms_count = db.query(Room).filter(Room.institution_id == institution_id).count()
    subjects_count = db.query(Subject).filter(Subject.institution_id == institution_id).count()

    latest_scenario = db.query(TimetableScenario).filter(
        TimetableScenario.institution_id == institution_id
    ).order_by(TimetableScenario.id.desc()).first()

    recent_audits = db.query(AuditLog).filter(
        AuditLog.institution_id == institution_id
    ).order_by(AuditLog.id.desc()).limit(10).all()

    # Teacher Workload breakdown
    teacher_workloads = []
    teachers = db.query(Teacher).filter(Teacher.institution_id == institution_id).all()
    
    assigned_counts = {}
    if latest_scenario:
        entries = db.query(TimetableEntry).filter(TimetableEntry.scenario_id == latest_scenario.id).all()
        for e in entries:
            assigned_counts[e.teacher_id] = assigned_counts.get(e.teacher_id, 0) + 1

    for t in teachers:
        assigned = assigned_counts.get(t.id, 0)
        limit = t.max_hours_per_week
        teacher_workloads.append({
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "assigned_hours": assigned,
            "max_hours": limit,
            "utilization_pct": round((assigned / max(1, limit)) * 100, 1),
            "status": "OVERLOAD" if assigned > limit else ("BALANCED" if assigned >= limit * 0.7 else "UNDERLOAD")
        })

    # Room Utilization
    room_occupancies = []
    rooms = db.query(Room).filter(Room.institution_id == institution_id).all()
    room_entries_count = {}
    if latest_scenario:
        for e in entries:
            room_entries_count[e.room_id] = room_entries_count.get(e.room_id, 0) + 1

    total_possible_slots = len(inst.working_days) * inst.periods_per_day
    for r in rooms:
        occupied = room_entries_count.get(r.id, 0)
        room_occupancies.append({
            "id": r.id,
            "name": r.name,
            "type": r.room_type,
            "capacity": r.capacity,
            "occupied_slots": occupied,
            "total_slots": total_possible_slots,
            "utilization_pct": round((occupied / max(1, total_possible_slots)) * 100, 1)
        })

    return {
        "kpis": {
            "total_divisions": divisions_count,
            "total_teachers": teachers_count,
            "total_rooms": rooms_count,
            "total_subjects": subjects_count,
            "has_active_schedule": latest_scenario is not None and latest_scenario.status in ["OPTIMAL", "FEASIBLE", "APPROVED", "PUBLISHED"],
            "latest_quality_score": latest_scenario.quality_score if latest_scenario else 0.0,
            "latest_scenario_status": latest_scenario.status if latest_scenario else "NO_SCHEDULE",
            "active_scenario_id": latest_scenario.id if latest_scenario else None
        },
        "teacher_workloads": teacher_workloads,
        "room_occupancies": room_occupancies,
        "recent_audits": recent_audits
    }
