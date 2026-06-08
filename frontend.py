import streamlit as st
import requests

API = "https://web-production-710c4.up.railway.app/api/project"

st.set_page_config(page_title="Progress Tracker", layout="wide")


# ─── Helpers ────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API}/{path}")
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path, body, password):
    try:
        r = requests.post(
            f"{API}/{path}",
            json=body,
            headers={"x-password": password}
        )
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_patch(path, password):
    try:
        r = requests.patch(
            f"{API}/{path}",
            headers={"x-password": password}
        )
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_delete(path, password):
    try:
        r = requests.delete(
            f"{API}/{path}",
            headers={"x-password": password}
        )
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ─── Public View ────────────────────────────────────────

def public_view():
    data = api_get("public")

    if not data or not data.get("setup"):
        st.title("Progress Tracker")
        st.info("No project set up yet. Check back soon.")
        return

    project = data["project"]
    progress = data["progress"]
    milestones = data["milestones"]
    updates = data["updates"]

    st.title(project["name"])
    st.caption(project["description"])
    st.caption(f"Started: {project['start_date']}  ·  Goal: {project['goal_date']}")

    st.markdown("---")

    # Progress bar
    pct = progress["percentage"]
    st.subheader(f"Overall Progress — {pct}%")
    st.progress(pct / 100)
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks Done", f"{progress['completedTasks']} / {progress['totalTasks']}")
    col2.metric("Milestones", progress["totalMilestones"])
    col3.metric("Completion", f"{pct}%")

    st.markdown("---")

    # Milestones
    st.subheader("Milestones")
    for m in milestones:
        tasks = m["tasks"]
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        with st.expander(f"{m['title']}  ({done}/{total} tasks)", expanded=True):
            if m.get("description"):
                st.caption(m["description"])
            if m.get("due_date"):
                st.caption(f"Due: {m['due_date']}")
            for t in tasks:
                icon = "✅" if t["done"] else "⬜"
                st.write(f"{icon} {t['title']}")

    st.markdown("---")

    # Updates
    st.subheader("Progress Updates")
    if not updates:
        st.caption("No updates posted yet.")
    for u in updates:
        st.markdown(f"**{u['created_at'][:10]}** — {u['note']}")


# ─── Admin View ─────────────────────────────────────────

def admin_view(password):

    st.subheader("Project Setup")
    with st.form("project_form"):
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        start_date = st.date_input("Start Date")
        goal_date = st.date_input("Goal Date")
        if st.form_submit_button("Save Project"):
            result = api_post("project", {
                "name": name,
                "description": description,
                "start_date": str(start_date),
                "goal_date": str(goal_date)
            }, password)
            if result:
                st.success("Project saved.")

    st.markdown("---")
    st.subheader("Add Milestone")
    with st.form("milestone_form"):
        title = st.text_input("Title")
        desc = st.text_area("Description (optional)")
        due = st.date_input("Due Date (optional)")
        order = st.number_input("Order", min_value=0, value=0)
        if st.form_submit_button("Add Milestone"):
            result = api_post("milestone", {
                "title": title,
                "description": desc,
                "due_date": str(due),
                "order": order
            }, password)
            if result:
                st.success("Milestone added.")
                st.rerun()

    st.markdown("---")
    st.subheader("Add Task")

    data = api_get("public")
    milestones = data.get("milestones", []) if data and data.get("setup") else []

    if not milestones:
        st.caption("Add a milestone first.")
    else:
        with st.form("task_form"):
            milestone_options = {m["title"]: m["id"] for m in milestones}
            chosen = st.selectbox("Milestone", list(milestone_options.keys()))
            task_title = st.text_input("Task Title")
            if st.form_submit_button("Add Task"):
                result = api_post("task", {
                    "milestone_id": milestone_options[chosen],
                    "title": task_title
                }, password)
                if result:
                    st.success("Task added.")
                    st.rerun()

        st.markdown("---")
        st.subheader("Manage Tasks")
        for m in milestones:
            st.markdown(f"**{m['title']}**")
            for t in m["tasks"]:
                col1, col2 = st.columns([6, 1])
                icon = "✅" if t["done"] else "⬜"
                col1.write(f"{icon} {t['title']}")
                if col2.button("Toggle", key=f"toggle_{t['id']}"):
                    api_patch(f"task/{t['id']}", password)
                    st.rerun()

    st.markdown("---")
    st.subheader("Post Update")
    with st.form("update_form"):
        note = st.text_area("What did you get done?")
        if st.form_submit_button("Post Update"):
            result = api_post("update", {"note": note}, password)
            if result:
                st.success("Update posted.")
                st.rerun()


# ─── App Entry Point ────────────────────────────────────

def main():
    st.sidebar.title("Navigation")
    view = st.sidebar.radio("View", ["Public", "Admin"])

    if view == "Public":
        public_view()

    elif view == "Admin":
        st.sidebar.markdown("---")
        password = st.sidebar.text_input("Password", type="password")
        if not password:
            st.warning("Enter your password in the sidebar to access the admin panel.")
            return
        admin_view(password)


main()