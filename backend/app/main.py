from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import init_db
from app.api import auth, courses, lessons, exercises, projects, dashboard, visual, notifications, users, cody, admin, feedback, duels, orientini, circuits, git_quest

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

@app.middleware("http")
async def add_security_headers(request, call_next):
    """Baseline hardening headers for the JSON API.

    CSP is deliberately not set here -- this API never serves HTML, so a
    content policy belongs on the CloudFront distribution in front of the
    frontend SPA instead (see deploy/aws/README.md).
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not settings.debug:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(courses.sections_router)
app.include_router(lessons.router)
app.include_router(exercises.router)
app.include_router(projects.router)
app.include_router(dashboard.router)
app.include_router(visual.router)
app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(cody.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.include_router(duels.router)
app.include_router(orientini.router)
app.include_router(circuits.router)
app.include_router(git_quest.router)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}