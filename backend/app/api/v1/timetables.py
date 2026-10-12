from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.models.institution import Institution
from app.models.academic import Division, ClassGroup
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.models.timetable import TimetableScenario, TimetableEntry
from app.models.audit import AuditLog
from app.schemas import GenerateTimetableRequest, SwapEntryRequest
from app.solver.cp_sat_engine import TimetableSolver
from app.services.export_service import ExportService

router = APIRouter(tags=["Timetables & Solver"])


@router.post("/institutions/{institution_id}/generate")
def generate_timetable(
    institution_id: int,
    payload: GenerateTimetableRequest,
    db: Session = Depends(get_db)
):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Fetch all data
    days = inst.working_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods_per_day = inst.periods_per_day or 7

    divisions = [
        {"id": d.id, "class_group_id": d.class_group_id, "name": d.name, "student_count": d.student_count}
        for d in db.query(Division).filter(Division.institution_id == institution_id).all()
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
        for s in db.query(Subject).filter(Subject.institution_id == institution_id).all()
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
        for t in db.query(Teacher).filter(Teacher.institution_id == institution_id).all()
    ]
    rooms = [
        {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "room_type": r.room_type,
            "capacity": r.capacity
        }
        for r in db.query(Room).filter(Room.institution_id == institution_id).all()
    ]

    # Check existing locked entries from any previous active scenario
    locked_entries = []
    latest_scenario = db.query(TimetableScenario).filter(
        TimetableScenario.institution_id == institution_id,
        TimetableScenario.status.in_(["OPTIMAL", "FEASIBLE", "APPROVED"])
    ).order_by(TimetableScenario.id.desc()).first()

    if latest_scenario:
        locked_db = db.query(TimetableEntry).filter(
            TimetableEntry.scenario_id == latest_scenario.id,
            TimetableEntry.is_locked == True
        ).all()
        for le in locked_db:
            locked_entries.append({
                "division_id": le.division_id,
                "subject_id": le.subject_id,
                "teacher_id": le.teacher_id,
                "room_id": le.room_id,
                "day_index": le.day_index,
                "slot_index": le.slot_index
            })

    # Instantiate Solver
    solver = TimetableSolver(
        days=days,
        periods_per_day=periods_per_day,
        divisions=divisions,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms,
        locked_entries=locked_entries,
        timeout_seconds=payload.timeout_seconds,
        enable_soft_constraints=payload.enable_soft_constraints
    )

    result = solver.solve()

    # Create Scenario
    scenario = TimetableScenario(
        institution_id=institution_id,
        name=payload.scenario_name,
        academic_year=payload.academic_year,
        term=payload.term,
        status=result["status"],
        solver_status=result["solver_status"],
        solver_time_seconds=result["solver_time_seconds"],
        quality_score=result["quality_score"],
        metrics=result["metrics"],
        infeasibility_report=result["infeasibility_report"]
    )
    db.add(scenario)
    db.flush()

    # Save Entries if feasible
    if result["status"] in ["OPTIMAL", "FEASIBLE"]:
        for e in result["entries"]:
            entry_model = TimetableEntry(
                scenario_id=scenario.id,
                day_index=e["day_index"],
                day_name=e["day_name"],
                slot_index=e["slot_index"],
                slot_label=e["slot_label"],
                division_id=e["division_id"],
                class_group_id=e["class_group_id"],
                subject_id=e["subject_id"],
                teacher_id=e["teacher_id"],
                room_id=e["room_id"],
                is_locked=e.get("is_locked", False)
            )
            db.add(entry_model)

    # Log in Audit
    audit = AuditLog(
        institution_id=institution_id,
        action="GENERATE_TIMETABLE",
        details=f"Scenario '{scenario.name}' generated. Result: {result['status']}, Quality: {result['quality_score']}%"
    )
    db.add(audit)
    db.commit()
    db.refresh(scenario)

    return {
        "scenario": scenario,
        "result": result
    }


@router.get("/institutions/{institution_id}/scenarios")
def list_scenarios(institution_id: int, db: Session = Depends(get_db)):
    return db.query(TimetableScenario).filter(
        TimetableScenario.institution_id == institution_id
    ).order_by(TimetableScenario.id.desc()).all()


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    sc = db.query(TimetableScenario).filter(TimetableScenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")

    entries = db.query(TimetableEntry).filter(TimetableEntry.scenario_id == scenario_id).all()
    return {
        "scenario": sc,
        "entries": entries
    }


@router.post("/entries/{entry_id}/toggle-lock")
def toggle_lock_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.is_locked = not entry.is_locked
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "is_locked": entry.is_locked}


@router.post("/entries/{entry_id}/swap")
def swap_entry(entry_id: int, payload: SwapEntryRequest, db: Session = Depends(get_db)):
    entry = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    sc_id = entry.scenario_id

    # Check Conflicts at target day and slot
    conflicts = []

    # 1. Division double-booking check
    div_clash = db.query(TimetableEntry).filter(
        TimetableEntry.scenario_id == sc_id,
        TimetableEntry.division_id == entry.division_id,
        TimetableEntry.day_index == payload.target_day_index,
        TimetableEntry.slot_index == payload.target_slot_index,
        TimetableEntry.id != entry.id
    ).first()
    if div_clash:
        conflicts.append(f"Student division already has a class in slot {payload.target_slot_index + 1}.")

    # 2. Teacher double-booking check
    t_id = payload.target_teacher_id or entry.teacher_id
    teacher_clash = db.query(TimetableEntry).filter(
        TimetableEntry.scenario_id == sc_id,
        TimetableEntry.teacher_id == t_id,
        TimetableEntry.day_index == payload.target_day_index,
        TimetableEntry.slot_index == payload.target_slot_index,
        TimetableEntry.id != entry.id
    ).first()
    if teacher_clash:
        conflicts.append(f"Faculty is already assigned to another division in slot {payload.target_slot_index + 1}.")

    # 3. Room double-booking check
    r_id = payload.target_room_id or entry.room_id
    room_clash = db.query(TimetableEntry).filter(
        TimetableEntry.scenario_id == sc_id,
        TimetableEntry.room_id == r_id,
        TimetableEntry.day_index == payload.target_day_index,
        TimetableEntry.slot_index == payload.target_slot_index,
        TimetableEntry.id != entry.id
    ).first()
    if room_clash:
        conflicts.append(f"Room is already occupied in slot {payload.target_slot_index + 1}.")

    if conflicts:
        return {
            "success": False,
            "has_conflicts": True,
            "conflicts": conflicts
        }

    # If no conflicts, perform swap/move
    entry.day_index = payload.target_day_index
    entry.slot_index = payload.target_slot_index
    if payload.target_room_id:
        entry.room_id = payload.target_room_id
    if payload.target_teacher_id:
        entry.teacher_id = payload.target_teacher_id
    entry.is_manual_override = True

    db.commit()
    db.refresh(entry)
    return {"success": True, "has_conflicts": False, "entry": entry}


@router.post("/scenarios/{scenario_id}/publish")
def publish_scenario(scenario_id: int, db: Session = Depends(get_db)):
    sc = db.query(TimetableScenario).filter(TimetableScenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Unpublish other scenarios of same institution
    db.query(TimetableScenario).filter(
        TimetableScenario.institution_id == sc.institution_id
    ).update({"is_published": False, "status": "APPROVED"})

    sc.is_published = True
    sc.status = "PUBLISHED"
    db.commit()
    db.refresh(sc)
    return {"message": "Timetable published successfully!", "scenario": sc}


@router.get("/scenarios/{scenario_id}/export-excel")
def export_excel(scenario_id: int, db: Session = Depends(get_db)):
    sc = db.query(TimetableScenario).filter(TimetableScenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")

    inst = db.query(Institution).filter(Institution.id == sc.institution_id).first()
    divisions = [
        {"id": d.id, "name": d.name, "student_count": d.student_count}
        for d in db.query(Division).filter(Division.institution_id == inst.id).all()
    ]
    teachers = [
        {"id": t.id, "name": t.name, "code": t.code, "max_hours_per_week": t.max_hours_per_week}
        for t in db.query(Teacher).filter(Teacher.institution_id == inst.id).all()
    ]
    rooms = [
        {"id": r.id, "name": r.name, "code": r.code, "room_type": r.room_type}
        for r in db.query(Room).filter(Room.institution_id == inst.id).all()
    ]
    subjects = [
        {"id": s.id, "name": s.name, "code": s.code, "color_code": s.color_code}
        for s in db.query(Subject).filter(Subject.institution_id == inst.id).all()
    ]
    entries = [
        {
            "division_id": e.division_id,
            "subject_id": e.subject_id,
            "teacher_id": e.teacher_id,
            "room_id": e.room_id,
            "day_index": e.day_index,
            "slot_index": e.slot_index
        }
        for e in db.query(TimetableEntry).filter(TimetableEntry.scenario_id == scenario_id).all()
    ]

    xlsx_bytes = ExportService.generate_excel(
        scenario_name=sc.name,
        institution_name=inst.name,
        days=inst.working_days,
        periods_per_day=inst.periods_per_day,
        divisions=divisions,
        teachers=teachers,
        rooms=rooms,
        subjects=subjects,
        entries=entries
    )

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=timetable_{scenario_id}.xlsx"}
    )


@router.get("/institutions/{institution_id}/compare-scenarios")
def compare_scenarios(institution_id: int, sc1_id: int, sc2_id: int, db: Session = Depends(get_db)):
    s1 = db.query(TimetableScenario).filter(TimetableScenario.id == sc1_id).first()
    s2 = db.query(TimetableScenario).filter(TimetableScenario.id == sc2_id).first()
    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="One or both scenarios not found")

    return {
        "scenario_a": s1,
        "scenario_b": s2,
        "comparison": {
            "quality_delta": round((s1.quality_score or 0) - (s2.quality_score or 0), 1),
            "solver_time_delta": round((s1.solver_time_seconds or 0) - (s2.solver_time_seconds or 0), 2),
            "teacher_gaps_a": s1.metrics.get("teacher_idle_gaps", 0) if s1.metrics else 0,
            "teacher_gaps_b": s2.metrics.get("teacher_idle_gaps", 0) if s2.metrics else 0,
            "room_util_a": s1.metrics.get("room_utilization_pct", 0) if s1.metrics else 0,
            "room_util_b": s2.metrics.get("room_utilization_pct", 0) if s2.metrics else 0
        }
    }
