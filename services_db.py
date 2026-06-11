from datetime import date
from sqlmodel import Session, select
from models import Project, Milestone, Task, Update
from models import Project, Milestone, Task, Update, Log


# ─── Project ────────────────────────────────────────────

def get_project(session: Session):
    return session.exec(select(Project)).first()


def create_project(session: Session, name: str, description: str,
                   start_date: date, goal_date: date) -> Project:
    project = Project(
        name=name,
        description=description,
        start_date=start_date,
        goal_date=goal_date
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_project(session: Session, name: str, description: str,
                   goal_date: date) -> Project:
    project = get_project(session)
    project.name = name
    project.description = description
    project.goal_date = goal_date
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


# ─── Milestones ─────────────────────────────────────────

def get_milestones(session: Session) -> list:
    return session.exec(select(Milestone).order_by(Milestone.order)).all()


def create_milestone(session: Session, title: str, description: str,
                     due_date: date, order: int) -> Milestone:
    milestone = Milestone(
        title=title,
        description=description,
        due_date=due_date,
        order=order
    )
    session.add(milestone)
    session.commit()
    session.refresh(milestone)
    return milestone


def delete_milestone(session: Session, milestone_id: int):
    milestone = session.get(Milestone, milestone_id)
    if not milestone:
        raise ValueError(f"Milestone {milestone_id} not found.")
    session.delete(milestone)
    session.commit()


# ─── Tasks ──────────────────────────────────────────────

def get_tasks(session: Session, milestone_id: int) -> list:
    return session.exec(
        select(Task).where(Task.milestone_id == milestone_id)
    ).all()


def create_task(session: Session, milestone_id: int, title: str) -> Task:
    task = Task(milestone_id=milestone_id, title=title)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def toggle_task(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found.")
    task.done = not task.done
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found.")
    session.delete(task)
    session.commit()


# ─── Updates ────────────────────────────────────────────

def get_updates(session: Session) -> list:
    return session.exec(
        select(Update).order_by(Update.created_at.desc())
    ).all()


def create_update(session: Session, note: str) -> Update:
    update = Update(note=note)
    session.add(update)
    session.commit()
    session.refresh(update)
    return update


# ─── Progress ───────────────────────────────────────────

def get_progress(session: Session) -> dict:
    milestones = get_milestones(session)
    all_tasks = session.exec(select(Task)).all()
    completed = [t for t in all_tasks if t.done]

    total = len(all_tasks)
    percentage = round((len(completed) / total) * 100) if total > 0 else 0

    return {
        "totalTasks": total,
        "completedTasks": len(completed),
        "percentage": percentage,
        "totalMilestones": len(milestones),
    }

# ─── Log ────────────────────────────────────────────────

def get_logs(session: Session) -> list:
    return session.exec(select(Log)).all()


def create_log(session: Session, title: str) -> Log:
    log = Log(title=title)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def toggle_log(session: Session, log_id: int) -> Log:
    log = session.get(Log, log_id)
    if not log:
        raise ValueError(f"Log {log_id} not found.")
    log.done = not log.done
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def delete_log(session: Session, log_id: int):
    log = session.get(Log, log_id)
    if not log:
        raise ValueError(f"Log {log_id} not found.")
    session.delete(log)
    session.commit()