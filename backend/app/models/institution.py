from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime
from datetime import datetime, timezone
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, default="COLLEGE")  # SCHOOL, COLLEGE, UNIVERSITY, COACHING
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    # Scheduling configuration defaults
    working_days = Column(JSON, default=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    periods_per_day = Column(Integer, default=7)
    period_duration_minutes = Column(Integer, default=50)
    day_start_time = Column(String(10), default="08:30")
    
    # Breaks config: list of dicts [{"name": "Recess", "after_period": 2, "duration": 15}, {"name": "Lunch", "after_period": 4, "duration": 45}]
    breaks = Column(JSON, default=lambda: [
        {"name": "Short Break", "after_period": 2, "duration_minutes": 15},
        {"name": "Lunch Break", "after_period": 4, "duration_minutes": 45}
    ])
    
    # Shifts config: list of dicts [{"name": "General Shift", "start_time": "08:30", "end_time": "15:30", "periods": 7}]
    shifts = Column(JSON, default=lambda: [
        {"name": "Morning Shift", "start_time": "08:30", "end_time": "15:00", "periods": 7}
    ])
    
    # Active feature toggles
    features = Column(JSON, default=lambda: {
        "laboratories": True,
        "multiple_shifts": False,
        "electives": True,
        "batches": True,
        "smart_break_balancing": True
    })

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
