from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class Owner:
	name: str
	age: int
	availability_spots: list[str] = field(default_factory=list)
	energy_level: int = 0
	preferences: list[str] = field(default_factory=list)
	zip_code: str = ""
	work_mode: str = ""
	commute_duration: int = 0

	def work(self, hours: int) -> None:
		pass

	def chill(self, minutes: int) -> None:
		pass

	def sleep(self, hours: float) -> None:
		pass

	def commute(self, minutes: int) -> None:
		pass


@dataclass
class Pet:
	pet_type: str
	breed: str
	name: str
	age: int
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
		pass

	def roam(self, minutes: int) -> None:
		pass

	def feed(self, amount: float) -> None:
		pass

	def sleep(self, hours: float) -> None:
		pass

	def walk(self, minutes: int) -> None:
		pass

	def play(self, minutes: int) -> None:
		pass

	def massage(self, minutes: int) -> None:
		pass

	def bathe(self) -> None:
		pass


@dataclass
class Task:
	task_name: str
	category: str
	min_duration: int
	duration: int
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
		pass

	def edit(self, fields: dict[str, Any]) -> None:
		pass

	def delete(self) -> None:
		pass

	def estimate_score(self, owner: Owner, pet: Pet) -> float:
		pass


@dataclass
class Schedule:
	hour: int
	day: int
	week: int
	month: int
	year: int
	total_free_time: int = 0
	planned_tasks: list[Task] = field(default_factory=list)

	def score_plan(self) -> float:
		pass

	def schedule(self, task: Task) -> bool:
		pass

	def schedule_at(self, task: Task, hour: int) -> bool:
		pass

	def forward(self, hours: int) -> None:
		pass

	def backward(self, hours: int) -> None:
		pass

	def generate_daily_plan(self, tasks: list[Task], available_minutes: int) -> list[Task]:
		pass

	def explain_plan(self) -> str:
		pass
