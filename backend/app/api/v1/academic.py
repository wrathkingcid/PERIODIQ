from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.academic import Department, ClassGroup, Division, Batch
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.schemas import SubjectCreate, TeacherCreate, RoomCreate

router = APIRouter(prefix="/academic", tags=["Academic Structure & Resources"])


# Departments & Classes
@router.get("/institutions/{institution_id}/departments")
def list_departments(institution_id: int, db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.institution_id == institution_id).all()


@router.get("/institutions/{institution_id}/classes")
def list_classes(institution_id: int, db: Session = Depends(get_db)):
    classes = db.query(ClassGroup).filter(ClassGroup.institution_id == institution_id).all()
    results = []
    for c in classes:
        divs = db.query(Division).filter(Division.class_group_id == c.id).all()
        results.append({
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "year": c.year,
            "semester": c.semester,
            "department_id": c.department_id,
            "divisions": [{"id": d.id, "name": d.name, "student_count": d.student_count} for d in divs]
        })
    return results


@router.get("/institutions/{institution_id}/divisions")
def list_divisions(institution_id: int, db: Session = Depends(get_db)):
    return db.query(Division).filter(Division.institution_id == institution_id).all()


# Subjects
@router.get("/institutions/{institution_id}/subjects")
def list_subjects(institution_id: int, db: Session = Depends(get_db)):
    return db.query(Subject).filter(Subject.institution_id == institution_id).all()


@router.post("/institutions/{institution_id}/subjects")
def create_subject(institution_id: int, payload: SubjectCreate, db: Session = Depends(get_db)):
    subj = Subject(
        institution_id=institution_id,
        class_group_id=payload.class_group_id,
        department_id=payload.department_id,
        name=payload.name,
        code=payload.code,
        weekly_hours=payload.weekly_hours,
        consecutive_periods=payload.consecutive_periods,
        is_lab=payload.is_lab,
        preferred_room_type=payload.preferred_room_type,
        color_code=payload.color_code
    )
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


# Teachers
@router.get("/institutions/{institution_id}/teachers")
def list_teachers(institution_id: int, db: Session = Depends(get_db)):
    return db.query(Teacher).filter(Teacher.institution_id == institution_id).all()


@router.post("/institutions/{institution_id}/teachers")
def create_teacher(institution_id: int, payload: TeacherCreate, db: Session = Depends(get_db)):
    t = Teacher(
        institution_id=institution_id,
        department_id=payload.department_id,
        name=payload.name,
        code=payload.code,
        email=payload.email,
        designation=payload.designation,
        max_hours_per_day=payload.max_hours_per_day,
        max_hours_per_week=payload.max_hours_per_week,
        competent_subject_ids=payload.competent_subject_ids,
        blackout_slots=payload.blackout_slots,
        preferred_slots=payload.preferred_slots
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


# Rooms
@router.get("/institutions/{institution_id}/rooms")
def list_rooms(institution_id: int, db: Session = Depends(get_db)):
    return db.query(Room).filter(Room.institution_id == institution_id).all()


@router.post("/institutions/{institution_id}/rooms")
def create_room(institution_id: int, payload: RoomCreate, db: Session = Depends(get_db)):
    r = Room(
        institution_id=institution_id,
        name=payload.name,
        code=payload.code,
        room_type=payload.room_type,
        capacity=payload.capacity,
        building=payload.building
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r
