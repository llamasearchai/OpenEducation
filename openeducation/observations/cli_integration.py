from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .observation_tools import ObservationToolsManager, ClassroomObservation

app = typer.Typer(help="Classroom observation and data collection tools")


@app.command()
def create_observation(
    classroom_id: str = typer.Option(..., help="Classroom identifier"),
    teacher_id: str = typer.Option(..., help="Teacher identifier"),
    observer_id: str = typer.Option(..., help="Observer identifier"),
    focus_area: str = typer.Option("curriculum", help="Focus area: curriculum, instruction, environment, interactions"),
    duration_minutes: int = typer.Option(30, help="Observation duration in minutes"),
    data_dir: str = typer.Option("data/observations", help="Data directory")
) -> None:
    """Create a new classroom observation."""
    try:
        manager = ObservationToolsManager(data_dir)

        observation = manager.create_observation(
            classroom_id=classroom_id,
            teacher_id=teacher_id,
            observer_id=observer_id,
            focus_area=focus_area,
            duration_minutes=duration_minutes
        )

        print(f"✅ Classroom observation created successfully!")
        print(f"   Observation ID: {observation.id}")
        print(f"   Classroom: {observation.classroom_id}")
        print(f"   Teacher: {observation.teacher_id}")
        print(f"   Focus Area: {observation.focus_area}")
        print(f"   Duration: {observation.duration_minutes} minutes")
        print(f"   Date: {observation.observation_date}")
        print(f"   Status: {observation.status}")

    except Exception as e:
        print(f"❌ Error creating observation: {e}")
        raise typer.Exit(1)


@app.command()
def record_criteria_score(
    observation_id: str = typer.Argument(..., help="Observation identifier"),
    criteria_id: str = typer.Option(..., help="Criteria identifier (e.g., env_1, int_1)"),
    score: str = typer.Option(..., help="Score value"),
    notes: str = typer.Option("", help="Optional notes"),
    data_dir: str = typer.Option("data/observations", help="Data directory")
) -> None:
    """Record a score for observation criteria."""
    try:
        manager = ObservationToolsManager(data_dir)

        # Parse score based on criteria type
        try:
            # Try numeric score first
            score_value = float(score)
        except ValueError:
            # Use string score for non-numeric values
            score_value = score

        manager.record_criteria_score(
            observation_id=observation_id,
            criteria_id=criteria_id,
            score=score_value,
            notes=notes
        )

        print(f"✅ Criteria score recorded successfully!")
        print(f"   Observation: {observation_id}")
        print(f"   Criteria: {criteria_id}")
        print(f"   Score: {score_value}")

    except Exception as e:
        print(f"❌ Error recording criteria score: {e}")
        raise typer.Exit(1)


@app.command()
def complete_observation(
    observation_id: str = typer.Argument(..., help="Observation identifier"),
    strengths: str = typer.Option(..., help="Comma-separated list of strengths"),
    areas_for_growth: str = typer.Option(..., help="Comma-separated list of areas for growth"),
    recommendations: str = typer.Option(..., help="Comma-separated list of recommendations"),
    follow_up_date: Optional[str] = typer.Option(None, help="Follow-up date (YYYY-MM-DD)"),
    data_dir: str = typer.Option("data/observations", help="Data directory")
) -> None:
    """Complete an observation with summary data."""
    try:
        manager = ObservationToolsManager(data_dir)

        strengths_list = [s.strip() for s in strengths.split(",")]
        growth_list = [g.strip() for g in areas_for_growth.split(",")]
        recommendations_list = [r.strip() for r in recommendations.split(",")]

        manager.complete_observation(
            observation_id=observation_id,
            strengths=strengths_list,
            areas_for_growth=growth_list,
            recommendations=recommendations_list,
            follow_up_date=follow_up_date
        )

        print(f"✅ Observation completed successfully!")
        print(f"   Observation: {observation_id}")
        print(f"   Strengths: {len(strengths_list)}")
        print(f"   Areas for Growth: {len(growth_list)}")
        print(f"   Recommendations: {len(recommendations_list)}")

        if follow_up_date:
            print(f"   Follow-up Date: {follow_up_date}")

    except Exception as e:
        print(f"❌ Error completing observation: {e}")
        raise typer.Exit(1)


@app.command()
def generate_report(
    observation_id: str = typer.Argument(..., help="Observation identifier"),
    output_file: Optional[str] = typer.Option(None, help="Output file path"),
    data_dir: str = typer.Option("data/observations", help="Data directory")
) -> None:
    """Generate a comprehensive observation report."""
    try:
        manager = ObservationToolsManager(data_dir)

        report = manager.generate_observation_report(observation_id)

        if "error" in report:
            print(f"❌ {report['error']}")
            raise typer.Exit(1)

        # Determine output file
        if output_file is None:
            output_file = f"observation_{observation_id}_report.json"

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Observation report generated successfully!")
        print(f"   Observation: {observation_id}")
        print(f"   Report saved to: {output_file}")
        print(f"   Generated at: {report['generated_at']}")

        # Print key metrics
        scores = report.get('scores_summary', {})
        if scores.get('total_criteria', 0) > 0:
            print("\n📊 Key Metrics:")
            print(f"   Total Criteria: {scores['total_criteria']}")
            print(f"   Scored Criteria: {scores['scored_criteria']}")
            print(f"   Average Score: {scores['average_score']}")

        if report.get('strengths'):
            print(f"\n💪 Strengths: {len(report['strengths'])}")

        if report.get('recommendations'):
            print(f"💡 Recommendations: {len(report['recommendations'])}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        raise typer.Exit(1)


@app.command()
def list_observations(
    teacher_id: Optional[str] = typer.Option(None, help="Filter by teacher ID"),
    classroom_id: Optional[str] = typer.Option(None, help="Filter by classroom ID"),
    status: Optional[str] = typer.Option(None, help="Filter by status (draft, completed, reviewed)"),
    data_dir: str = typer.Option("data/observations", help="Data directory")
) -> None:
    """List classroom observations with optional filtering."""
    try:
        manager = ObservationToolsManager(data_dir)

        # Get all observation files
        obs_files = list(Path(data_dir).glob("observation_*.json"))

        if not obs_files:
            print("📋 No observations found")
            return

        observations = []
        for obs_file in obs_files:
            try:
                obs_data = json.loads(obs_file.read_text())
                observation = ClassroomObservation(**obs_data)

                # Apply filters
                if teacher_id and observation.teacher_id != teacher_id:
                    continue
                if classroom_id and observation.classroom_id != classroom_id:
                    continue
                if status and observation.status != status:
                    continue

                observations.append(observation)
            except Exception:
                continue

        if not observations:
            print("📋 No observations match the specified filters")
            return

        print(f"📋 Classroom Observations ({len(observations)} total)")
        print("=" * 80)

        for obs in sorted(observations, key=lambda x: x.observation_date, reverse=True):
            print(f"🔍 {obs.id}")
            print(f"   Classroom: {obs.classroom_id} | Teacher: {obs.teacher_id}")
            print(f"   Date: {obs.observation_date} | Duration: {obs.duration_minutes}min")
            print(f"   Focus: {obs.focus_area} | Status: {obs.status}")

            if obs.strengths:
                print(f"   💪 Strengths: {len(obs.strengths)}")
            if obs.areas_for_growth:
                print(f"   📈 Areas for Growth: {len(obs.areas_for_growth)}")
            if obs.recommendations:
                print(f"   💡 Recommendations: {len(obs.recommendations)}")

            print()

    except Exception as e:
        print(f"❌ Error listing observations: {e}")
        raise typer.Exit(1)


@app.command()
def show_criteria() -> None:
    """Show available observation criteria."""
    try:
        manager = ObservationToolsManager()

        print("🔍 Research-Based Observation Criteria")
        print("=" * 60)

        criteria = manager.observation_criteria

        for category, criteria_list in criteria.items():
            print(f"\n📂 {category.replace('_', ' ').title()}")
            print("-" * 40)

            for criterion in criteria_list:
                print(f"🔸 {criterion.id}: {criterion.name}")
                print(f"   {criterion.description}")
                print(f"   Indicators: {len(criterion.indicators)}")
                print(f"   Scoring: {criterion.scoring_method}")
                print(f"   Standard: {criterion.standard}")
                print()

    except Exception as e:
        print(f"❌ Error showing criteria: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
