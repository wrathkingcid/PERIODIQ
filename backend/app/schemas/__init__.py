from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr


# Auth
class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "INSTITUTION_ADMIN"
    institution_id: Optional[int] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# Institution
class InstitutionCreate(BaseModel):
    name: str
    type: str = "COLLEGE"  # SCHOOL, COLLEGE, COACHING
    code: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    working_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    periods_per_day: int = 7
    period_duration_minutes: int = 50
    day_start_time: str = "08:30"
    breaks: Optional[List[Dict[str, Any]]] = None
    shifts: Optional[List[Dict[str, Any]]] = None

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    working_days: Optional[List[str]] = None
    periods_per_day: Optional[int] = None
    period_duration_minutes: Optional[int] = None
    day_start_time: Optional[str] = None
    breaks: Optional[List[Dict[str, Any]]] = None
    shifts: Optional[List[Dict[str, Any]]] = None
    features: Optional[Dict[str, Any]] = None


# Academic Entities
class SubjectCreate(BaseModel):
    class_group_id: int
    department_id: Optional[int] = None
    name: str
    code: str
    weekly_hours: int = 4
    consecutive_periods: int = 1
    is_lab: bool = False
    preferred_room_type: str = "lecture"
    color_code: Optional[str] = "#6366f1"

class TeacherCreate(BaseModel):
    department_id: Optional[int] = None
    name: str
    code: str
    email: Optional[str] = None
    designation: Optional[str] = "Professor"
    max_hours_per_day: int = 4
    max_hours_per_week: int = 20
    competent_subject_ids: List[int] = []
    blackout_slots: List[List[int]] = []
    preferred_slots: List[List[int]] = []

class RoomCreate(BaseModel):
    name: str
    code: str
    room_type: str = "lecture"
    capacity: int = 50
    building: Optional[str] = "Main"


# Solver Request
class GenerateTimetableRequest(BaseModel):
    scenario_name: str = "Master Optimized Timetable"
    academic_year: str = "2026-2027"
    term: str = "Term 1"
    timeout_seconds: int = 40
    enable_soft_constraints: bool = True
    priority_settings: Optional[Dict[str, Any]] = None  # balance_subjects, reduce_gaps, teacher_prefs

class SwapEntryRequest(BaseModel):
    target_day_index: int
    target_slot_index: int
    target_room_id: Optional[int] = None
    target_teacher_id: Optional[int] = None

class IngestDataRequest(BaseModel):
    subjects: List[Dict[str, Any]]
    teachers: List[Dict[str, Any]]
    rooms: List[Dict[str, Any]]
    classes: Optional[List[Dict[str, Any]]] = None
    divisions: Optional[List[Dict[str, Any]]] = None
