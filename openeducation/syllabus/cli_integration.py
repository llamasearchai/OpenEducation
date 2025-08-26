from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .generator import SyllabusGenerator, Syllabus

app = typer.Typer(help="Syllabus generation and management tools")


@app.command()
def generate(
    subject: str = typer.Option(..., help="Subject area (e.g., science, mathematics)"),
    grade_level: str = typer.Option("9-12", help="Grade level (e.g., 9-12, K-5)"),
    duration_weeks: int = typer.Option(36, help="Course duration in weeks"),
    instructor: str = typer.Option("Teacher", help="Instructor name"),
    output_dir: str = typer.Option("data/syllabi", help="Output directory"),
    create_deck: bool = typer.Option(True, help="Generate Anki deck from syllabus"),
) -> None:
    """Generate a comprehensive syllabus for the specified subject."""
    try:
        generator = SyllabusGenerator()

        # Generate syllabus
        syllabus = generator.generate_syllabus(
            subject=subject,
            grade_level=grade_level,
            duration_weeks=duration_weeks,
            instructor=instructor
        )

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save syllabus as JSON
        syllabus_file = output_path / f"{syllabus.id}.json"
        with open(syllabus_file, "w", encoding="utf-8") as f:
            json.dump({
                "id": syllabus.id,
                "subject": syllabus.subject,
                "grade_level": syllabus.grade_level,
                "title": syllabus.title,
                "description": syllabus.description,
                "instructor": syllabus.instructor,
                "duration_weeks": syllabus.duration_weeks,
                "standards": syllabus.standards,
                "materials": syllabus.materials,
                "grading_policy": syllabus.grading_policy,
                "prerequisites": syllabus.prerequisites,
                "learning_outcomes": syllabus.learning_outcomes,
                "units": [
                    {
                        "id": unit.id,
                        "title": unit.title,
                        "description": unit.description,
                        "duration_weeks": unit.duration_weeks,
                        "assessment_methods": unit.assessment_methods,
                        "resources": unit.resources,
                        "projects": unit.projects,
                        "objectives": [
                            {
                                "id": obj.id,
                                "title": obj.title,
                                "description": obj.description,
                                "standard": obj.standard,
                                "difficulty": obj.difficulty,
                                "estimated_time": obj.estimated_time,
                                "prerequisites": obj.prerequisites,
                                "assessment_criteria": obj.assessment_criteria,
                                "resources": obj.resources,
                            }
                            for obj in unit.objectives
                        ]
                    }
                    for unit in syllabus.units
                ]
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ Syllabus generated: {syllabus_file}")

        # Generate Anki deck if requested
        if create_deck:
            cards_path = generator.generate_anki_deck_from_syllabus(syllabus, str(output_path))
            print(f"✅ Anki deck generated: {cards_path}")

        # Create learning schedule
        schedule = generator.create_learning_schedule(syllabus)
        schedule_file = output_path / f"{syllabus.id}_schedule.json"
        with open(schedule_file, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        print(f"✅ Learning schedule created: {schedule_file}")

        print("\n📚 Syllabus Summary:")
        print(f"   Subject: {syllabus.subject}")
        print(f"   Title: {syllabus.title}")
        print(f"   Units: {len(syllabus.units)}")
        print(f"   Duration: {syllabus.duration_weeks} weeks")
        print(f"   Standards: {', '.join(syllabus.standards)}")

    except Exception as e:
        print(f"❌ Error generating syllabus: {e}")
        raise typer.Exit(1)


@app.command()
def list_subjects() -> None:
    """List all available subjects for syllabus generation."""
    generator = SyllabusGenerator()
    subjects = list(generator.subject_templates.keys())

    print("📖 Available subjects for syllabus generation:")
    print("=" * 50)

    subject_descriptions = {
        "science": "Integrated science covering biology, chemistry, physics, and environmental science",
        "visual_performing_arts": "Visual arts, music, theater, and digital media creation",
        "social_studies": "World history, cultures, and contemporary global issues",
        "service_learning": "Community engagement and civic leadership",
        "mathematics": "Advanced algebra, trigonometry, and calculus preparation",
        "language_literacy": "Reading, writing, speaking, and critical thinking",
        "biliteracy_dual_language": "Dual language proficiency and cultural understanding",
        "social_justice": "Inequality analysis and social change strategies",
        "classroom_management": "Teaching strategies and classroom environment",
        "health_fitness": "Physical fitness and wellness education"
    }

    for subject in subjects:
        description = subject_descriptions.get(subject, "Educational content and activities")
        print(f"{subject:<15} {description}")
@app.command()
def schedule(
    syllabus_file: str = typer.Argument(..., help="Path to syllabus JSON file"),
    start_date: Optional[str] = typer.Option(None, help="Start date (YYYY-MM-DD)"),
    output_file: Optional[str] = typer.Option(None, help="Output schedule file"),
) -> None:
    """Create a detailed learning schedule from a syllabus."""
    try:
        # Load syllabus
        with open(syllabus_file, "r", encoding="utf-8") as f:
            syllabus_data = json.load(f)

        # Recreate syllabus object
        syllabus = Syllabus(
            id=syllabus_data["id"],
            subject=syllabus_data["subject"],
            grade_level=syllabus_data["grade_level"],
            title=syllabus_data["title"],
            description=syllabus_data["description"],
            duration_weeks=syllabus_data["duration_weeks"],
            instructor=syllabus_data["instructor"],
            standards=syllabus_data["standards"],
            materials=syllabus_data["materials"],
            grading_policy=syllabus_data["grading_policy"],
            prerequisites=syllabus_data["prerequisites"],
            learning_outcomes=syllabus_data["learning_outcomes"],
        )

        # Generate schedule
        generator = SyllabusGenerator()
        schedule = generator.create_learning_schedule(syllabus, start_date)

        # Determine output file
        if output_file is None:
            output_file = syllabus_file.replace(".json", "_schedule.json")

        # Save schedule
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        print(f"✅ Learning schedule created: {output_file}")
        print("\n📅 Schedule Summary:")
        print(f"   Start Date: {schedule['start_date']}")
        print(f"   End Date: {schedule['end_date']}")
        print(f"   Units: {len(schedule['schedule'])}")

        total_objectives = sum(len(unit['objectives']) for unit in schedule['schedule'])
        print(f"   Total Objectives: {total_objectives}")

    except Exception as e:
        print(f"❌ Error creating schedule: {e}")
        raise typer.Exit(1)


@app.command()
def export_deck(
    syllabus_file: str = typer.Argument(..., help="Path to syllabus JSON file"),
    output_dir: str = typer.Option("data/decks", help="Output directory for deck"),
) -> None:
    """Export Anki deck from syllabus content."""
    try:
        # Load syllabus
        with open(syllabus_file, "r", encoding="utf-8") as f:
            syllabus_data = json.load(f)

        # Recreate syllabus object
        syllabus = Syllabus(
            id=syllabus_data["id"],
            subject=syllabus_data["subject"],
            grade_level=syllabus_data["grade_level"],
            title=syllabus_data["title"],
            description=syllabus_data["description"],
            duration_weeks=syllabus_data["duration_weeks"],
            instructor=syllabus_data["instructor"],
            standards=syllabus_data["standards"],
            materials=syllabus_data["materials"],
            grading_policy=syllabus_data["grading_policy"],
            prerequisites=syllabus_data["prerequisites"],
            learning_outcomes=syllabus_data["learning_outcomes"],
        )

        # Generate Anki deck
        generator = SyllabusGenerator()
        cards_path = generator.generate_anki_deck_from_syllabus(syllabus, output_dir)

        print(f"✅ Anki deck exported: {cards_path}")

        # Count cards
        with open(cards_path, "r", encoding="utf-8") as f:
            cards = json.load(f)
            print(f"   Cards Generated: {len(cards)}")

        # Show card types
        card_types = {}
        for card in cards:
            card_type = card.get("tags", ["unknown"])[0]
            card_types[card_type] = card_types.get(card_type, 0) + 1

        print("   Card Types:")
        for card_type, count in card_types.items():
            print(f"     - {card_type}: {count}")

    except Exception as e:
        print(f"❌ Error exporting deck: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
