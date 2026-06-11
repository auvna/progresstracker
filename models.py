from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    start_date: date
    goal_date: date


class Milestone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    order: int = 0


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    milestone_id: int = Field(foreign_key="milestone.id")
    title: str
    done: bool = False


class Update(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    note: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    done: bool = False
