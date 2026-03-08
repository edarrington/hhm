"""Todoist API integration for household task management.

Provides client for Todoist API with household-level access.
"""

from __future__ import annotations

from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)


class TodoistClient:
    """Todoist API client for household task management."""

    API_BASE = "https://api.todoist.com/rest/v2"

    def __init__(self, api_token: str):
        """Initialize Todoist client.
        
        Args:
            api_token: Todoist API token
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    async def list_projects(self) -> list[dict]:
        """List all household Todoist projects.
        
        Returns:
            List of project objects
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE}/projects",
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to list Todoist projects: {e}")
            return []

    async def list_tasks(
        self,
        project_id: Optional[str] = None,
        filter_query: Optional[str] = None,
    ) -> list[dict]:
        """List household tasks.
        
        Args:
            project_id: Filter by project ID
            filter_query: Todoist filter query (e.g., "@today", "@high")
            
        Returns:
            List of task objects
        """
        try:
            params = {}
            if project_id:
                params["project_id"] = project_id
            if filter_query:
                params["filter"] = filter_query
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE}/tasks",
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to list Todoist tasks: {e}")
            return []

    async def create_task(
        self,
        content: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: int = 1,
        labels: Optional[list[str]] = None,
    ) -> Optional[dict]:
        """Create a household task.
        
        Args:
            content: Task title
            project_id: Project to add to
            description: Task description
            due_date: Due date (RFC 3339 or YYYY-MM-DD)
            priority: Priority 1-4 (4=highest)
            labels: List of label names
            
        Returns:
            Created task object or None on error
        """
        try:
            task_data = {
                "content": content,
                "priority": priority,
            }
            
            if project_id:
                task_data["project_id"] = project_id
            if description:
                task_data["description"] = description
            if due_date:
                task_data["due_string"] = due_date
            if labels:
                task_data["labels"] = labels
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/tasks",
                    headers=self.headers,
                    json=task_data,
                )
                response.raise_for_status()
                created_task = response.json()
                logger.info(f"Created task: {content}")
                return created_task
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    async def update_task(
        self,
        task_id: str,
        **kwargs,
    ) -> Optional[dict]:
        """Update a household task.
        
        Args:
            task_id: Task ID to update
            **kwargs: Fields to update (content, due_date, priority, etc)
            
        Returns:
            Updated task or None on error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/tasks/{task_id}",
                    headers=self.headers,
                    json=kwargs,
                )
                response.raise_for_status()
                logger.info(f"Updated task {task_id}")
                return response.json()
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return None

    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete.
        
        Args:
            task_id: Task ID to complete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/tasks/{task_id}/close",
                    headers=self.headers,
                )
                response.raise_for_status()
                logger.info(f"Completed task {task_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            return False

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.API_BASE}/tasks/{task_id}",
                    headers=self.headers,
                )
                response.raise_for_status()
                logger.info(f"Deleted task {task_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    async def create_project(
        self,
        name: str,
        color: Optional[str] = None,
    ) -> Optional[dict]:
        """Create a household project.
        
        Args:
            name: Project name
            color: Color name (e.g., "blue", "red")
            
        Returns:
            Created project or None on error
        """
        try:
            project_data = {"name": name}
            if color:
                project_data["color"] = color
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/projects",
                    headers=self.headers,
                    json=project_data,
                )
                response.raise_for_status()
                created_project = response.json()
                logger.info(f"Created project: {name}")
                return created_project
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return None
