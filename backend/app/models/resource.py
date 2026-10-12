from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    room_type = Column(String(50), default="lecture")  # lecture, lab_computer, lab_science, lab_physics, lab_chemistry, workshop
    capacity = Column(Integer, default=50)
    
    building = Column(String(100), default="Main Wing")
    floor = Column(String(50), default="1st Floor")
    
    equipment_tags = Column(JSON, default=list)  # e.g., ["projector", "computers_40", "chemicals"]
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
