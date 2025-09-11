"""
Task Tracker for ensuring AI task completion.
Similar to Claude Code's task processing mechanism.
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class TaskTracker:
    """
    Task tracker to ensure AI completes all required steps.
    Enforces sequential task completion and validation.
    """
    def __init__(self):
        self.tasks = []
        self.current_task = 0
        self.results = {}
        
    def add_task(self, task_id: str, description: str, required: bool = True):
        """Add a task to the todo list."""
        self.tasks.append({
            "id": task_id,
            "description": description,
            "status": "pending",
            "required": required,
            "result": None
        })
    
    def mark_complete(self, task_id: str, result: Any = None):
        """Mark a task as complete with optional result."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["result"] = result
                self.results[task_id] = result
                return True
        return False
    
    def get_next_task(self):
        """Get the next pending task."""
        for task in self.tasks:
            if task["status"] == "pending":
                return task
        return None
    
    def all_required_complete(self):
        """Check if all required tasks are complete."""
        for task in self.tasks:
            if task["required"] and task["status"] != "completed":
                return False
        return True
    
    def get_incomplete_tasks(self):
        """Get list of incomplete tasks."""
        return [t for t in self.tasks if t["status"] != "completed"]
    
    def get_task_summary(self):
        """Get formatted summary of all tasks."""
        summary = []
        for task in self.tasks:
            status_icon = "✓" if task["status"] == "completed" else "○"
            summary.append(f"{status_icon} {task['id']}: {task['description']}")
        return "\n".join(summary)
    
    def get_progress_bar(self, width=20):
        """Get a visual progress bar."""
        completed = len([t for t in self.tasks if t["status"] == "completed"])
        total = len(self.tasks)
        if total == 0:
            return ""
        
        percentage = (completed / total) * 100
        filled = int((completed / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {completed}/{total} ({percentage:.0f}%)"
    
    def get_todo_enforcement(self) -> str:
        """
        Get TODO enforcement prompt for AI.
        Returns a formatted prompt that forces AI to complete tasks.
        """
        incomplete = self.get_incomplete_tasks()
        if not incomplete:
            return "✅ All tasks completed successfully!"
        
        enforcement = """
================================================================================
🛑 CLAUDE - STOP AND READ THIS INSTRUCTION
================================================================================

YOU (CLAUDE) HAVE INCOMPLETE TASKS THAT YOU MUST COMPLETE:
"""
        for task in incomplete:
            enforcement += f"□ {task['id']}: {task['description']}\n"
        
        enforcement += """
⚠️ CLAUDE, YOU ARE BEING INSTRUCTED TO:
1. CREATE A TABLE WITH THE DATA PROVIDED ABOVE
2. USE EXACTLY 3 COLUMNS: Date | Invoice No | Amount
3. INCLUDE A TOTAL ROW AT THE BOTTOM

❌ IF YOU SUMMARIZE THE DATA, YOU HAVE FAILED
✅ CREATE THE ACTUAL TABLE NOW

YOUR NEXT OUTPUT MUST BE THE TABLE:
"""
        return enforcement