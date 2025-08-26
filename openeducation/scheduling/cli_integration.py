from __future__ import annotations

import json
from typing import Optional

import typer

from .progress_tracker import AnkiPerformance, ProgressTracker, StudySession

app = typer.Typer(help="Learning progress tracking and study management")


@app.command()
def import_anki_reviews(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus to associate with"),
    student_id: str = typer.Option(..., help="Unique student identifier"),
    reviews_file: str = typer.Argument(..., help="Path to JSON file with Anki review data"),
    data_dir: str = typer.Option("data/progress", help="Directory to store progress data")
) -> None:
    """Import Anki review data from a JSON file."""
    try:
        tracker = ProgressTracker(data_dir)
        
        with open(reviews_file, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)

        anki_reviews = [AnkiPerformance(**review) for review in reviews_data]
        
        tracker.import_anki_reviews(syllabus_id, student_id, anki_reviews)
        
        print(f"✅ Successfully imported {len(anki_reviews)} Anki reviews for syllabus '{syllabus_id}'.")
        print(f"   Student ID: {student_id}")

    except FileNotFoundError:
        print(f"❌ Error: The file '{reviews_file}' was not found.")
        raise typer.Exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{reviews_file}'. Please ensure it's a valid JSON file.")
        raise typer.Exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise typer.Exit(1)


@app.command()
def start_tracking(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus to track"),
    student_id: str = typer.Option(..., help="Unique student identifier"),
    data_dir: str = typer.Option("data/progress", help="Directory to store progress data")
) -> None:
    """Start tracking progress for a syllabus."""
    try:
        tracker = ProgressTracker(data_dir)
        progress = tracker.start_tracking(syllabus_id, student_id)

        print(f"✅ Started tracking progress for syllabus '{syllabus_id}'")
        print(f"   Student ID: {student_id}")
        print(f"   Start Date: {progress.start_date}")
        print(f"   Progress file: {data_dir}/{syllabus_id}_{student_id}_progress.json")

    except Exception as e:
        print(f"❌ Error starting progress tracking: {e}")
        raise typer.Exit(1)


@app.command()
def log_session(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    unit_id: str = typer.Option(..., help="Unit ID being studied"),
    objective_id: str = typer.Option(..., help="Learning objective ID"),
    duration_actual: int = typer.Option(..., help="Actual study time in minutes"),
    completed: bool = typer.Option(True, help="Whether the session was completed"),
    difficulty_rating: Optional[int] = typer.Option(None, help="Difficulty rating (1-5)"),
    understanding_level: Optional[int] = typer.Option(None, help="Understanding level (1-5)"),
    notes: str = typer.Option("", help="Study session notes"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Log a completed study session."""
    try:
        if difficulty_rating and not (1 <= difficulty_rating <= 5):
            raise ValueError("Difficulty rating must be between 1 and 5")
        if understanding_level and not (1 <= understanding_level <= 5):
            raise ValueError("Understanding level must be between 1 and 5")

        tracker = ProgressTracker(data_dir)

        session = StudySession(
            id=f"{student_id}_{objective_id}_{unit_id}",
            syllabus_id=syllabus_id,
            unit_id=unit_id,
            objective_id=objective_id,
            scheduled_date="",  # Would be set from schedule
            duration_planned=0,  # Would be set from schedule
            duration_actual=duration_actual,
            completed=completed,
            notes=notes,
            difficulty_rating=difficulty_rating,
            understanding_level=understanding_level
        )

        tracker.log_session(session)

        print("✅ Study session logged successfully")
        print(f"   Syllabus: {syllabus_id}")
        print(f"   Unit: {unit_id}")
        print(f"   Objective: {objective_id}")
        print(f"   Duration: {duration_actual} minutes")
        print(f"   Completed: {completed}")

        if difficulty_rating and understanding_level:
            print(f"   Difficulty Rating: {difficulty_rating}/5")
            print(f"   Understanding Level: {understanding_level}/5")

    except Exception as e:
        print(f"❌ Error logging session: {e}")
        raise typer.Exit(1)


@app.command()
def get_report(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Get a comprehensive progress report."""
    try:
        tracker = ProgressTracker(data_dir)
        report = tracker.get_progress_report(syllabus_id, student_id)

        if "error" in report:
            print(f"❌ {report['error']}")
            raise typer.Exit(1)

        print(f"📊 Progress Report for {syllabus_id}")
        print(f"   Student: {student_id}")
        print("=" * 60)

        overall = report["overall_progress"]
        print("\n🎯 Overall Progress:")
        print(f"   Completion Rate: {overall['completion_rate']}%")
        print(f"   Sessions Completed: {overall['completed_sessions']}/{overall['total_sessions']}")
        print(f"   Total Study Time: {overall['total_study_time']} minutes")
        print(f"   Average Session Time: {overall['average_session_time']:.1f} minutes")
        print(f"   Current Streak: {overall['current_streak']} days")

        metrics = report["performance_metrics"]
        print("\n📈 Performance Metrics:")
        print(f"   Average Difficulty: {metrics['average_difficulty']}/5")
        print(f"   Average Understanding: {metrics['average_understanding']}/5")

        print("\n📚 Unit Breakdown:")
        for unit_id, unit_data in report["unit_breakdown"].items():
            print(f"   {unit_id}: {unit_data['completion_rate']}% complete, {unit_data['total_time']} min")

        if report["achievements"]:
            print("\n🏆 Achievements:")
            for achievement in report["achievements"]:
                print(f"   ✓ {achievement}")

        if report["challenges"]:
            print("\n⚠️  Challenges:")
            for challenge in report["challenges"]:
                print(f"   • {challenge}")

    except Exception as e:
        print(f"❌ Error getting report: {e}")
        raise typer.Exit(1)


@app.command()
def get_performance_report(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Generate a performance report with weak/strong topics."""
    try:
        tracker = ProgressTracker(data_dir)
        report = tracker.generate_performance_report(syllabus_id, student_id)

        print(f"🚀 Performance Report for {report.student_id} on Syllabus '{report.syllabus_id}'")
        print(f"   Report Date: {report.report_date}")
        print("=" * 60)
        
        print(f"\n📈 Overall Completion Rate: {report.overall_completion_rate}%")
        
        if report.weak_topics:
            print("\n⚠️  Topics to Focus On:")
            for topic, score in report.weak_topics.items():
                print(f"   - {topic} (Performance Score: {score:.2f})")
        
        if report.strong_topics:
            print("\n✅ Strong Topics:")
            for topic, score in report.strong_topics.items():
                print(f"   - {topic} (Performance Score: {score:.2f})")

        if not report.weak_topics and not report.strong_topics:
             print("\n📊 No specific weak or strong topics identified. Keep up the consistent work!")

        print("\n📝 Detailed Feedback:")
        for line in report.detailed_feedback:
            print(f"   - {line}")

    except Exception as e:
        print(f"❌ Error generating performance report: {e}")
        raise typer.Exit(1)


@app.command()
def add_achievement(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    achievement: str = typer.Option(..., help="Achievement description"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Add an achievement to the student's progress."""
    try:
        tracker = ProgressTracker(data_dir)
        tracker.update_achievement(syllabus_id, student_id, achievement)

        print(f"✅ Achievement added: {achievement}")
        print(f"   Syllabus: {syllabus_id}")
        print(f"   Student: {student_id}")

    except Exception as e:
        print(f"❌ Error adding achievement: {e}")
        raise typer.Exit(1)


@app.command()
def log_challenge(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    challenge: str = typer.Option(..., help="Challenge or difficulty description"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Log a challenge or difficulty encountered."""
    try:
        tracker = ProgressTracker(data_dir)
        tracker.log_challenge(syllabus_id, student_id, challenge)

        print(f"✅ Challenge logged: {challenge}")
        print(f"   Syllabus: {syllabus_id}")
        print(f"   Student: {student_id}")

    except Exception as e:
        print(f"❌ Error logging challenge: {e}")
        raise typer.Exit(1)


@app.command()
def generate_schedule(
    syllabus_file: str = typer.Option(..., help="Path to syllabus JSON file"),
    student_id: str = typer.Option(..., help="Student identifier"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Generate study sessions from syllabus schedule."""
    try:
        # Load syllabus schedule
        with open(syllabus_file.replace('.json', '_schedule.json'), 'r', encoding='utf-8') as f:
            schedule = json.load(f)

        tracker = ProgressTracker(data_dir)
        sessions = tracker.generate_study_schedule(schedule, student_id)

        print(f"📅 Generated {len(sessions)} study sessions for {student_id}")
        print(f"   Syllabus: {schedule['syllabus_id']}")
        print("=" * 60)

        # Group by unit
        unit_sessions = {}
        for session in sessions:
            if session.unit_id not in unit_sessions:
                unit_sessions[session.unit_id] = []
            unit_sessions[session.unit_id].append(session)

        for unit_id, sessions_list in unit_sessions.items():
            print(f"\n📚 {unit_id} ({len(sessions_list)} sessions):")
            for session in sessions_list[:3]:  # Show first 3 per unit
                print(f"   • {session.objective_id}: {session.duration_planned} min")
            if len(sessions_list) > 3:
                print(f"   ... and {len(sessions_list) - 3} more sessions")

        # Save sessions (would integrate with actual scheduling system)
        print("\n💡 Note: Use 'log-session' command to record completed study sessions")

    except Exception as e:
        print(f"❌ Error generating schedule: {e}")
        raise typer.Exit(1)


@app.command()
def export_progress(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    output_file: Optional[str] = typer.Option(None, help="Output file path"),
    data_dir: str = typer.Option("data/progress", help="Progress data directory")
) -> None:
    """Export progress data to JSON format."""
    try:
        tracker = ProgressTracker(data_dir)
        report = tracker.get_progress_report(syllabus_id, student_id)

        if "error" in report:
            print(f"❌ {report['error']}")
            raise typer.Exit(1)

        if output_file is None:
            output_file = f"{syllabus_id}_{student_id}_progress_export.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Progress data exported to: {output_file}")

        # Print summary
        overall = report["overall_progress"]
        print("\n📊 Export Summary:")
        print(f"   Completion Rate: {overall['completion_rate']}%")
        print(f"   Study Sessions: {overall['total_sessions']}")
        print(f"   Total Time: {overall['total_study_time']} minutes")

    except Exception as e:
        print(f"❌ Error exporting progress: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
