from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes_project import router as project_router
from database import create_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Progress Tracker", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["progresstracker-7lpvfkjrcsinxvytwpadgq.streamlit.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project_router, prefix="/api/project")


@app.get("/health")
def health():
    return {"status": "ok"}