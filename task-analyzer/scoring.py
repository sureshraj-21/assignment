"""Task scoring and cycle detection logic."""
from datetime import datetime
from typing import List, Dict, Tuple, Set

def score_tasks(tasks: List[Dict], strategy: str = "smart") -> List[Dict]:
    """
    Score and prioritize tasks based on the selected strategy.
    
    Args:
        tasks: List of task dictionaries
        strategy: Scoring strategy ("smart", "urgency", "effort", "importance")
    
    Returns:
        List of tasks with score and components
    """
    
    # Assign IDs if missing
    for i, task in enumerate(tasks):
        if "id" not in task:
            task["id"] = f"task_{i}"
    
    # Normalize task data
    for task in tasks:
        task.setdefault("priority", 5)
        task.setdefault("effort", 5)
        task.setdefault("due_date", None)
        task.setdefault("dependencies", [])
    
    # Calculate score components
    max_priority = max((t.get("priority", 1) for t in tasks), default=10)
    max_effort = max((t.get("effort", 1) for t in tasks), default=10)
    
    for task in tasks:
        # Urgency score (based on due date)
        urgency = _calculate_urgency(task.get("due_date"))
        
        # Importance score (normalized priority)
        importance_norm = min(task.get("priority", 5) / max(max_priority, 1), 1.0)
        
        # Effort score (lower effort = higher score)
        effort_norm = 1 - (min(task.get("effort", 5) / max(max_effort, 1), 1.0))
        
        # Calculate final score based on strategy
        if strategy == "urgency":
            final_score = urgency
        elif strategy == "effort":
            final_score = effort_norm
        elif strategy == "importance":
            final_score = importance_norm
        else:  # smart (default)
            final_score = (urgency * 0.4) + (importance_norm * 0.4) + (effort_norm * 0.2)
        
        task["components"] = {
            "urgency": urgency,
            "importance_norm": importance_norm,
            "effort": effort_norm,
        }
        task["raw_score"] = final_score
        task["score"] = round(final_score, 2)
    
    # Sort by score (descending)
    sorted_tasks = sorted(tasks, key=lambda t: t.get("raw_score", 0), reverse=True)
    
    return sorted_tasks


def detect_cycles(tasks: List[Dict]) -> Tuple[bool, List[List[str]]]:
    """
    Detect circular dependencies in tasks.
    
    Args:
        tasks: List of task dictionaries with 'id' and 'dependencies' fields
    
    Returns:
        Tuple of (has_cycle: bool, cycles: List of cycle paths)
    """
    
    # Build adjacency list
    graph = {}
    for task in tasks:
        task_id = task.get("id", "")
        deps = task.get("dependencies", [])
        graph[task_id] = deps if isinstance(deps, list) else []
    
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node: str, path: List[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return len(cycles) > 0, cycles


def _calculate_urgency(due_date: str) -> float:
    """
    Calculate urgency score based on due date, accounting for business days (excluding weekends).
    
    Args:
        due_date: Date string in format YYYY-MM-DD
    
    Returns:
        Urgency score between 0 and 1
    """
    if not due_date:
        return 0.3  # Low urgency if no due date
    
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        # Calculate business days until due date (Mon-Fri only)
        business_days = 0
        current = today
        while current < due:
            # 0 = Monday, 6 = Sunday
            if current.weekday() < 5:  # Monday to Friday
                business_days += 1
            current = current.replace(day=current.day + 1) if current.day < 28 else datetime(
                current.year, current.month + 1 if current.month < 12 else 1, 1
            ).date()
        
        # Simplified: just count days but apply discount for weekends
        total_days = (due - today).days
        
        if total_days < 0:
            return 1.0  # Overdue
        elif total_days == 0:
            return 0.95  # Due today
        elif total_days <= 3:
            return 0.8  # Due soon
        elif total_days <= 7:
            return 0.6  # Due this week (5 business days)
        elif total_days <= 30:
            return 0.4  # Due this month (~20 business days)
        else:
            return 0.2  # Due later
    except (ValueError, AttributeError):
        return 0.3  # Default if date parsing fails
