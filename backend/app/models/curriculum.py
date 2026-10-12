from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    class_group_id = Column(Integer, ForeignKey("class_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    
    # Weekly scheduling demands
    weekly_hours = Column(Integer, nullable=False, default=4)
    consecutive_periods = Column(Integer, default=1)  # 1 for standard periods, 2 or 3 for lab sessions
    
    # Subject characteristics
    is_lab = Column(Boolean, default=False)
    is_elective = Column(Boolean, default=False)
    requires_batches = Column(Boolean, default=False)  # If true, runs for practical batches concurrently or in rotation
    credit_hours = Column(Float, default=3.0)
    
    preferred_room_type = Column(String(50), default="lecture")  # lecture, lab_computer, lab_science, lab_physics, workshop
    color_code = Column(String(20), default="#6366f1")  # Hex color for UI schedule visualization
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
