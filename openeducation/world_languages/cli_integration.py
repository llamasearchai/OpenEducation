from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .language_core import WorldLanguagesManager, Language, ProficiencyLevel, ACTFLMode

app = typer.Typer(help="World Languages instruction and cultural integration")


@app.command()
def show_curricula() -> None:
    """Show available language curricula."""
    try:
        manager = WorldLanguagesManager()

        print("🌍 World Languages Curricula Overview")
        print("=" * 60)

        curricula = manager.get_all_curricula()

        for language, levels in curricula.items():
            print(f"\n🏛️  {language}")
            print("-" * 30)

            for level, curriculum in levels.items():
                print(f"📚 {level.replace('_', ' ').title()}")
                print(f"   Title: {curriculum.title}")
                print(f"   Target: {curriculum.proficiency_target.value}")
                print(f"   Units: {len(curriculum.units)}")
                print(f"   Standards: {', '.join(curriculum.alignment_standards)}")

    except Exception as e:
        print(f"❌ Error showing curricula: {e}")
        raise typer.Exit(1)


@app.command()
def get_curriculum(
    language: str = typer.Option(..., help="Language (Japanese, Mandarin, Korean, French, Spanish)"),
    level: str = typer.Option(..., help="Level (middle_school, high_school)")
) -> None:
    """Get detailed curriculum for specific language and level."""
    try:
        manager = WorldLanguagesManager()

        curriculum = manager.get_curriculum(language, level)

        print(f"📚 {curriculum.title}")
        print("=" * 60)
        print(f"Language: {curriculum.language.value}")
        print(f"Level: {curriculum.level}")
        print(f"Target Proficiency: {curriculum.proficiency_target.value}")
        print(f"Description: {curriculum.description}")
        print(f"Created: {curriculum.created_date}")
        print(f"Standards: {', '.join(curriculum.alignment_standards)}")

        print("\n🎯 Essential Questions:")
        for question in curriculum.essential_questions:
            print(f"   • {question}")

        print("\n💡 Enduring Understandings:")
        for understanding in curriculum.enduring_understandings:
            print(f"   • {understanding}")

        print("\n🌍 Cultural Competencies:")
        for competency in curriculum.cultural_competencies:
            print(f"   • {competency}")

        print("\n💻 Technology Integration:")
        for tech in curriculum.technology_integration:
            print(f"   • {tech}")

        print("\n📊 Assessment Methods:")
        for method in curriculum.assessment_methods:
            print(f"   • {method}")

        print("\n📖 Units:")
        for i, unit in enumerate(curriculum.units, 1):
            print(f"   {i}. {unit['title']}")
            print(f"      Theme: {unit['theme']}")
            print(f"      Focus: {unit['proficiency_focus']}")
            print(f"      Activities: {len(unit['learning_activities'])}")

    except Exception as e:
        print(f"❌ Error getting curriculum: {e}")
        raise typer.Exit(1)


@app.command()
def create_lesson_plan(
    curriculum_id: str = typer.Option(..., help="Curriculum identifier"),
    title: str = typer.Option(..., help="Lesson plan title"),
    grade_level: str = typer.Option(..., help="Grade level (Middle School, High School)"),
    duration_minutes: int = typer.Option(45, help="Duration in minutes"),
    objective: str = typer.Option(..., help="Main learning objective"),
    communicative_goals: str = typer.Option(..., help="JSON string of communicative goals by mode"),
    language_functions: str = typer.Option(..., help="Comma-separated language functions"),
    vocabulary_focus: str = typer.Option(..., help="Comma-separated vocabulary words"),
    cultural_elements: str = typer.Option(..., help="Comma-separated cultural elements"),
    technology_tools: str = typer.Option(..., help="Comma-separated technology tools")
) -> None:
    """Create a comprehensive lesson plan."""
    try:
        manager = WorldLanguagesManager()

        # Parse communicative goals JSON
        try:
            goals_dict = json.loads(communicative_goals)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for communicative goals")
            print("Example: '{\"Interpersonal\": [\"Practice greetings\"], \"Presentational\": [\"Create presentation\"]}'")
            raise typer.Exit(1)

        # Parse lists
        functions_list = [f.strip() for f in language_functions.split(",")]
        vocab_list = [v.strip() for v in vocabulary_focus.split(",")]
        culture_list = [c.strip() for c in cultural_elements.split(",")]
        tech_list = [t.strip() for t in technology_tools.split(",") if t.strip()]

        lesson_plan = manager.create_lesson_plan(
            curriculum_id=curriculum_id,
            title=title,
            grade_level=grade_level,
            duration_minutes=duration_minutes,
            objective=objective,
            communicative_goals=goals_dict,
            language_functions=functions_list,
            vocabulary_focus=vocab_list,
            cultural_elements=culture_list,
            technology_tools=tech_list
        )

        print(f"✅ Lesson plan created successfully!")
        print(f"   Plan ID: {lesson_plan.id}")
        print(f"   Title: {lesson_plan.title}")
        print(f"   Grade Level: {lesson_plan.grade_level}")
        print(f"   Duration: {lesson_plan.duration_minutes} minutes")
        print(f"   Objective: {lesson_plan.objective}")

        print("\n🎯 Communicative Goals:")
        for mode, goals in lesson_plan.communicative_goals.items():
            print(f"   {mode}: {', '.join(goals)}")

        print("\n📝 Language Functions:")
        for func in lesson_plan.language_functions:
            print(f"   • {func}")

        print(f"\n📚 Vocabulary Focus: {len(lesson_plan.vocabulary_focus)} words")
        print(f"🌍 Cultural Elements: {len(lesson_plan.cultural_elements)}")
        print(f"💻 Technology Tools: {len(lesson_plan.technology_tools)}")
        print(f"📋 Procedures: {len(lesson_plan.procedures)} steps")
        print(f"📊 Assessment Methods: {len(lesson_plan.assessment['formative']) + len(lesson_plan.assessment['summative'])}")

    except Exception as e:
        print(f"❌ Error creating lesson plan: {e}")
        raise typer.Exit(1)


@app.command()
def create_cultural_activity(
    language: str = typer.Option(..., help="Language (Japanese, Mandarin, Korean, French, Spanish)"),
    title: str = typer.Option(..., help="Activity title"),
    description: str = typer.Option(..., help="Activity description"),
    activity_type: str = typer.Option("cultural_event", help="Type (cultural_event, presentation, internship, exchange)"),
    grade_levels: str = typer.Option(..., help="Comma-separated grade levels"),
    objectives: str = typer.Option(..., help="Comma-separated objectives"),
    duration_hours: int = typer.Option(2, help="Duration in hours")
) -> None:
    """Create a cultural enrichment activity."""
    try:
        manager = WorldLanguagesManager()

        # Parse language enum
        lang = Language(language)

        # Parse lists
        grade_list = [g.strip() for g in grade_levels.split(",")]
        obj_list = [o.strip() for o in objectives.split(",")]

        activity = manager.create_cultural_activity(
            language=lang,
            title=title,
            description=description,
            activity_type=activity_type,
            grade_levels=grade_list,
            objectives=obj_list,
            duration_hours=duration_hours
        )

        print(f"✅ Cultural activity created successfully!")
        print(f"   Activity ID: {activity.id}")
        print(f"   Language: {activity.language.value}")
        print(f"   Title: {activity.title}")
        print(f"   Type: {activity.type}")
        print(f"   Duration: {activity.duration_hours} hours")
        print(f"   Grade Levels: {', '.join(activity.grade_levels)}")

        print("\n🎯 Objectives:")
        for obj in activity.objectives:
            print(f"   • {obj}")

        print("\n📋 Preparation Needed:")
        for prep in activity.preparation_needed:
            print(f"   • {prep}")

        print(f"\n📚 Materials Required: {len(activity.materials_required)}")
        print(f"📊 Assessment Methods: {len(activity.assessment_methods)}")

    except Exception as e:
        print(f"❌ Error creating cultural activity: {e}")
        raise typer.Exit(1)


@app.command()
def assess_student(
    student_id: str = typer.Option(..., help="Student identifier"),
    language: str = typer.Option(..., help="Language"),
    proficiency_level: str = typer.Option(..., help="Current proficiency level"),
    assessment_type: str = typer.Option("progress", help="Assessment type"),
    scores: str = typer.Option(..., help="JSON string of assessment scores"),
    strengths: str = typer.Option(..., help="Comma-separated strengths"),
    areas_for_growth: str = typer.Option(..., help="Comma-separated areas for growth"),
    recommendations: str = typer.Option(..., help="Comma-separated recommendations")
) -> None:
    """Conduct comprehensive language assessment."""
    try:
        manager = WorldLanguagesManager()

        # Parse enums
        lang = Language(language)
        level = ProficiencyLevel(proficiency_level)

        # Parse scores JSON
        try:
            scores_dict = json.loads(scores)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for scores")
            print("Example: '{\"vocabulary\": 3.5, \"grammar\": 2.8, \"culture\": 4.0}'")
            raise typer.Exit(1)

        # Parse lists
        strengths_list = [s.strip() for s in strengths.split(",")]
        growth_list = [g.strip() for g in areas_for_growth.split(",")]
        recommendations_list = [r.strip() for r in recommendations.split(",")]

        assessment = manager.assess_student_progress(
            student_id=student_id,
            language=lang,
            proficiency_level=level,
            assessment_type=assessment_type,
            scores=scores_dict,
            strengths=strengths_list,
            areas_for_growth=growth_list,
            recommendations=recommendations_list
        )

        print(f"✅ Language assessment completed successfully!")
        print(f"   Assessment ID: {assessment.id}")
        print(f"   Student: {assessment.student_id}")
        print(f"   Language: {assessment.language.value}")
        print(f"   Proficiency Level: {assessment.proficiency_level.value}")
        print(f"   Assessment Type: {assessment.assessment_type}")
        print(f"   Date: {assessment.assessment_date}")

        print("\n📊 Scores:")
        for category, score in assessment.scores.items():
            print(f"   {category}: {score}")

        print(f"\n💪 Strengths: {len(assessment.strengths)}")
        print(f"📈 Areas for Growth: {len(assessment.areas_for_growth)}")
        print(f"💡 Recommendations: {len(assessment.recommendations)}")

    except Exception as e:
        print(f"❌ Error conducting assessment: {e}")
        raise typer.Exit(1)


@app.command()
def list_lesson_plans(
    curriculum_id: Optional[str] = typer.Option(None, help="Filter by curriculum ID"),
    grade_level: Optional[str] = typer.Option(None, help="Filter by grade level")
) -> None:
    """List lesson plans with optional filtering."""
    try:
        manager = WorldLanguagesManager()

        # Get all lesson plan files
        data_dir = Path("data/world_languages")
        lesson_files = list(data_dir.glob("lesson_plan_*.json"))

        if not lesson_files:
            print("📋 No lesson plans found")
            return

        lesson_plans = []
        for lesson_file in lesson_files:
            try:
                lesson_data = json.loads(lesson_file.read_text())
                lesson_plan = manager._load_lesson_plan_from_data(lesson_data)

                # Apply filters
                if curriculum_id and lesson_plan.curriculum_id != curriculum_id:
                    continue
                if grade_level and grade_level.lower() not in lesson_plan.grade_level.lower():
                    continue

                lesson_plans.append(lesson_plan)
            except Exception:
                continue

        if not lesson_plans:
            print("📋 No lesson plans match the specified filters")
            return

        print(f"📋 Lesson Plans ({len(lesson_plans)} total)")
        print("=" * 80)

        for plan in sorted(lesson_plans, key=lambda x: x.created_date, reverse=True):
            print(f"📝 {plan.id}")
            print(f"   Title: {plan.title}")
            print(f"   Grade Level: {plan.grade_level}")
            print(f"   Duration: {plan.duration_minutes} minutes")
            print(f"   Objective: {plan.objective}")
            print(f"   Created: {plan.created_date}")

            if plan.communicative_goals:
                print(f"   Communicative Goals: {len(plan.communicative_goals)} modes")

            if plan.vocabulary_focus:
                print(f"   Vocabulary: {len(plan.vocabulary_focus)} words")

            if plan.cultural_elements:
                print(f"   Cultural Elements: {len(plan.cultural_elements)}")

            print()

    except Exception as e:
        print(f"❌ Error listing lesson plans: {e}")
        raise typer.Exit(1)


@app.command()
def list_cultural_activities(
    language: Optional[str] = typer.Option(None, help="Filter by language"),
    activity_type: Optional[str] = typer.Option(None, help="Filter by activity type"),
    grade_level: Optional[str] = typer.Option(None, help="Filter by grade level")
) -> None:
    """List cultural activities with optional filtering."""
    try:
        manager = WorldLanguagesManager()

        # Get all cultural activity files
        data_dir = Path("data/world_languages")
        activity_files = list(data_dir.glob("cultural_activity_*.json"))

        if not activity_files:
            print("🌍 No cultural activities found")
            return

        activities = []
        for activity_file in activity_files:
            try:
                activity_data = json.loads(activity_file.read_text())
                activity = manager._load_cultural_activity_from_data(activity_data)

                # Apply filters
                if language and activity.language.value != language:
                    continue
                if activity_type and activity.type != activity_type:
                    continue
                if grade_level and grade_level not in activity.grade_levels:
                    continue

                activities.append(activity)
            except Exception:
                continue

        if not activities:
            print("🌍 No cultural activities match the specified filters")
            return

        print(f"🌍 Cultural Activities ({len(activities)} total)")
        print("=" * 80)

        for activity in sorted(activities, key=lambda x: x.title):
            print(f"🎭 {activity.id}")
            print(f"   Language: {activity.language.value}")
            print(f"   Title: {activity.title}")
            print(f"   Type: {activity.type}")
            print(f"   Duration: {activity.duration_hours} hours")
            print(f"   Grade Levels: {', '.join(activity.grade_levels)}")
            print(f"   Status: {activity.status}")

            if activity.objectives:
                print(f"   Objectives: {len(activity.objectives)}")

            if activity.scheduled_date:
                print(f"   Scheduled: {activity.scheduled_date}")

            print()

    except Exception as e:
        print(f"❌ Error listing cultural activities: {e}")
        raise typer.Exit(1)


@app.command()
def show_proficiency_levels() -> None:
    """Show ACTFL proficiency levels and descriptions."""
    try:
        print("🎯 ACTFL Proficiency Levels")
        print("=" * 50)

        levels = [
            ("Novice Low", "Can communicate using memorized words and phrases"),
            ("Novice Mid", "Can handle short social interactions with familiar topics"),
            ("Novice High", "Can create simple sentences on familiar topics"),
            ("Intermediate Low", "Can handle uncomplicated tasks in most situations"),
            ("Intermediate Mid", "Can participate in conversations on familiar topics"),
            ("Intermediate High", "Can satisfy most work and school needs"),
            ("Advanced Low", "Can handle a range of face-to-face professional tasks"),
            ("Advanced Mid", "Can discuss concrete topics with ease"),
            ("Advanced High", "Can handle most formal and informal interactions"),
            ("Superior", "Can communicate with accuracy in major topics"),
            ("Distinguished", "Can communicate as well as educated native speakers")
        ]

        for level, description in levels:
            print(f"📊 {level}")
            print(f"   {description}")
            print()

    except Exception as e:
        print(f"❌ Error showing proficiency levels: {e}")
        raise typer.Exit(1)


@app.command()
def show_actfl_modes() -> None:
    """Show ACTFL modes of communication."""
    try:
        print("💬 ACTFL Modes of Communication")
        print("=" * 50)

        modes = [
            ("Interpersonal", "Two-way communication between people"),
            ("Interpretive", "Understanding written and spoken language"),
            ("Presentational", "Expressing oneself through speaking/writing")
        ]

        for mode, description in modes:
            print(f"🎭 {mode}")
            print(f"   {description}")
            print()

        print("🌟 Key Features:")
        print("   • Communicative approach focuses on real-world language use")
        print("   • All modes essential for comprehensive language proficiency")
        print("   • Integrated skills development across modes")

    except Exception as e:
        print(f"❌ Error showing ACTFL modes: {e}")
        raise typer.Exit(1)


@app.command()
def show_content_areas() -> None:
    """Show world language content areas."""
    try:
        print("📚 World Language Content Areas")
        print("=" * 50)

        areas = [
            ("Grammar", "Language structures and patterns"),
            ("Vocabulary", "Word knowledge and usage"),
            ("Pronunciation", "Sounds and intonation patterns"),
            ("Culture", "Cultural perspectives and practices"),
            ("Literature", "Literary texts and analysis"),
            ("History", "Historical contexts and events"),
            ("Current Events", "Contemporary issues and topics"),
            ("Professions", "Career-related language and skills"),
            ("Media", "Digital and traditional media content")
        ]

        for area, description in areas:
            print(f"📖 {area}")
            print(f"   {description}")
            print()

        print("🌟 Integration Focus:")
        print("   • Content and language integrated learning")
        print("   • Cultural context for all content areas")
        print("   • Real-world application and relevance")

    except Exception as e:
        print(f"❌ Error showing content areas: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
