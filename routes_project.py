import os
from services_db import (
    get_project, create_project, update_project,
    get_milestones, create_milestone, delete_milestone,
    get_tasks, create_task, toggle_task, delete_task,
    get_updates, create_update, get_progress,
    get_logs, create_log, toggle_log, delete_log
)
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_session
from services_db import (
    get_project, create_project, update_project,
    get_milestones, create_milestone, delete_milestone,
    get_tasks, create_task, toggle_task, delete_task,
    get_updates, create_update, get_progress
)
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# ─── Auth ───────────────────────────────────────────────

def check_auth(x_password: str = Header(...)):
    if x_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ─── Request Bodies ─────────────────────────────────────

class ProjectBody(BaseModel):
    name: str
    description: str
    start_date: date
    goal_date: date

class LogBody(BaseModel):
    title: str


class MilestoneBody(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    order: int = 0


class TaskBody(BaseModel):
    milestone_id: int
    title: str


class UpdateBody(BaseModel):
    note: str


# ─── Public Endpoints ───────────────────────────────────

@router.get("/public")
def public_view(session: Session = Depends(get_session)):
    try:
        project = get_project(session)
        if not project:
            return {"setup": False}
        milestones = get_milestones(session)
        result = []
        for m in milestones:
            tasks = get_tasks(session, m.id)
            result.append({
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "due_date": str(m.due_date) if m.due_date else None,
                "tasks": [{"id": t.id, "title": t.title, "done": t.done} for t in tasks]
            })
        updates = get_updates(session)
        progress = get_progress(session)
        return {
            "setup": True,
            "project": project,
            "milestones": result,
            "updates": [{"note": u.note, "created_at": str(u.created_at)} for u in updates],
            "progress": progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Admin Endpoints ────────────────────────────────────

@router.post("/project", dependencies=[Depends(check_auth)])
def setup_project(body: ProjectBody, session: Session = Depends(get_session)):
    try:
        existing = get_project(session)
        if existing:
            return update_project(session, body.name, body.description, body.goal_date)
        return create_project(session, body.name, body.description,
                              body.start_date, body.goal_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/milestone", dependencies=[Depends(check_auth)])
def add_milestone(body: MilestoneBody, session: Session = Depends(get_session)):
    try:
        return create_milestone(session, body.title, body.description,
                                body.due_date, body.order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/milestone/{milestone_id}", dependencies=[Depends(check_auth)])
def remove_milestone(milestone_id: int, session: Session = Depends(get_session)):
    try:
        delete_milestone(session, milestone_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task", dependencies=[Depends(check_auth)])
def add_task(body: TaskBody, session: Session = Depends(get_session)):
    try:
        return create_task(session, body.milestone_id, body.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/task/{task_id}", dependencies=[Depends(check_auth)])
def complete_task(task_id: int, session: Session = Depends(get_session)):
    try:
        return toggle_task(session, task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}", dependencies=[Depends(check_auth)])
def remove_task(task_id: int, session: Session = Depends(get_session)):
    try:
        delete_task(session, task_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", dependencies=[Depends(check_auth)])
def post_update(body: UpdateBody, session: Session = Depends(get_session)):
    try:
        return create_update(session, body.note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Log Endpoints ──────────────────────────────────────

@router.get("/log")
def get_log_entries(session: Session = Depends(get_session)):
    try:
        logs = get_logs(session)
        return [{"id": l.id, "title": l.title, "done": l.done} for l in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/log")
def add_log_entry(body: LogBody, session: Session = Depends(get_session)):
    try:
        return create_log(session, body.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/log/{log_id}")
def toggle_log_entry(log_id: int, session: Session = Depends(get_session)):
    try:
        return toggle_log(session, log_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/log/{log_id}")
def delete_log_entry(log_id: int, session: Session = Depends(get_session)):
    try:
        delete_log(session, log_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))