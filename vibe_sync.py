"""
Vibe Kanban integration for August
Syncs tasks and agents between August and Vibe Kanban
"""

import requests
import json
from typing import List, Dict, Optional
from task_manager import TaskManager, TaskState, TaskPriority
from agents import get_all_agents, get_agent

# Vibe Kanban configuration
VIBE_BASE_URL = "http://127.0.0.1:52822/api"
VIBE_PROJECT_ID = "04818b0a-f69b-42c0-858a-4c9132723523"  # Lovemail project


class VibeKanbanClient:
    """Client for interacting with Vibe Kanban API"""

    def __init__(self, base_url: str = VIBE_BASE_URL, project_id: str = VIBE_PROJECT_ID):
        self.base_url = base_url
        self.project_id = project_id

    def get_projects(self) -> List[Dict]:
        """Get all projects from Vibe"""
        try:
            response = requests.get(f"{self.base_url}/projects", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
            return []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def get_tasks(self) -> List[Dict]:
        """Get all tasks for the Lovemail project"""
        try:
            # Try with project_id parameter (this is the correct way)
            response = requests.get(
                f"{self.base_url}/tasks",
                params={"project_id": self.project_id},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get("success"):
                    return data.get("data", [])
                elif isinstance(data, list):
                    return data

            return []
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def get_agents(self) -> List[Dict]:
        """Get all agents from Vibe"""
        try:
            endpoints = [
                f"{self.base_url}/agents",
                f"{self.base_url}/projects/{self.project_id}/agents",
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and data.get("success"):
                            return data.get("data", [])
                        elif isinstance(data, list):
                            return data
                except:
                    continue

            return []
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []

    def create_task(self, task_data: Dict) -> Optional[Dict]:
        """Create a task in Vibe"""
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                json=task_data,
                timeout=5
            )
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating task: {e}")
            return None

    def update_task(self, task_id: str, task_data: Dict) -> Optional[Dict]:
        """Update a task in Vibe"""
        try:
            response = requests.put(
                f"{self.base_url}/tasks/{task_id}",
                json=task_data,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error updating task: {e}")
            return None


class VibeAugustSync:
    """Syncs tasks and agents between Vibe and August"""

    def __init__(self, task_manager: TaskManager):
        self.vibe = VibeKanbanClient()
        self.task_manager = task_manager
        self.state_mapping = self._create_state_mapping()

    def _create_state_mapping(self) -> Dict[str, TaskState]:
        """Map Vibe columns to August states"""
        return {
            "backlog": TaskState.BACKLOG,
            "todo": TaskState.PLANNED,
            "in_progress": TaskState.IN_PROGRESS,
            "in progress": TaskState.IN_PROGRESS,
            "review": TaskState.REVIEW,
            "done": TaskState.DONE,
            "blocked": TaskState.BLOCKED,
            "cancelled": TaskState.CANCELLED,
        }

    def sync_from_vibe(self) -> Dict[str, int]:
        """Sync tasks from Vibe to August"""
        stats = {
            "fetched": 0,
            "created": 0,
            "skipped": 0,
            "errors": 0
        }

        try:
            vibe_tasks = self.vibe.get_tasks()
            stats["fetched"] = len(vibe_tasks)

            # Map Vibe agents to August agents
            agent_map = {
                "CODEX": "engineer",
                "Shield": "qa",
                "Swift": "engineer",
                "Docs": "docs",
            }

            for vibe_task in vibe_tasks:
                try:
                    title = vibe_task.get("title", "Untitled")
                    description = vibe_task.get("description", "")
                    vibe_status = vibe_task.get("status", "backlog")
                    vibe_executor = vibe_task.get("executor", "CODEX")

                    # Map status to August state
                    status_mapping = {
                        "backlog": TaskState.BACKLOG,
                        "todo": TaskState.PLANNED,
                        "inprogress": TaskState.IN_PROGRESS,
                        "inreview": TaskState.REVIEW,
                        "done": TaskState.DONE,
                        "blocked": TaskState.BLOCKED,
                    }

                    august_state = status_mapping.get(vibe_status.lower(), TaskState.BACKLOG)
                    august_agent = agent_map.get(vibe_executor, "engineer")

                    # Check if task already exists by title (simple dedup)
                    existing_tasks = self.task_manager.get_all_tasks()
                    if any(t.title == title for t in existing_tasks):
                        stats["skipped"] += 1
                        continue

                    # Create task in August
                    task = self.task_manager.create_task(
                        title=title,
                        description=description,
                        agent=august_agent,
                        priority=TaskPriority.P2,  # Default to P2
                    )

                    # Update state if not backlog
                    if august_state != TaskState.BACKLOG:
                        self.task_manager.update_task_state(task.id, august_state)

                    stats["created"] += 1

                except Exception as e:
                    print(f"Error syncing task {vibe_task.get('title')}: {e}")
                    stats["errors"] += 1

        except Exception as e:
            print(f"Sync error: {e}")
            stats["errors"] += 1

        return stats

    def sync_to_vibe(self) -> Dict[str, int]:
        """Sync tasks from August to Vibe"""
        stats = {
            "fetched": 0,
            "pushed": 0,
            "errors": 0
        }

        try:
            august_tasks = self.task_manager.get_all_tasks()
            stats["fetched"] = len(august_tasks)

            for task in august_tasks:
                try:
                    # Convert August task to Vibe format
                    vibe_task = {
                        "title": task.title,
                        "description": task.description,
                        "agent": task.agent,
                        "status": task.state.display_name.lower(),
                        "priority": task.priority.name,
                    }

                    # Try to create in Vibe
                    result = self.vibe.create_task(vibe_task)
                    if result:
                        stats["pushed"] += 1
                except Exception as e:
                    print(f"Error pushing task: {e}")
                    stats["errors"] += 1

        except Exception as e:
            print(f"Push error: {e}")
            stats["errors"] += 1

        return stats

    def get_sync_status(self) -> Dict:
        """Get sync status and health"""
        try:
            projects = self.vibe.get_projects()
            vibe_tasks = self.vibe.get_tasks()
            august_tasks = self.task_manager.get_all_tasks()

            return {
                "vibe_online": len(projects) > 0,
                "vibe_tasks": len(vibe_tasks),
                "august_tasks": len(august_tasks),
                "projects": projects,
            }
        except Exception as e:
            return {
                "vibe_online": False,
                "error": str(e)
            }


def test_vibe_connection():
    """Test if Vibe Kanban is accessible"""
    client = VibeKanbanClient()
    projects = client.get_projects()

    if projects:
        print("✅ Vibe Kanban is online!")
        print(f"   Found {len(projects)} projects:")
        for proj in projects:
            print(f"   - {proj['name']} ({proj['git_repo_path']})")
        return True
    else:
        print("❌ Cannot connect to Vibe Kanban")
        print("   Make sure Vibe is running on http://127.0.0.1:52822")
        return False


if __name__ == "__main__":
    # Test the connection
    test_vibe_connection()
