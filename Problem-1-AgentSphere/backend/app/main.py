from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.agents import router as agents_router
from app.api.routes.posts import router as posts_router
from app.api.routes import comments
from app.api.routes import analytics
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import webhooks
from app.api.routes import simulation


app = FastAPI(
    title=settings.app_name,
    description="Event-driven social network for autonomous AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Agent Network API is running",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(agents_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1", tags=["Comments"])
app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"]
)

app.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Agent Webhooks"]
)

app.include_router(
    simulation.router,
    prefix="/api/v1",
    tags=["Simulation"]
)
