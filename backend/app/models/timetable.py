from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database import Base


class TimetableScenario(Base):
    __tablename__ = "timetable_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    academic_year = Column(String(50), default="2026-2027")
    term = Column(String(50), default="Semester 1")
    
    # Status: DRAFT, GENERATING, OPTIMAL, FEASIBLE, INFEASIBLE, APPROVED, PUBLISHED
    status = Column(String(50), default="DRAFT", index=True)
    solver_status = Column(String(50), default="UNKNOWN")
    solver_time_seconds = Column(Float, default=0.0)
    
    # Quality & Analytics Score (0 - 100)
    quality_score = Column(Float, default=0.0)
    metrics = Column(JSON, default=lambda: {
        "teacher_idle_gaps": 0,
        "student_idle_gaps": 0,
        "room_utilization_pct": 0.0,
        "subject_balance_score": 0.0,
        "teacher_preference_satisfaction_pct": 0.0
    })
    
    # Infeasibility diagnostics & recommendations if constraints could not be met
    infeasibility_report = Column(JSON, nullable=True)
    
    # Snapshot of parameters applied during solve
    solver_parameters = Column(JSON, default=dict)
    
    version = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("timetable_scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    
    day_index = Column(Integer, nullable=False)  # 0 = Day 1 (e.g. Monday), 1 = Day 2, etc.
    day_name = Column(String(20), nullable=False)
    slot_index = Column(Integer, nullable=False)  # 0 = Period 1, 1 = Period 2, etc.
    slot_label = Column(String(50), nullable=True)  # e.g., "08:30 - 09:20"
    shift_name = Column(String(50), default="General Shift")
    
    # Academic targets
    class_group_id = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    division_id = Column(Integer, ForeignKey("divisions.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Assignments
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Locking & Manual override: pinned cells survive re-generation
    is_locked = Column(Boolean, default=False)
    is_manual_override = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
