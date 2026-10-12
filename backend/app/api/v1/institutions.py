from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.institution import Institution
from app.schemas import InstitutionCreate, InstitutionUpdate
from app.services.sample_data_loader import SampleDataLoader

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.get("/")
def list_institutions(db: Session = Depends(get_db)):
    institutions = db.query(Institution).all()
    # If no institutions yet, auto seed the 3 rich samples!
    if not institutions:
        SampleDataLoader.load_all_samples(db)
        institutions = db.query(Institution).all()
    return institutions


@router.post("/")
def create_institution(payload: InstitutionCreate, db: Session = Depends(get_db)):
    existing = db.query(Institution).filter(Institution.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Institution code already exists")

    inst = Institution(
        name=payload.name,
        type=payload.type,
        code=payload.code,
        description=payload.description,
        contact_email=payload.contact_email,
        working_days=payload.working_days,
        periods_per_day=payload.periods_per_day,
        period_duration_minutes=payload.period_duration_minutes,
        day_start_time=payload.day_start_time,
        breaks=payload.breaks or [
            {"name": "Recess", "after_period": 2, "duration_minutes": 15},
            {"name": "Lunch", "after_period": 4, "duration_minutes": 45}
        ],
        shifts=payload.shifts or [
            {"name": "General Shift", "start_time": payload.day_start_time, "end_time": "15:30", "periods": payload.periods_per_day}
        ]
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


@router.get("/{id}")
def get_institution(id: int, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst


@router.put("/{id}")
def update_institution(id: int, payload: InstitutionUpdate, db: Session = Depends(get_db)):
    inst = db.query(Institution).filter(Institution.id == id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    if payload.name is not None:
        inst.name = payload.name
    if payload.working_days is not None:
        inst.working_days = payload.working_days
    if payload.periods_per_day is not None:
        inst.periods_per_day = payload.periods_per_day
    if payload.period_duration_minutes is not None:
        inst.period_duration_minutes = payload.period_duration_minutes
    if payload.day_start_time is not None:
        inst.day_start_time = payload.day_start_time
    if payload.breaks is not None:
        inst.breaks = payload.breaks
    if payload.shifts is not None:
        inst.shifts = payload.shifts
    if payload.features is not None:
        inst.features = payload.features

    db.commit()
    db.refresh(inst)
    return inst


@router.post("/{id}/seed-samples")
def seed_sample(id: int, sample_type: str = "ALL", db: Session = Depends(get_db)):
    if sample_type == "SCHOOL":
        SampleDataLoader.load_school(db)
    elif sample_type == "COLLEGE":
        SampleDataLoader.load_engineering_college(db)
    elif sample_type == "COACHING":
        SampleDataLoader.load_coaching_institute(db)
    else:
        SampleDataLoader.load_all_samples(db)
    return {"message": f"Sample data loaded successfully for {sample_type}"}
