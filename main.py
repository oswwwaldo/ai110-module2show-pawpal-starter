"""
Demo script: Create an owner with multiple pets and tasks, then generate and display a daily schedule.
"""

from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, Schedule
from pawpal_services import OwnerService, PetService, TaskService, ScheduleService


def main():
    print("=" * 70)
    print("PawPal+ Daily Schedule Demo")
    print("=" * 70)
    print()

    # Create an owner
    owner = OwnerService.create_owner(
        name="Alice",
        age=32,
        energy_level=75,
        zip_code="90210",
        work_mode="flexible",
        commute_duration=30,
    )
    print(f"✓ Created owner: {owner.name} (ID: {owner.owner_id[:8]}...)")
    print()

    # Create pets
    dog = PetService.create_pet(
        owner=owner,
        pet_type="dog",
        breed="Golden Retriever",
        name="Max",
        age=3,
        weight=32.5,
        health=85,
        hunger=50,
        hygiene=70,
        happiness=80,
        energy=75,
        activity_level=70,
    )
    print(f"✓ Created pet 1: {dog.name} ({dog.pet_type}) - ID: {dog.pet_id[:8]}...")

    cat = PetService.create_pet(
        owner=owner,
        pet_type="cat",
        breed="Siamese",
        name="Luna",
        age=2,
        weight=4.2,
        health=90,
        hunger=60,
        hygiene=80,
        happiness=75,
        energy=60,
        activity_level=40,
    )
    print(f"✓ Created pet 2: {cat.name} ({cat.pet_type}) - ID: {cat.pet_id[:8]}...")
    print()

    # Create tasks for the pets
    task1 = TaskService.create_task(
        owner=owner,
        pet=dog,
        task_name="Morning Walk",
        category="exercise",
        min_duration=15,
        duration=30,
        priority=9,
        is_mandatory=True,
        energy_cost=10,
        location="Riverside Park",
    )
    print(f"✓ Created task 1: {task1.task_name} (for {dog.name}, {task1.duration}m) - ID: {task1.task_id[:8]}...")

    task2 = TaskService.create_task(
        owner=owner,
        pet=dog,
        task_name="Feeding",
        category="feeding",
        min_duration=5,
        duration=10,
        priority=10,
        is_mandatory=True,
        energy_cost=2,
        location="Home",
        today=True,
    )
    print(f"✓ Created task 2: {task2.task_name} (for {dog.name}, {task2.duration}m) - ID: {task2.task_id[:8]}...")

    task3 = TaskService.create_task(
        owner=owner,
        pet=cat,
        task_name="Play Session",
        category="enrichment",
        min_duration=10,
        duration=20,
        priority=7,
        is_mandatory=False,
        energy_cost=5,
        location="Home",
        starred=True,
    )
    print(f"✓ Created task 3: {task3.task_name} (for {cat.name}, {task3.duration}m) - ID: {task3.task_id[:8]}...")

    task4 = TaskService.create_task(
        owner=owner,
        pet=cat,
        task_name="Grooming",
        category="grooming",
        min_duration=10,
        duration=15,
        priority=6,
        is_mandatory=False,
        energy_cost=3,
        location="Home",
        due_date=date.today(),
    )
    print(f"✓ Created task 4: {task4.task_name} (for {cat.name}, {task4.duration}m) - ID: {task4.task_id[:8]}...")
    print()

    # Create a schedule for today
    today = datetime.now()
    schedule = ScheduleService.create_schedule(
        owner=owner,
        year=today.year,
        month=today.month,
        day=today.day,
        hour=8,  # Start at 8 AM
    )
    print(f"✓ Created schedule for today ({today.strftime('%Y-%m-%d')})")
    print(f"  Available time starting at {schedule.hour}:00")
    print()

    # Generate a daily plan with 180 minutes (3 hours) available
    available_minutes = 180
    all_tasks = owner.tasks
    plan = ScheduleService.generate_daily_plan(
        schedule=schedule,
        tasks=all_tasks,
        available_minutes=available_minutes,
        start_time=datetime(today.year, today.month, today.day, 8, 0),
    )

    print(f"✓ Generated daily plan with {available_minutes} minutes available")
    print()

    # Display the schedule
    print("=" * 70)
    print("TODAY'S PET CARE SCHEDULE")
    print("=" * 70)
    print()
    explanation = ScheduleService.explain_plan(schedule)
    print(explanation)
    print()
    print(f"Free time remaining: {schedule.total_free_time} minutes")
    print(f"Plan score: {schedule.score_plan()}")
    print()

    # Display scheduled items with detailed info
    if schedule.schedule_items:
        print("=" * 70)
        print("DETAILED SCHEDULE ITEMS")
        print("=" * 70)
        print()
        for idx, item in enumerate(schedule.schedule_items, 1):
            print(f"[{idx}] {item.task.task_name}")
            print(f"    Time: {item.start_at.strftime('%H:%M')} - {item.end_at.strftime('%H:%M')}")
            print(f"    Pet: {item.pet.name}")
            print(f"    Priority: {item.task.priority} | Mandatory: {item.task.is_mandatory}")
            print(f"    State: {item.state}")
            print()
    else:
        print("No scheduled items (all tasks fit in free-form planning).")
        print()

    # Display owner and pet state
    print("=" * 70)
    print("OWNER & PET STATE")
    print("=" * 70)
    print()
    print(f"Owner: {owner.name}")
    print(f"  Energy Level: {owner.energy_level}")
    print(f"  # Pets: {len(owner.pets)}")
    print(f"  # Tasks: {len(owner.tasks)}")
    print()
    for pet in owner.pets:
        print(f"Pet: {pet.name} ({pet.pet_type})")
        print(f"  Age: {pet.age} | Weight: {pet.weight} kg")
        print(f"  Health: {pet.health} | Energy: {pet.energy} | Happiness: {pet.happiness}")
        print(f"  Hunger: {pet.hunger} | Hygiene: {pet.hygiene} | Activity: {pet.activity_level}")
        print()


if __name__ == "__main__":
    main()
