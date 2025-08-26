from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .practice_based_coaching import PracticeBasedCoachingManager, CoachingCycle

app = typer.Typer(help="Practice Based Coaching and staff development")


@app.command()
def create_cycle(
    teacher_id: str = typer.Option(..., help="Teacher identifier"),
    coach_id: str = typer.Option(..., help="Coach identifier"),
    focus_area: str = typer.Option(..., help="Focus area for coaching (e.g., classroom management, instructional strategies)"),
    current_level: str = typer.Option(..., help="Current level of practice (emerging, developing, proficient)"),
    goal_level: str = typer.Option("proficient", help="Goal level of practice"),
    duration_weeks: int = typer.Option(8, help="Coaching cycle duration in weeks"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Create a new Practice Based Coaching cycle."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        cycle = manager.create_coaching_cycle(
            teacher_id=teacher_id,
            coach_id=coach_id,
            focus_area=focus_area,
            current_level=current_level,
            goal_level=goal_level,
            duration_weeks=duration_weeks
        )

        print(f"✅ Practice Based Coaching cycle created successfully!")
        print(f"   Cycle ID: {cycle.id}")
        print(f"   Teacher: {cycle.teacher_id}")
        print(f"   Coach: {cycle.coach_id}")
        print(f"   Focus Area: {cycle.focus_area}")
        print(f"   Current Level: {cycle.current_level}")
        print(f"   Goal Level: {cycle.goal_level}")
        print(f"   Duration: {duration_weeks} weeks")
        print(f"   Strategies: {len(cycle.strategies)}")
        print(f"   Action Steps: {len(cycle.action_steps)}")

    except Exception as e:
        print(f"❌ Error creating coaching cycle: {e}")
        raise typer.Exit(1)


@app.command()
def log_session(
    cycle_id: str = typer.Option(..., help="Coaching cycle identifier"),
    session_type: str = typer.Option(..., help="Session type: planning, observation, feedback, reflection, check_in"),
    duration_minutes: int = typer.Option(60, help="Session duration in minutes"),
    location: str = typer.Option("classroom", help="Session location: classroom, office, remote"),
    agenda_items: str = typer.Option(..., help="Comma-separated list of agenda items"),
    discussion_topics: str = typer.Option(..., help="Comma-separated list of discussion topics"),
    teacher_reflections: str = typer.Option(..., help="Comma-separated list of teacher reflections"),
    coach_feedback: str = typer.Option(..., help="Comma-separated list of coach feedback"),
    action_items: str = typer.Option(..., help="Comma-separated list of action items"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Log a coaching session."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        # Parse comma-separated values
        agenda_list = [item.strip() for item in agenda_items.split(",")]
        discussion_list = [topic.strip() for topic in discussion_topics.split(",")]
        reflections_list = [ref.strip() for ref in teacher_reflections.split(",")]
        feedback_list = [fb.strip() for fb in coach_feedback.split(",")]
        actions_list = [action.strip() for action in action_items.split(",")]

        session = manager.log_coaching_session(
            cycle_id=cycle_id,
            session_type=session_type,
            duration_minutes=duration_minutes,
            location=location,
            agenda_items=agenda_list,
            discussion_topics=discussion_list,
            teacher_reflections=reflections_list,
            coach_feedback=feedback_list,
            action_items=actions_list
        )

        print(f"✅ Coaching session logged successfully!")
        print(f"   Session ID: {session.id}")
        print(f"   Cycle: {cycle_id}")
        print(f"   Type: {session.session_type}")
        print(f"   Duration: {session.duration_minutes} minutes")
        print(f"   Location: {session.location}")
        print(f"   Date: {session.session_date}")
        print(f"   Agenda Items: {len(session.agenda_items)}")
        print(f"   Teacher Reflections: {len(session.teacher_reflections)}")
        print(f"   Coach Feedback: {len(session.coach_feedback)}")
        print(f"   Action Items: {len(session.action_items)}")

    except Exception as e:
        print(f"❌ Error logging coaching session: {e}")
        raise typer.Exit(1)


@app.command()
def update_progress(
    cycle_id: str = typer.Option(..., help="Coaching cycle identifier"),
    progress_notes: str = typer.Option(..., help="Progress notes and observations"),
    challenges: str = typer.Option("", help="Comma-separated list of challenges encountered"),
    new_action_items: str = typer.Option("", help="Comma-separated list of new action items"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Update coaching cycle progress."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        challenges_list = [c.strip() for c in challenges.split(",") if c.strip()]
        actions_list = [a.strip() for a in new_action_items.split(",") if a.strip()]

        manager.update_coaching_cycle_progress(
            cycle_id=cycle_id,
            progress_notes=progress_notes,
            challenges=challenges_list,
            new_action_items=actions_list
        )

        print(f"✅ Coaching cycle progress updated successfully!")
        print(f"   Cycle: {cycle_id}")
        print(f"   Progress Notes: Added")
        print(f"   Challenges: {len(challenges_list)}")
        print(f"   New Action Items: {len(actions_list)}")

    except Exception as e:
        print(f"❌ Error updating progress: {e}")
        raise typer.Exit(1)


@app.command()
def complete_cycle(
    cycle_id: str = typer.Option(..., help="Coaching cycle identifier"),
    outcome_notes: str = typer.Option(..., help="Outcome notes and final reflections"),
    achieved_level: str = typer.Option("", help="Achieved level of practice"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Mark a coaching cycle as completed."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        final_level = achieved_level if achieved_level else None

        manager.complete_coaching_cycle(
            cycle_id=cycle_id,
            outcome_notes=outcome_notes,
            achieved_level=final_level
        )

        print(f"✅ Coaching cycle completed successfully!")
        print(f"   Cycle: {cycle_id}")
        print(f"   Status: Completed")

        if final_level:
            print(f"   Achieved Level: {final_level}")

        print(f"   Outcome Notes: {len(outcome_notes)} characters")

    except Exception as e:
        print(f"❌ Error completing coaching cycle: {e}")
        raise typer.Exit(1)


@app.command()
def generate_report(
    cycle_id: str = typer.Option(..., help="Coaching cycle identifier"),
    output_file: Optional[str] = typer.Option(None, help="Output file path"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Generate a comprehensive coaching cycle report."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        report = manager.generate_coaching_report(cycle_id)

        if "error" in report:
            print(f"❌ {report['error']}")
            raise typer.Exit(1)

        # Determine output file
        if output_file is None:
            output_file = f"coaching_{cycle_id}_report.json"

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Coaching report generated successfully!")
        print(f"   Cycle: {cycle_id}")
        print(f"   Report saved to: {output_file}")
        print(f"   Generated at: {report['generated_at']}")

        # Print key metrics
        metrics = report.get('progress_metrics', {})
        if metrics:
            print("\n📊 Key Metrics:")
            print(f"   Overall Progress: {metrics.get('overall_progress_percentage', 0)}%")
            print(f"   Sessions Completed: {metrics.get('sessions_completed', 0)}")
            print(f"   Evidence Collected: {metrics.get('evidence_collected', 0)}")
            print(f"   Challenges Addressed: {metrics.get('challenges_addressed', 0)}")

        session_summary = report.get('session_summary', {})
        if session_summary:
            print("\n📅 Session Summary:")
            print(f"   Total Sessions: {session_summary.get('total_sessions', 0)}")
            print(f"   Total Time: {session_summary.get('total_time', 0)} minutes")

    except Exception as e:
        print(f"❌ Error generating coaching report: {e}")
        raise typer.Exit(1)


@app.command()
def list_cycles(
    teacher_id: Optional[str] = typer.Option(None, help="Filter by teacher ID"),
    coach_id: Optional[str] = typer.Option(None, help="Filter by coach ID"),
    status: Optional[str] = typer.Option(None, help="Filter by status (active, completed, paused)"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """List coaching cycles with optional filtering."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        # Get all cycle files
        cycle_files = list(Path(data_dir).glob("cycle_*.json"))

        if not cycle_files:
            print("📋 No coaching cycles found")
            return

        cycles = []
        for cycle_file in cycle_files:
            try:
                cycle_data = json.loads(cycle_file.read_text())
                cycle = CoachingCycle(**cycle_data)

                # Apply filters
                if teacher_id and cycle.teacher_id != teacher_id:
                    continue
                if coach_id and cycle.coach_id != coach_id:
                    continue
                if status and cycle.status != status:
                    continue

                cycles.append(cycle)
            except Exception:
                continue

        if not cycles:
            print("📋 No coaching cycles match the specified filters")
            return

        print(f"🎯 Coaching Cycles ({len(cycles)} total)")
        print("=" * 80)

        for cycle in sorted(cycles, key=lambda x: x.start_date, reverse=True):
            print(f"🔄 {cycle.id}")
            print(f"   Teacher: {cycle.teacher_id} | Coach: {cycle.coach_id}")
            print(f"   Focus: {cycle.focus_area}")
            print(f"   Level: {cycle.current_level} → {cycle.goal_level}")
            print(f"   Start: {cycle.start_date}")
            if cycle.target_completion_date:
                print(f"   Target Completion: {cycle.target_completion_date}")
            if cycle.completion_date:
                print(f"   Actual Completion: {cycle.completion_date}")
            print(f"   Status: {cycle.status}")

            if cycle.strategies:
                print(f"   📚 Strategies: {len(cycle.strategies)}")
            if cycle.action_steps:
                print(f"   ✅ Action Steps: {len(cycle.action_steps)}")
            if cycle.evidence_of_progress:
                print(f"   📈 Evidence: {len(cycle.evidence_of_progress)}")

            print()

    except Exception as e:
        print(f"❌ Error listing coaching cycles: {e}")
        raise typer.Exit(1)


@app.command()
def get_teacher_history(
    teacher_id: str = typer.Option(..., help="Teacher identifier"),
    data_dir: str = typer.Option("data/coaching", help="Data directory")
) -> None:
    """Get coaching history for a specific teacher."""
    try:
        manager = PracticeBasedCoachingManager(data_dir)

        cycles = manager.get_teacher_coaching_history(teacher_id)

        if not cycles:
            print(f"📋 No coaching history found for teacher {teacher_id}")
            return

        print(f"📚 Coaching History for {teacher_id}")
        print("=" * 60)

        active_cycles = [c for c in cycles if c.status == "active"]
        completed_cycles = [c for c in cycles if c.status == "completed"]

        print(f"🎯 Active Cycles: {len(active_cycles)}")
        print(f"✅ Completed Cycles: {len(completed_cycles)}")
        print(f"📊 Total Cycles: {len(cycles)}")

        if active_cycles:
            print("\n🔄 Active Coaching:")
            for cycle in active_cycles:
                print(f"   • {cycle.focus_area} ({cycle.current_level} → {cycle.goal_level})")

        if completed_cycles:
            print("\n✅ Completed Coaching:")
            for cycle in completed_cycles[:5]:  # Show last 5
                print(f"   • {cycle.focus_area} (Completed: {cycle.completion_date})")

        # Show focus areas
        focus_areas = {}
        for cycle in cycles:
            focus_areas[cycle.focus_area] = focus_areas.get(cycle.focus_area, 0) + 1

        if focus_areas:
            print("\n🎯 Focus Areas:")
            for area, count in sorted(focus_areas.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {area}: {count} cycle(s)")

    except Exception as e:
        print(f"❌ Error getting teacher history: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
