from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import init_db
from app.api import auth, courses, lessons, exercises, projects, dashboard, visual, notifications

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(exercises.router)
app.include_router(projects.router)
app.include_router(dashboard.router)
app.include_router(visual.router)
app.include_router(notifications.router)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}