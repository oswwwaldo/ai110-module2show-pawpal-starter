"""Data models for PawPal+: Owner, Pet, Task, Schedule, and ScheduleItem domain classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4


def _clamp(value: int, lower: int = 0, upper: int = 100) -> int:
	"""Clamp an integer value between lower and upper bounds (default 0-100)."""
	return max(lower, min(upper, value))


@dataclass
class Owner:
	"""Represents a pet owner with schedule, preferences, and activity tracking."""
	name: str
	age: int
	owner_id: str = field(default_factory=lambda: str(uuid4()))
	availability_spots: list[str] = field(default_factory=list)
	energy_level: int = 0
	preferences: list[str] = field(default_factory=list)
	zip_code: str = ""
	work_mode: str = ""
	commute_duration: int = 0
	pets: list[Pet] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)

	def work(self, hours: int) -> None:
		"""Decrease owner energy level based on work duration."""
		if hours < 0:
			raise ValueError("hours must be non-negative")
		self.energy_level = _clamp(self.energy_level - (hours * 5))

	def chill(self, minutes: int) -> None:
		"""Increase owner energy level by relaxing for specified minutes."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.energy_level = _clamp(self.energy_level + (minutes // 15))

	def sleep(self, hours: float) -> None:
		"""Restore owner energy level by sleeping for specified hours."""
		if hours < 0:
			raise ValueError("hours must be non-negative")
		self.energy_level = _clamp(self.energy_level + int(hours * 10))

	def commute(self, minutes: int) -> None:
		"""Decrease owner energy level based on commute duration."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.energy_level = _clamp(self.energy_level - (minutes // 20))


@dataclass
class Pet:
	"""Represents a pet with state, health, and care activity tracking."""
	pet_type: str
	breed: str
	name: str
	age: int
	pet_id: str = field(default_factory=lambda: str(uuid4()))
	owner_reference: Owner | None = None
	weight: float = 0.0
	health: int = 0
	hunger: int = 0
	hygiene: int = 0
	happiness: int = 0
	energy: int = 0
	thirst: int = 0
	activity_level: int = 0
	last_fed_time: datetime | None = None
	last_bathed_time: datetime | None = None
	last_exercised_time: datetime | None = None
	last_drank_time: datetime | None = None
	last_played_time: datetime | None = None
	last_chilled_time: datetime | None = None
	last_roamed_time: datetime | None = None
	medication_frequency: str = ""

	def chill(self, minutes: int) -> None:
		"""Increase pet happiness and energy by relaxing together."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.happiness = _clamp(self.happiness + (minutes // 15))
		self.energy = _clamp(self.energy + (minutes // 10))
		self.last_chilled_time = datetime.now()

	def roam(self, minutes: int) -> None:
		"""Increase pet activity level while expending energy and increasing hunger."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.activity_level = _clamp(self.activity_level + (minutes // 10))
		self.energy = _clamp(self.energy - (minutes // 8))
		self.hunger = _clamp(self.hunger + (minutes // 10))
		self.last_roamed_time = datetime.now()

	def feed(self, amount: float) -> None:
		"""Reduce hunger and improve health by feeding the pet."""
		if amount <= 0:
			raise ValueError("amount must be greater than 0")
		self.hunger = _clamp(self.hunger - int(amount * 10))
		self.health = _clamp(self.health + int(amount * 2))
		self.last_fed_time = datetime.now()

	def sleep(self, hours: float) -> None:
		"""Restore pet energy and happiness through sleep."""
		if hours < 0:
			raise ValueError("hours must be non-negative")
		self.energy = _clamp(self.energy + int(hours * 12))
		self.happiness = _clamp(self.happiness + int(hours * 2))

	def walk(self, minutes: int) -> None:
		"""Improve pet activity, health, and hunger through exercise."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.activity_level = _clamp(self.activity_level + (minutes // 8))
		self.health = _clamp(self.health + (minutes // 20))
		self.energy = _clamp(self.energy - (minutes // 10))
		self.hunger = _clamp(self.hunger + (minutes // 12))
		self.last_exercised_time = datetime.now()

	def play(self, minutes: int) -> None:
		"""Increase pet happiness while expending energy through play."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.happiness = _clamp(self.happiness + (minutes // 8))
		self.energy = _clamp(self.energy - (minutes // 12))
		self.last_played_time = datetime.now()

	def massage(self, minutes: int) -> None:
		"""Improve pet happiness and health through massage."""
		if minutes < 0:
			raise ValueError("minutes must be non-negative")
		self.happiness = _clamp(self.happiness + (minutes // 10))
		self.health = _clamp(self.health + (minutes // 20))

	def bathe(self) -> None:
		"""Maximize pet hygiene while slightly decreasing happiness."""
		self.hygiene = _clamp(100)
		self.happiness = _clamp(self.happiness - 5)
		self.last_bathed_time = datetime.now()


@dataclass
class Task:
	"""Represents a pet care task with priority, scheduling, and scoring metadata."""
	task_name: str
	category: str
	min_duration: int
	duration: int
	task_id: str = field(default_factory=lambda: str(uuid4()))
	owner_reference: Owner | None = None
	pet_reference: Pet | None = None
	location: str = ""
	priority: int = 0
	starred: bool = False
	status: str = "pending"
	today: bool = False
	due_date: date | None = None
	remind_date: date | None = None
	frequency: str = ""
	note: str = ""
	color: str = ""
	is_weather_dependent: bool = False
	is_mandatory: bool = False
	energy_cost: int = 0

	@classmethod
	def create(cls, task_name: str, category: str, min_duration: int, duration: int) -> Task:
		"""Factory method to create a validated task with duration constraints."""
		if min_duration < 0 or duration < 0:
			raise ValueError("durations must be non-negative")
		if min_duration > duration:
			raise ValueError("min_duration cannot be greater than duration")
		return cls(
			task_name=task_name,
			category=category,
			min_duration=min_duration,
			duration=duration,
		)

	def edit(self, fields: dict[str, Any]) -> None:
		"""Update task fields with validation for duration constraints."""
		for key, value in fields.items():
			if not hasattr(self, key):
				raise KeyError(f"Unknown task field: {key}")
			setattr(self, key, value)

		if self.min_duration < 0 or self.duration < 0:
			raise ValueError("durations must be non-negative")
		if self.min_duration > self.duration:
			raise ValueError("min_duration cannot be greater than duration")

	def delete(self) -> None:
		"""Mark task as deleted."""
		self.status = "deleted"

	def estimate_score(self, owner: Owner, pet: Pet) -> float:
		"""Compute task priority score considering mandatory, starred, due date, and owner energy."""
		score = float(self.priority * 10)
		if self.is_mandatory:
			score += 30
		if self.starred:
			score += 8
		if self.today:
			score += 5
		if self.due_date is not None:
			days_to_due = (self.due_date - date.today()).days
			if days_to_due <= 0:
				score += 20
			elif days_to_due <= 2:
				score += 10

		energy_gap = self.energy_cost - owner.energy_level
		if energy_gap > 0:
			score -= min(energy_gap, 25)

		if self.pet_reference is not None and self.pet_reference.pet_id == pet.pet_id:
			score += 5

		return score


@dataclass
class ScheduleItem:
	"""Represents a scheduled pet care task with time window and completion state."""
	task: Task
	pet: Pet
	start_at: datetime
	end_at: datetime
	item_id: str = field(default_factory=lambda: str(uuid4()))
	state: Literal["pending", "expired", "completed"] = "pending"
	owner_reference: Owner | None = None
	task_id: str | None = None
	pet_id: str | None = None


@dataclass
class Schedule:
	"""Represents a daily schedule with planned tasks and timed schedule items."""
	hour: int
	day: int
	week: int
	month: int
	year: int
	owner_reference: Owner | None = None
	total_free_time: int = 0
	planned_tasks: list[Task] = field(default_factory=list)
	schedule_items: list[ScheduleItem] = field(default_factory=list)
	pets_in_scope: list[Pet] = field(default_factory=list)

	def score_plan(self) -> float:
		"""Calculate overall plan quality score from task priorities and item completion states."""
		if not self.schedule_items and not self.planned_tasks:
			return 0.0

		task_score = 0.0
		if self.planned_tasks:
			task_score = float(
				sum((task.priority * 10) + (20 if task.is_mandatory else 0) for task in self.planned_tasks)
			)

		state_bonus = 0.0
		for item in self.schedule_items:
			if item.state == "completed":
				state_bonus += 5
			elif item.state == "expired":
				state_bonus -= 10

		return max(0.0, task_score + state_bonus)

	def schedule(self, task: Task) -> bool:
		"""Add a task to the planned tasks list if not already scheduled."""
		if any(existing.task_id == task.task_id for existing in self.planned_tasks):
			return False
		self.planned_tasks.append(task)
		return True

	def schedule_at(self, task: Task, hour: int) -> bool:
		"""Schedule a task at a specific hour and create a timed schedule item."""
		if hour < 0 or hour > 23:
			return False

		if not self.schedule(task):
			return False

		if task.pet_reference is None:
			return True

		start_at = datetime(self.year, self.month, self.day, hour)
		end_at = start_at + timedelta(minutes=max(task.min_duration, task.duration))
		item = ScheduleItem(
			task=task,
			pet=task.pet_reference,
			start_at=start_at,
			end_at=end_at,
			owner_reference=self.owner_reference or task.owner_reference,
			task_id=task.task_id,
			pet_id=task.pet_reference.pet_id,
		)
		self.schedule_items.append(item)
		if all(pet.pet_id != task.pet_reference.pet_id for pet in self.pets_in_scope):
			self.pets_in_scope.append(task.pet_reference)
		return True

	def forward(self, hours: int) -> None:		
		"""Move schedule time backward by specified hours."""		
		"""Advance schedule time forward by specified hours."""
		if hours < 0:
			raise ValueError("hours must be non-negative")
		current = datetime(self.year, self.month, self.day, self.hour)
		future = current + timedelta(hours=hours)
		self.hour = future.hour
		self.day = future.day
		self.month = future.month
		self.year = future.year
		self.week = int(future.strftime("%U"))

	def backward(self, hours: int) -> None:
		"""Move schedule time backward by specified hours."""
		if hours < 0:
			raise ValueError("hours must be non-negative")
		current = datetime(self.year, self.month, self.day, self.hour)
		past = current - timedelta(hours=hours)
		self.hour = past.hour
		self.day = past.day
		self.month = past.month
		self.year = past.year
		self.week = int(past.strftime("%U"))

	def generate_daily_plan(self, tasks: list[Task], available_minutes: int) -> list[Task]:
		"""Generate an optimal plan by prioritizing mandatory, high-priority, and starred tasks."""
		if available_minutes <= 0:
			self.planned_tasks = []
			self.schedule_items = []
			self.total_free_time = 0
			return []

		prioritized = sorted(
			tasks,
			key=lambda task: (
				int(task.is_mandatory),
				task.priority,
				int(task.starred),
			),
			reverse=True,
		)

		selected: list[Task] = []
		remaining = available_minutes
		for task in prioritized:
			required = max(task.min_duration, task.duration)
			if required <= remaining:
				selected.append(task)
				remaining -= required

		self.planned_tasks = selected
		self.total_free_time = remaining
		return selected

	def explain_plan(self) -> str:
		"""Return a human-readable explanation of the schedule or plan."""
		if self.schedule_items:
			lines = []
			for item in self.schedule_items:
				lines.append(
					f"{item.start_at.strftime('%H:%M')}-{item.end_at.strftime('%H:%M')}: "
					f"{item.task.task_name} ({item.state})"
				)
			return "\n".join(lines)

		if self.planned_tasks:
			names = ", ".join(task.task_name for task in self.planned_tasks)
			return f"Planned tasks: {names}. Free time left: {self.total_free_time} minutes."

		return "No tasks were scheduled."
