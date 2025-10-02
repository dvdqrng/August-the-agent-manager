"""
Task management system for August PM bot
Handles task creation, state transitions, and persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class TaskState(Enum):
    """Task states with display colors"""
    BACKLOG = ("🆕", "BACKLOG", "#6B7280")      # Gray
    PLANNED = ("📋", "PLANNED", "#3B82F6")      # Blue
    IN_PROGRESS = ("🏃", "IN_PROGRESS", "#FBBF24")  # Yellow
    REVIEW = ("👀", "REVIEW", "#F97316")        # Orange
    DONE = ("✅", "DONE", "#10B981")            # Green
    BLOCKED = ("❌", "BLOCKED", "#EF4444")      # Red
    CANCELLED = ("🗑️", "CANCELLED", "#4B5563")  # Dark Gray

    def __init__(self, emoji, name, color):
        self.emoji = emoji
        self.display_name = name
        self.color = color


class TaskPriority(Enum):
    """Task priority levels"""
    P0 = ("🔴", "P0 - Critical")
    P1 = ("🟠", "P1 - High")
    P2 = ("🟡", "P2 - Medium")
    P3 = ("🟢", "P3 - Low")

    def __init__(self, emoji, display_name):
        self.emoji = emoji
        self.display_name = display_name


class Task:
    """Represents a task in the system"""
    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        agent: str,
        state: TaskState = TaskState.BACKLOG,
        priority: TaskPriority = TaskPriority.P2,
        created_at: datetime = None,
        updated_at: datetime = None,
        parent_task: Optional[str] = None,
        tags: List[str] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.agent = agent
        self.state = state
        self.priority = priority
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.parent_task = parent_task
        self.tags = tags or []

    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'agent': self.agent,
            'state': self.state.display_name,
            'priority': self.priority.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parent_task': self.parent_task,
            'tags': self.tags
        }

    def format_display(self) -> str:
        """Format task for Telegram display"""
        lines = [
            f"{self.state.emoji} {self.priority.emoji} **{self.title}**",
            f"Agent: {self.agent}",
            f"Status: {self.state.display_name}",
            f"Priority: {self.priority.display_name}",
        ]

        if self.description:
            lines.append(f"Description: {self.description[:100]}")

        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags)}")

        return "\n".join(lines)


class TaskManager:
    """Manages task persistence and operations"""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                agent TEXT NOT NULL,
                state TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                parent_task TEXT,
                tags TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                field TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_task(
        self,
        title: str,
        description: str,
        agent: str,
        priority: TaskPriority = TaskPriority.P2,
        tags: List[str] = None
    ) -> Task:
        """Create a new task"""
        import uuid
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"

        task = Task(
            id=task_id,
            title=title,
            description=description,
            agent=agent,
            priority=priority,
            tags=tags or []
        )

        self._save_task(task)
        return task

    def _save_task(self, task: Task):
        """Save task to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (id, title, description, agent, state, priority, created_at, updated_at, parent_task, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id,
            task.title,
            task.description,
            task.agent,
            task.state.display_name,
            task.priority.name,
            task.created_at.isoformat(),
            task.updated_at.isoformat(),
            task.parent_task,
            json.dumps(task.tags)
        ))

        conn.commit()
        conn.close()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_task(row)

    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object"""
        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            agent=row[3],
            state=TaskState[row[4]],
            priority=TaskPriority[row[5]],
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
            parent_task=row[8],
            tags=json.loads(row[9]) if row[9] else []
        )

    def update_task_state(self, task_id: str, new_state: TaskState):
        """Update task state and log history"""
        task = self.get_task(task_id)
        if not task:
            return None

        old_state = task.state
        task.state = new_state
        task.updated_at = datetime.now()

        self._save_task(task)
        self._log_history(task_id, "state", old_state.display_name, new_state.display_name)

        return task

    def _log_history(self, task_id: str, field: str, old_value: str, new_value: str):
        """Log task changes to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO task_history (task_id, field, old_value, new_value, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, field, old_value, new_value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_tasks_by_agent(self, agent: str) -> List[Task]:
        """Get all tasks assigned to an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE agent = ? ORDER BY updated_at DESC", (agent,))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def get_tasks_by_state(self, state: TaskState) -> List[Task]:
        """Get all tasks in a specific state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tasks WHERE state = ? ORDER BY priority, updated_at DESC",
            (state.display_name,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def delete_task(self, task_id: str):
        """Delete a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        cursor.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))

        conn.commit()
        conn.close()

    def get_workload_summary(self) -> Dict[str, int]:
        """Get task count per agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent, COUNT(*)
            FROM tasks
            WHERE state NOT IN ('DONE', 'CANCELLED')
            GROUP BY agent
        """)

        results = dict(cursor.fetchall())
        conn.close()

        return results
