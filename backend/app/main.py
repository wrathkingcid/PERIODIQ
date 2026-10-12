from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # import all models
from app.services.sample_data_loader import SampleDataLoader
from app.api.v1.auth import router as auth_router
from app.api.v1.institutions import router as institutions_router
from app.api.v1.academic import router as academic_router
from app.api.v1.shift_planner import router as shifts_router
from app.api.v1.upload import router as upload_router
from app.api.v1.timetables import router as timetables_router
from app.api.v1.analytics import router as analytics_router

# Initialize tables
Base.metadata.create_all(bind=engine)

# Auto seed default samples if empty
try:
    with SessionLocal() as db:
        SampleDataLoader.load_all_samples(db)
except Exception as e:
    print(f"Sample auto-load notification: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Universal Automatic Timetable Generator and Optimization Engine powered by Google OR-Tools CP-SAT for Schools, Colleges, and Coaching Institutes."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for seamless local dev & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(institutions_router, prefix=settings.API_V1_STR)
app.include_router(academic_router, prefix=settings.API_V1_STR)
app.include_router(shifts_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
app.include_router(timetables_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "OR-Tools CP-SAT Ready"}
