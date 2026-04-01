"""
Unit tests for PawPal+ system: Task completion, addition, and scheduling.
"""

import pytest
from datetime import datetime, date, timedelta
from pawpal_system import Owner, Pet, Task, Schedule, ScheduleItem
from pawpal_services import OwnerService, PetService, TaskService, ScheduleService


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def owner():
    """Create a test owner."""
    return OwnerService.create_owner(name="TestOwner", age=30, energy_level=80)


@pytest.fixture
def pet(owner):
    """Create a test pet owned by the test owner."""
    return PetService.create_pet(
        owner=owner,
        pet_type="dog",
        breed="Labrador",
        name="TestDog",
        age=2,
    )


@pytest.fixture
def pet2(owner):
    """Create a second test pet owned by the test owner."""
    return PetService.create_pet(
        owner=owner,
        pet_type="cat",
        breed="Persian",
        name="TestCat",
        age=1,
    )


@pytest.fixture
def task(owner, pet):
    """Create a test task assigned to the pet."""
    return TaskService.create_task(
        owner=owner,
        pet=pet,
        task_name="Test Task",
        category="testing",
        min_duration=10,
        duration=20,
        priority=5,
    )


@pytest.fixture
def schedule(owner):
    """Create a test schedule."""
    today = datetime.now()
    return ScheduleService.create_schedule(
        owner=owner,
        year=today.year,
        month=today.month,
        day=today.day,
        hour=8,
    )


# ============================================================================
# Task Completion Tests
# ============================================================================


class TestTaskCompletion:
    """Tests for task state transitions and completion."""

    def test_task_initial_state_pending(self, owner, pet):
        """Verify that a newly created task has 'pending' state by default."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="New Task",
            category="test",
            min_duration=5,
            duration=10,
        )
        assert task.status == "pending", "New task should have pending status"

    def test_schedule_item_initial_state_pending(self, owner, pet, task, schedule):
        """Verify that a newly added schedule item has 'pending' state."""
        start = datetime.now()
        end = start + timedelta(minutes=20)
        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )
        assert item.state == "pending", "New schedule item should have pending state"

    def test_complete_schedule_item(self, owner, pet, task, schedule):
        """Verify that marking a schedule item as complete changes its state."""
        start = datetime.now()
        end = start + timedelta(minutes=20)
        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )

        # Mark as completed
        success = ScheduleService.complete_item(schedule, item.item_id)
        assert success, "complete_item should succeed for valid item_id"

        # Verify state changed
        updated_item = next(i for i in schedule.schedule_items if i.item_id == item.item_id)
        assert updated_item.state == "completed", "Item state should be 'completed' after complete_item()"

    def test_update_item_state_to_expired(self, owner, pet, task, schedule):
        """Verify that explicitly setting state to 'expired' works."""
        start = datetime.now()
        end = start + timedelta(minutes=20)
        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )

        success = ScheduleService.update_item_state(schedule, item.item_id, "expired")
        assert success, "update_item_state should succeed"

        updated_item = next(i for i in schedule.schedule_items if i.item_id == item.item_id)
        assert updated_item.state == "expired", "State should be 'expired'"

    def test_update_item_state_invalid_state_raises(self, owner, pet, task, schedule):
        """Verify that setting an invalid state raises ValueError."""
        start = datetime.now()
        end = start + timedelta(minutes=20)
        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )

        with pytest.raises(ValueError, match="state must be one of"):
            ScheduleService.update_item_state(schedule, item.item_id, "invalid_state")

    def test_expire_overdue_items(self, owner, pet, task, schedule):
        """Verify that expire_overdue_items correctly marks expired tasks."""
        # Create an item that ended in the past
        now = datetime.now()
        past_start = now - timedelta(hours=2)
        past_end = now - timedelta(hours=1)

        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=past_start,
            end_at=past_end,
        )

        # Expire overdue items
        expired_count = ScheduleService.expire_overdue_items(schedule, now=now)
        assert expired_count == 1, "One item should be expired"

        updated_item = next(i for i in schedule.schedule_items if i.item_id == item.item_id)
        assert updated_item.state == "expired", "Overdue item should be marked expired"

    def test_task_completion_flow(self, owner, pet, task, schedule):
        """Full flow: create task -> schedule -> complete."""
        start = datetime.now()
        end = start + timedelta(minutes=20)

        # Add to schedule
        item = ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )
        assert item.state == "pending"

        # Complete it
        ScheduleService.complete_item(schedule, item.item_id)

        # Verify change
        final_item = next(i for i in schedule.schedule_items if i.item_id == item.item_id)
        assert final_item.state == "completed"


# ============================================================================
# Task Addition Tests
# ============================================================================


class TestTaskAddition:
    """Tests for adding tasks and verifying ownership links."""

    def test_add_task_increases_owner_task_count(self, owner, pet):
        """Verify that adding a task to an owner increases the owner's task count."""
        initial_count = len(owner.tasks)
        assert initial_count == 0, "Owner should start with no tasks"

        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="New Task",
            category="test",
            min_duration=5,
            duration=10,
        )

        assert len(owner.tasks) == initial_count + 1, "Owner task count should increase by 1"
        assert task in owner.tasks, "Created task should be in owner.tasks"

    def test_add_multiple_tasks_to_owner(self, owner, pet, pet2):
        """Verify that multiple tasks can be added and counted correctly."""
        task1 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Task 1",
            category="test",
            min_duration=5,
            duration=10,
        )

        task2 = TaskService.create_task(
            owner=owner,
            pet=pet2,
            task_name="Task 2",
            category="test",
            min_duration=5,
            duration=10,
        )

        assert len(owner.tasks) == 2, "Owner should have 2 tasks"
        assert task1 in owner.tasks, "Task 1 should be in owner.tasks"
        assert task2 in owner.tasks, "Task 2 should be in owner.tasks"

    def test_task_linked_to_pet(self, owner, pet):
        """Verify that a created task has pet_reference pointing to the correct pet."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Pet Task",
            category="test",
            min_duration=5,
            duration=10,
        )

        assert task.pet_reference is not None, "Task should have pet_reference"
        assert task.pet_reference.pet_id == pet.pet_id, "Task pet_reference should match the pet"

    def test_task_linked_to_owner(self, owner, pet):
        """Verify that a created task has owner_reference pointing to the correct owner."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Owner Task",
            category="test",
            min_duration=5,
            duration=10,
        )

        assert task.owner_reference is not None, "Task should have owner_reference"
        assert task.owner_reference.owner_id == owner.owner_id, "Task owner_reference should match the owner"

    def test_list_tasks_for_pet(self, owner, pet, pet2):
        """Verify that tasks can be filtered by pet."""
        # Create tasks for different pets
        task1 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Pet1 Task 1",
            category="test",
            min_duration=5,
            duration=10,
        )

        task2 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Pet1 Task 2",
            category="test",
            min_duration=5,
            duration=10,
        )

        task3 = TaskService.create_task(
            owner=owner,
            pet=pet2,
            task_name="Pet2 Task 1",
            category="test",
            min_duration=5,
            duration=10,
        )

        # List tasks for pet
        pet_tasks = TaskService.list_tasks_for_pet(owner, pet.pet_id)
        assert len(pet_tasks) == 2, "Should return 2 tasks for pet"
        assert task1 in pet_tasks, "Task 1 should be in pet tasks"
        assert task2 in pet_tasks, "Task 2 should be in pet tasks"
        assert task3 not in pet_tasks, "Task 3 (for different pet) should not be in pet tasks"

    def test_delete_task_decreases_owner_count(self, owner, pet):
        """Verify that deleting a task decreases the owner's task count."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Deletable Task",
            category="test",
            min_duration=5,
            duration=10,
        )

        assert len(owner.tasks) == 1

        TaskService.delete_task(owner, task.task_id)
        assert len(owner.tasks) == 0, "Task count should decrease after deletion"

    def test_task_with_different_priority_levels(self, owner, pet):
        """Verify that tasks can have different priorities."""
        low_priority = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Low Priority",
            category="test",
            min_duration=5,
            duration=10,
            priority=1,
        )

        high_priority = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="High Priority",
            category="test",
            min_duration=5,
            duration=10,
            priority=10,
        )

        assert low_priority.priority == 1
        assert high_priority.priority == 10
        assert len(owner.tasks) == 2


# ============================================================================
# Schedule Generation Tests
# ============================================================================


class TestScheduleGeneration:
    """Tests for schedule generation and planning."""

    def test_generate_daily_plan_respects_time_limit(self, owner, pet):
        """Verify that generated plan respects available time limit."""
        schedule = ScheduleService.create_schedule(
            owner=owner,
            year=2026,
            month=4,
            day=1,
            hour=8,
        )

        # Create tasks totaling 100 minutes
        task1 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Task1",
            category="test",
            min_duration=30,
            duration=40,
            priority=5,
        )

        task2 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Task2",
            category="test",
            min_duration=20,
            duration=30,
            priority=6,
        )

        task3 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Task3",
            category="test",
            min_duration=15,
            duration=20,
            priority=4,
        )

        # Generate plan with 60 minutes available
        plan = ScheduleService.generate_daily_plan(
            schedule=schedule,
            tasks=[task1, task2, task3],
            available_minutes=60,
        )

        # Total time used should not exceed 60 minutes
        total_used = sum(max(item.task.min_duration, item.task.duration) for item in schedule.schedule_items)
        assert total_used <= 60, f"Total used time {total_used} should not exceed 60 minutes"
        assert schedule.total_free_time >= 0, "Free time should not be negative"

    def test_generate_daily_plan_prioritizes_mandatory(self, owner, pet):
        """Verify that mandatory tasks are prioritized in plan generation."""
        schedule = ScheduleService.create_schedule(
            owner=owner,
            year=2026,
            month=4,
            day=1,
            hour=8,
        )

        # Create mandatory and optional tasks
        mandatory = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Mandatory",
            category="test",
            min_duration=5,
            duration=10,
            priority=1,
            is_mandatory=True,
        )

        optional = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Optional",
            category="test",
            min_duration=5,
            duration=10,
            priority=10,
            is_mandatory=False,
        )

        plan = ScheduleService.generate_daily_plan(
            schedule=schedule,
            tasks=[optional, mandatory],
            available_minutes=20,
        )

        # Both should fit
        assert len(plan) == 2, "Both tasks should fit in plan"
        # Mandatory should be first in planned_tasks
        assert schedule.planned_tasks[0].is_mandatory, "Mandatory task should be first in plan"

    def test_schedule_plan_explanation(self, owner, pet, task, schedule):
        """Verify that plan explanation is readable and contains task info."""
        start = datetime.now()
        end = start + timedelta(minutes=20)

        ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start,
            end_at=end,
        )

        explanation = ScheduleService.explain_plan(schedule)
        assert task.task_name in explanation, "Explanation should contain task name"
        assert pet.name in explanation, "Explanation should contain pet name"
        assert "priority" in explanation, "Explanation should mention priority"


# ============================================================================
# Validation and Error Handling Tests
# ============================================================================


class TestValidationAndErrors:
    """Tests for error handling and input validation."""

    def test_task_creation_with_invalid_duration_raises(self, owner, pet):
        """Verify that editing a task with invalid durations raises."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Valid",
            category="test",
            min_duration=5,
            duration=10,
        )
        # Editing with invalid durations should raise
        with pytest.raises(ValueError, match="durations must be non-negative"):
            TaskService.update_task(task, min_duration=-5)

    def test_schedule_item_with_invalid_time_window_raises(self, owner, pet, task, schedule):
        """Verify that creating a schedule item with end_at <= start_at raises."""
        start = datetime.now()
        end = start - timedelta(minutes=5)

        with pytest.raises(ValueError, match="end_at must be later than start_at"):
            ScheduleService.add_schedule_item(
                schedule=schedule,
                task=task,
                pet=pet,
                start_at=start,
                end_at=end,
            )

    def test_schedule_item_overlap_detection(self, owner, pet, task, schedule):
        """Verify that overlapping schedule items are rejected."""
        start1 = datetime(2026, 4, 1, 8, 0)
        end1 = datetime(2026, 4, 1, 9, 0)

        ScheduleService.add_schedule_item(
            schedule=schedule,
            task=task,
            pet=pet,
            start_at=start1,
            end_at=end1,
        )

        # Try to add overlapping item
        start2 = datetime(2026, 4, 1, 8, 30)
        end2 = datetime(2026, 4, 1, 9, 30)

        task2 = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Another Task",
            category="test",
            min_duration=5,
            duration=60,
        )

        with pytest.raises(ValueError, match="overlaps with existing item"):
            ScheduleService.add_schedule_item(
                schedule=schedule,
                task=task2,
                pet=pet,
                start_at=start2,
                end_at=end2,
            )

    def test_pet_mismatch_task_pet_reference_raises(self, owner, pet, pet2):
        """Verify that assigning a task to a mismatched pet raises."""
        task = TaskService.create_task(
            owner=owner,
            pet=pet,
            task_name="Pet1 Task",
            category="test",
            min_duration=5,
            duration=10,
        )

        start = datetime.now()
        end = start + timedelta(minutes=10)

        with pytest.raises(ValueError, match="pet_reference does not match"):
            ScheduleService.add_schedule_item(
                schedule=ScheduleService.create_schedule(owner, 2026, 4, 1),
                task=task,
                pet=pet2,
                start_at=start,
                end_at=end,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
