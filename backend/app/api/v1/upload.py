from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.institution import Institution
from app.models.academic import ClassGroup, Division
from app.models.curriculum import Subject
from app.models.teacher import Teacher
from app.models.resource import Room
from app.services.document_parser import DocumentParser
from app.schemas import IngestDataRequest

router = APIRouter(prefix="/upload", tags=["Data Ingestion & Review"])


@router.post("/institutions/{institution_id}/parse-file")
async def parse_uploaded_file(
    institution_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    content_bytes = await file.read()
    try:
        extracted = DocumentParser.parse_file(file.filename, content_bytes)
        return {
            "filename": file.filename,
            "file_size_bytes": len(content_bytes),
            "extracted": extracted
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")


@router.post("/institutions/{institution_id}/commit-ingest")
def commit_ingest_data(
    institution_id: int,
    payload: IngestDataRequest,
    db: Session = Depends(get_db)
):
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    # 1. Classes & Divisions
    created_classes = {}
    if payload.classes:
        for c_data in payload.classes:
            cg = ClassGroup(
                institution_id=institution_id,
                name=c_data.get("name", "Cohort Year 1"),
                code=c_data.get("code", "Y1")
            )
            db.add(cg)
            db.flush()
            created_classes[c_data.get("name")] = cg.id

    # Fallback class if none
    default_cg_id = list(created_classes.values())[0] if created_classes else None
    if not default_cg_id:
        existing_cg = db.query(ClassGroup).filter(ClassGroup.institution_id == institution_id).first()
        if existing_cg:
            default_cg_id = existing_cg.id
        else:
            cg = ClassGroup(institution_id=institution_id, name="Cohort 1", code="C1")
            db.add(cg)
            db.flush()
            default_cg_id = cg.id

    if payload.divisions:
        for d_data in payload.divisions:
            div = Division(
                institution_id=institution_id,
                class_group_id=default_cg_id,
                name=d_data.get("name", "Section A"),
                student_count=int(d_data.get("student_count", 40))
            )
            db.add(div)
            db.flush()

    # 2. Rooms
    for r_data in payload.rooms:
        r = Room(
            institution_id=institution_id,
            name=r_data.get("name"),
            code=r_data.get("code", r_data.get("name").replace(" ", "-")),
            room_type=r_data.get("room_type", "lecture"),
            capacity=int(r_data.get("capacity", 50))
        )
        db.add(r)
    db.flush()

    # 3. Subjects
    created_subjects = []
    for s_data in payload.subjects:
        s = Subject(
            institution_id=institution_id,
            class_group_id=default_cg_id,
            name=s_data.get("name"),
            code=s_data.get("code", s_data.get("name")[:6].upper()),
            weekly_hours=int(s_data.get("weekly_hours", 4)),
            consecutive_periods=int(s_data.get("consecutive_periods", 1)),
            is_lab=bool(s_data.get("is_lab", False)),
            preferred_room_type=s_data.get("preferred_room_type", "lecture")
        )
        db.add(s)
        created_subjects.append(s)
    db.flush()

    # 4. Teachers
    sub_ids = [s.id for s in created_subjects]
    for t_data in payload.teachers:
        t = Teacher(
            institution_id=institution_id,
            name=t_data.get("name"),
            code=t_data.get("code", t_data.get("name")[:4].upper()),
            email=t_data.get("email", ""),
            max_hours_per_week=int(t_data.get("max_hours_per_week", 20)),
            max_hours_per_day=int(t_data.get("max_hours_per_day", 4)),
            competent_subject_ids=t_data.get("competent_subject_ids", sub_ids)
        )
        db.add(t)

    db.commit()
    return {"message": "Data committed successfully to institutional catalog!"}
