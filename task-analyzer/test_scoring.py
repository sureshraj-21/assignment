"""Tests for the task scoring module."""
import pytest
from datetime import datetime, timedelta
from scoring import score_tasks, detect_cycles, _calculate_urgency


class TestScoreTasks:
    """Test cases for score_tasks function."""
    
    def test_score_tasks_basic(self):
        """Test basic task scoring."""
        tasks = [
            {"id": "1", "title": "Task A", "priority": 8, "effort": 4, "due_date": "2025-11-30"},
            {"id": "2", "title": "Task B", "priority": 5, "effort": 2, "due_date": "2025-12-15"},
        ]
        
        scored = score_tasks(tasks, strategy="smart")
        
        assert len(scored) == 2
        assert all("score" in task for task in scored)
        assert all("components" in task for task in scored)
        assert scored[0]["score"] > scored[1]["score"]  # Task A should score higher
    
    def test_score_tasks_assigns_ids(self):
        """Test that missing task IDs are assigned."""
        tasks = [
            {"title": "Task A", "priority": 5, "effort": 5},
            {"title": "Task B", "priority": 5, "effort": 5},
        ]
        
        scored = score_tasks(tasks)
        
        assert scored[0]["id"] == "task_0"
        assert scored[1]["id"] == "task_1"
    
    def test_score_tasks_urgency_strategy(self):
        """Test urgency scoring strategy."""
        today = datetime.now().date()
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        
        tasks = [
            {"id": "1", "title": "Urgent", "due_date": tomorrow, "priority": 1, "effort": 10},
            {"id": "2", "title": "Not urgent", "due_date": next_week, "priority": 10, "effort": 1},
        ]
        
        scored = score_tasks(tasks, strategy="urgency")
        
        # Urgent task should score higher with urgency strategy
        assert scored[0]["id"] == "1"
    
    def test_score_tasks_effort_strategy(self):
        """Test effort scoring strategy."""
        tasks = [
            {"id": "1", "title": "Quick", "priority": 1, "effort": 1, "due_date": "2025-12-31"},
            {"id": "2", "title": "Hard", "priority": 10, "effort": 10, "due_date": "2025-12-31"},
        ]
        
        scored = score_tasks(tasks, strategy="effort")
        
        # Quick task should score higher with effort strategy
        assert scored[0]["id"] == "1"
    
    def test_score_tasks_sets_defaults(self):
        """Test that missing fields are set with defaults."""
        tasks = [{"id": "1", "title": "Task A"}]
        
        scored = score_tasks(tasks)
        
        assert scored[0]["priority"] == 5
        assert scored[0]["effort"] == 5
        assert scored[0]["dependencies"] == []


class TestDetectCycles:
    """Test cases for detect_cycles function."""
    
    def test_detect_cycles_no_cycles(self):
        """Test detection when there are no cycles."""
        tasks = [
            {"id": "1", "dependencies": []},
            {"id": "2", "dependencies": ["1"]},
            {"id": "3", "dependencies": ["2"]},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        
        assert has_cycle is False
        assert cycles == []
    
    def test_detect_cycles_simple_cycle(self):
        """Test detection of a simple cycle."""
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["1"]},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        
        assert has_cycle is True
        assert len(cycles) > 0
    
    def test_detect_cycles_complex_cycle(self):
        """Test detection of a complex cycle."""
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["3"]},
            {"id": "3", "dependencies": ["1"]},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        
        assert has_cycle is True
        assert len(cycles) > 0
    
    def test_detect_cycles_self_loop(self):
        """Test detection of a self-loop."""
        tasks = [
            {"id": "1", "dependencies": ["1"]},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        
        assert has_cycle is True


class TestCalculateUrgency:
    """Test cases for _calculate_urgency function."""
    
    def test_urgency_overdue(self):
        """Test urgency for overdue tasks."""
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        urgency = _calculate_urgency(yesterday)
        assert urgency == 1.0
    
    def test_urgency_today(self):
        """Test urgency for tasks due today."""
        today = datetime.now().date().strftime("%Y-%m-%d")
        urgency = _calculate_urgency(today)
        assert urgency == 0.95
    
    def test_urgency_soon(self):
        """Test urgency for tasks due soon."""
        tomorrow = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
        urgency = _calculate_urgency(tomorrow)
        assert 0.7 <= urgency <= 0.9
    
    def test_urgency_week(self):
        """Test urgency for tasks due this week."""
        next_week = (datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")
        urgency = _calculate_urgency(next_week)
        assert 0.5 <= urgency <= 0.7
    
    def test_urgency_month(self):
        """Test urgency for tasks due this month."""
        next_month = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
        urgency = _calculate_urgency(next_month)
        assert 0.3 <= urgency <= 0.5
    
    def test_urgency_later(self):
        """Test urgency for tasks due later."""
        later = (datetime.now().date() + timedelta(days=60)).strftime("%Y-%m-%d")
        urgency = _calculate_urgency(later)
        assert urgency == 0.2
    
    def test_urgency_no_due_date(self):
        """Test urgency when no due date is provided."""
        urgency = _calculate_urgency(None)
        assert urgency == 0.3
    
    def test_urgency_invalid_date(self):
        """Test urgency with invalid date format."""
        urgency = _calculate_urgency("invalid-date")
        assert urgency == 0.3


# ============================================
# Additional Comprehensive Tests
# ============================================

class TestScoreTasksEdgeCases:
    """Edge case tests for score_tasks."""
    
    def test_empty_task_list(self):
        """Test scoring an empty task list."""
        scored = score_tasks([])
        assert scored == []
    
    def test_single_task(self):
        """Test scoring a single task."""
        tasks = [{"id": "1", "title": "Only task", "priority": 5, "effort": 5}]
        scored = score_tasks(tasks)
        assert len(scored) == 1
        assert scored[0]["score"] >= 0 and scored[0]["score"] <= 1
    
    def test_all_same_priority(self):
        """Test tasks with identical priority and effort."""
        tasks = [
            {"id": str(i), "title": f"Task {i}", "priority": 5, "effort": 5, "due_date": None}
            for i in range(3)
        ]
        scored = score_tasks(tasks)
        # All should have the same score
        assert all(t["score"] == scored[0]["score"] for t in scored)
    
    def test_importance_strategy(self):
        """Test importance-focused strategy."""
        tasks = [
            {"id": "1", "title": "High priority", "priority": 10, "effort": 10, "due_date": None},
            {"id": "2", "title": "Low priority", "priority": 1, "effort": 1, "due_date": None},
        ]
        scored = score_tasks(tasks, strategy="importance")
        assert scored[0]["id"] == "1"
    
    def test_component_normalization(self):
        """Test that components are properly normalized between 0 and 1."""
        tasks = [
            {"id": "1", "title": "High effort", "priority": 10, "effort": 10, "due_date": None},
            {"id": "2", "title": "Low effort", "priority": 1, "effort": 1, "due_date": None},
        ]
        scored = score_tasks(tasks)
        
        for task in scored:
            assert 0 <= task["components"]["effort"] <= 1
            assert 0 <= task["components"]["importance_norm"] <= 1
            assert 0 <= task["components"]["urgency"] <= 1


class TestDetectCyclesAdvanced:
    """Advanced cycle detection tests."""
    
    def test_multiple_independent_cycles(self):
        """Test detection of multiple independent cycles."""
        tasks = [
            {"id": "1", "dependencies": ["2"]},
            {"id": "2", "dependencies": ["1"]},
            {"id": "3", "dependencies": ["4"]},
            {"id": "4", "dependencies": ["3"]},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        assert has_cycle is True
        assert len(cycles) >= 2
    
    def test_partial_dependencies(self):
        """Test with some tasks having no dependencies."""
        tasks = [
            {"id": "1", "dependencies": []},
            {"id": "2", "dependencies": ["1"]},
            {"id": "3", "dependencies": ["2"]},
            {"id": "4", "dependencies": []},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        assert has_cycle is False
    
    def test_missing_dependency_references(self):
        """Test when dependencies reference non-existent tasks."""
        tasks = [
            {"id": "1", "dependencies": ["99"]},  # References non-existent task
            {"id": "2", "dependencies": []},
        ]
        
        has_cycle, cycles = detect_cycles(tasks)
        # Should not crash, treat missing refs as no cycle
        assert has_cycle is False


class TestScoringStrategies:
    """Test all four scoring strategies."""
    
    def test_all_strategies_produce_scores(self):
        """Verify all strategies generate valid scores."""
        tasks = [
            {"id": "1", "title": "A", "priority": 8, "effort": 3, "due_date": "2025-11-27"},
            {"id": "2", "title": "B", "priority": 5, "effort": 7, "due_date": "2025-12-10"},
            {"id": "3", "title": "C", "priority": 2, "effort": 9, "due_date": "2025-12-25"},
        ]
        
        strategies = ["smart", "urgency", "effort", "importance"]
        results = {}
        
        for strategy in strategies:
            scored = score_tasks(tasks, strategy=strategy)
            results[strategy] = scored
            
            # Verify all tasks have scores
            assert len(scored) == 3
            assert all(0 <= t["score"] <= 1 for t in scored)
        
        # Verify different strategies produce different orderings
        smart_order = [t["id"] for t in results["smart"]]
        effort_order = [t["id"] for t in results["effort"]]
        assert smart_order != effort_order
    
    def test_smart_strategy_balance(self):
        """Test that smart strategy balances all factors."""
        today = datetime.now().date()
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        tasks = [
            {
                "id": "urgent_hard",
                "title": "Urgent but hard",
                "priority": 1,
                "effort": 10,
                "due_date": tomorrow
            },
            {
                "id": "easy_low",
                "title": "Easy but low importance",
                "priority": 1,
                "effort": 1,
                "due_date": None
            },
        ]
        
        scored = score_tasks(tasks, strategy="smart")
        # Smart should prioritize urgent_hard due to urgency weight
        assert scored[0]["id"] == "urgent_hard"


class TestDataNormalization:
    """Test data normalization and defaults."""
    
    def test_list_dependencies_normalization(self):
        """Test that non-list dependencies are handled."""
        tasks = [
            {"id": "1", "title": "A", "dependencies": "task2"},  # String instead of list
        ]
        
        # Should not crash
        scored = score_tasks(tasks)
        assert len(scored) == 1
    
    def test_missing_optional_fields(self):
        """Test handling of completely missing optional fields."""
        tasks = [
            {"id": "1", "title": "Minimal task"}  # Only id and title
        ]
        
        scored = score_tasks(tasks)
        assert scored[0]["priority"] == 5  # Default
        assert scored[0]["effort"] == 5    # Default
        assert scored[0]["due_date"] is None  # Default
        assert scored[0]["dependencies"] == []  # Default


class TestScoreConsistency:
    """Test consistency of scoring across different scenarios."""
    
    def test_score_determinism(self):
        """Test that scoring the same task list produces same results."""
        tasks = [
            {"id": "1", "title": "Task A", "priority": 7, "effort": 4, "due_date": "2025-12-01"},
            {"id": "2", "title": "Task B", "priority": 3, "effort": 8, "due_date": "2025-12-15"},
        ]
        
        scored1 = score_tasks(tasks, strategy="smart")
        scored2 = score_tasks(tasks, strategy="smart")
        
        for i in range(len(scored1)):
            assert scored1[i]["score"] == scored2[i]["score"]
    
    def test_sorting_consistency(self):
        """Test that tasks are consistently sorted by score."""
        tasks = [
            {"id": str(i), "title": f"Task {i}", "priority": 10-i, "effort": i, "due_date": None}
            for i in range(5)
        ]
        
        scored = score_tasks(tasks)
        scores = [t["score"] for t in scored]
        
        # Scores should be in descending order
        assert scores == sorted(scores, reverse=True)


