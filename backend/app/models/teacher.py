from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    designation = Column(String(100), default="Professor")
    
    # Workload limits
    max_hours_per_day = Column(Integer, default=5)
    max_hours_per_week = Column(Integer, default=20)
    
    # Subject competencies: list of subject IDs this teacher is qualified to teach
    competent_subject_ids = Column(JSON, default=list)
    
    # Availability:
    # blackout_slots: list of [day_idx, slot_idx] where teacher is unavailable (Hard constraint)
    blackout_slots = Column(JSON, default=list)
    
    # preferred_slots: list of [day_idx, slot_idx] where teacher prefers to teach (Soft constraint reward)
    preferred_slots = Column(JSON, default=list)
    
    color_code = Column(String(20), default="#4f46e5")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
