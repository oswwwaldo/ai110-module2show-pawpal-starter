from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from pawpal_system import Owner, Pet, Schedule, ScheduleItem, Task


class OwnerService:
    @staticmethod
    def create_owner(name: str, age: int, **kwargs: object) -> Owner:
        return Owner(name=name, age=age, **kwargs)

    @staticmethod
    def add_pet(owner: Owner, pet: Pet) -> Pet:
        pet.owner_reference = owner
        if all(existing.pet_id != pet.pet_id for existing in owner.pets):
            owner.pets.append(pet)
        return pet

    @staticmethod
    def remove_pet(owner: Owner, pet_id: str) -> bool:
        for idx, pet in enumerate(owner.pets):
            if pet.pet_id == pet_id:
                owner.pets.pop(idx)
                owner.tasks = [task for task in owner.tasks if not task.pet_reference or task.pet_reference.pet_id != pet_id]
                return True
        return False

    @staticmethod
    def add_task(owner: Owner, task: Task) -> Task:
        task.owner_reference = owner
        if task.pet_reference is not None and task.pet_reference.owner_reference is not None:
            if task.pet_reference.owner_reference.owner_id != owner.owner_id:
                raise ValueError("task pet_reference must belong to owner")
        if all(existing.task_id != task.task_id for existing in owner.tasks):
            owner.tasks.append(task)
        return task

    @staticmethod
    def remove_task(owner: Owner, task_id: str) -> bool:
        for idx, task in enumerate(owner.tasks):
            if task.task_id == task_id:
                owner.tasks.pop(idx)
                return True
        return False

    @staticmethod
    def get_pet(owner: Owner, pet_id: str) -> Pet | None:
        return next((pet for pet in owner.pets if pet.pet_id == pet_id), None)

    @staticmethod
    def get_task(owner: Owner, task_id: str) -> Task | None:
        return next((task for task in owner.tasks if task.task_id == task_id), None)


class PetService:
    @staticmethod
    def create_pet(
        owner: Owner,
        pet_type: str,
        breed: str,
        name: str,
        age: int,
        **kwargs: object,
    ) -> Pet:
        pet = Pet(pet_type=pet_type, breed=breed, name=name, age=age, **kwargs)
        return OwnerService.add_pet(owner, pet)

    @staticmethod
    def update_pet(pet: Pet, **fields: object) -> Pet:
        for key, value in fields.items():
            if hasattr(pet, key):
                setattr(pet, key, value)
            else:
                raise KeyError(f"Unknown pet field: {key}")
        return pet


class TaskService:
    @staticmethod
    def create_task(
        owner: Owner,
        pet: Pet,
        task_name: str,
        category: str,
        min_duration: int,
        duration: int,
        **kwargs: object,
    ) -> Task:
        if pet.owner_reference is not None and pet.owner_reference.owner_id != owner.owner_id:
            raise ValueError("pet does not belong to owner")

        task = Task(
            task_name=task_name,
            category=category,
            min_duration=min_duration,
            duration=duration,
            owner_reference=owner,
            pet_reference=pet,
            **kwargs,
        )
        return OwnerService.add_task(owner, task)

    @staticmethod
    def update_task(task: Task, **fields: object) -> Task:
        task.edit(fields)
        return task

    @staticmethod
    def delete_task(owner: Owner, task_id: str, schedule: Schedule | None = None) -> bool:
        deleted = OwnerService.remove_task(owner, task_id)
        if not deleted:
            return False

        if schedule is not None:
            schedule.planned_tasks = [task for task in schedule.planned_tasks if task.task_id != task_id]
            schedule.schedule_items = [item for item in schedule.schedule_items if item.task_id != task_id]
        return True

    @staticmethod
    def list_tasks_for_pet(owner: Owner, pet_id: str) -> list[Task]:
        return [
            task
            for task in owner.tasks
            if task.pet_reference is not None and task.pet_reference.pet_id == pet_id
        ]


class ScheduleService:
    VALID_STATES = {"pending", "expired", "completed"}

    @staticmethod
    def create_schedule(
        owner: Owner,
        year: int,
        month: int,
        day: int,
        hour: int = 8,
    ) -> Schedule:
        schedule = Schedule(
            hour=hour,
            day=day,
            week=int(datetime(year, month, day).strftime("%U")),
            month=month,
            year=year,
            owner_reference=owner,
            pets_in_scope=list(owner.pets),
        )
        return schedule

    @staticmethod
    def set_owner(schedule: Schedule, owner: Owner) -> Schedule:
        schedule.owner_reference = owner
        schedule.pets_in_scope = list(owner.pets)
        return schedule

    @staticmethod
    def add_schedule_item(
        schedule: Schedule,
        task: Task,
        pet: Pet,
        start_at: datetime,
        end_at: datetime,
        state: Literal["pending", "expired", "completed"] = "pending",
    ) -> ScheduleItem:
        if state not in ScheduleService.VALID_STATES:
            raise ValueError("state must be one of: pending, expired, completed")
        if end_at <= start_at:
            raise ValueError("end_at must be later than start_at")
        if task.pet_reference is not None and task.pet_reference.pet_id != pet.pet_id:
            raise ValueError("task pet_reference does not match provided pet")
        if task.owner_reference is not None and schedule.owner_reference is not None:
            if task.owner_reference.owner_id != schedule.owner_reference.owner_id:
                raise ValueError("task owner does not match schedule owner")

        for existing in schedule.schedule_items:
            overlaps = start_at < existing.end_at and end_at > existing.start_at
            if overlaps:
                raise ValueError("schedule item overlaps with existing item")

        item = ScheduleItem(
            task=task,
            pet=pet,
            start_at=start_at,
            end_at=end_at,
            state=state,
            owner_reference=schedule.owner_reference or task.owner_reference,
            task_id=task.task_id,
            pet_id=pet.pet_id,
        )
        schedule.schedule_items.append(item)
        if all(existing.task_id != task.task_id for existing in schedule.planned_tasks):
            schedule.planned_tasks.append(task)
        if all(existing.pet_id != pet.pet_id for existing in schedule.pets_in_scope):
            schedule.pets_in_scope.append(pet)
        return item

    @staticmethod
    def generate_daily_plan(
        schedule: Schedule,
        tasks: list[Task],
        available_minutes: int,
        start_time: datetime | None = None,
    ) -> list[ScheduleItem]:
        if available_minutes <= 0:
            schedule.schedule_items = []
            schedule.planned_tasks = []
            return []

        start_cursor = start_time or datetime(schedule.year, schedule.month, schedule.day, schedule.hour)
        remaining = available_minutes

        prioritized_tasks = sorted(
            tasks,
            key=lambda task: (
                int(task.is_mandatory),
                task.priority,
                int(task.starred),
                task.due_date is not None,
            ),
            reverse=True,
        )

        items: list[ScheduleItem] = []
        for task in prioritized_tasks:
            task_minutes = max(task.min_duration, task.duration)
            if task_minutes <= remaining and task.pet_reference is not None:
                end_at = start_cursor + timedelta(minutes=task_minutes)
                item = ScheduleService.add_schedule_item(
                    schedule=schedule,
                    task=task,
                    pet=task.pet_reference,
                    start_at=start_cursor,
                    end_at=end_at,
                    state="pending",
                )
                items.append(item)
                start_cursor = end_at
                remaining -= task_minutes

        schedule.total_free_time = max(0, remaining)
        schedule.schedule_items = items
        schedule.planned_tasks = [item.task for item in items]
        schedule.pets_in_scope = list({item.pet.pet_id: item.pet for item in items}.values())
        return items

    @staticmethod
    def complete_item(schedule: Schedule, item_id: str) -> bool:
        for item in schedule.schedule_items:
            if item.item_id == item_id:
                item.state = "completed"
                return True
        return False

    @staticmethod
    def update_item_state(
        schedule: Schedule,
        item_id: str,
        state: Literal["pending", "expired", "completed"],
    ) -> bool:
        if state not in ScheduleService.VALID_STATES:
            raise ValueError("state must be one of: pending, expired, completed")
        for item in schedule.schedule_items:
            if item.item_id == item_id:
                item.state = state
                return True
        return False

    @staticmethod
    def remove_schedule_item(schedule: Schedule, item_id: str) -> bool:
        for idx, item in enumerate(schedule.schedule_items):
            if item.item_id == item_id:
                schedule.schedule_items.pop(idx)
                schedule.planned_tasks = [existing.task for existing in schedule.schedule_items]
                schedule.pets_in_scope = list({existing.pet.pet_id: existing.pet for existing in schedule.schedule_items}.values())
                return True
        return False

    @staticmethod
    def expire_overdue_items(schedule: Schedule, now: datetime | None = None) -> int:
        current_time = now or datetime.now()
        updated_count = 0
        for item in schedule.schedule_items:
            if item.state == "pending" and item.end_at < current_time:
                item.state = "expired"
                updated_count += 1
        return updated_count

    @staticmethod
    def explain_plan(schedule: Schedule) -> str:
        if not schedule.schedule_items:
            return "No tasks were scheduled."

        lines = []
        for item in schedule.schedule_items:
            reason_bits = [
                f"priority={item.task.priority}",
                f"mandatory={item.task.is_mandatory}",
                f"duration={item.task.duration}m",
            ]
            if item.task.starred:
                reason_bits.append("starred")
            lines.append(
                f"{item.start_at.strftime('%H:%M')} - {item.end_at.strftime('%H:%M')}: "
                f"{item.task.task_name} for {item.pet.name} ({', '.join(reason_bits)})"
            )
        return "\n".join(lines)
