from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .child_assessment import ChildAssessmentManager, ChildProfile

app = typer.Typer(help="Child assessment and progress tracking")


@app.command()
def create_profile(
    first_name: str = typer.Option(..., help="Child's first name"),
    last_name: str = typer.Option(..., help="Child's last name"),
    date_of_birth: str = typer.Option(..., help="Date of birth (YYYY-MM-DD)"),
    classroom_id: str = typer.Option(..., help="Classroom identifier"),
    primary_language: str = typer.Option("English", help="Primary language"),
    special_needs: str = typer.Option("", help="Comma-separated list of special needs"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Create a new child profile."""
    try:
        manager = ChildAssessmentManager(data_dir)

        # Parse special needs
        special_needs_list = [need.strip() for need in special_needs.split(",") if need.strip()]

        profile = manager.create_child_profile(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            classroom_id=classroom_id,
            primary_language=primary_language,
            special_needs=special_needs_list
        )

        print(f"✅ Child profile created successfully!")
        print(f"   Profile ID: {profile.id}")
        print(f"   Name: {profile.first_name} {profile.last_name}")
        print(f"   Age: {manager._calculate_age(profile.date_of_birth)} years")
        print(f"   Classroom: {profile.classroom_id}")
        print(f"   Enrollment Date: {profile.enrollment_date}")
        print(f"   Primary Language: {profile.primary_language}")

        if special_needs_list:
            print(f"   Special Needs: {len(special_needs_list)}")

    except Exception as e:
        print(f"❌ Error creating child profile: {e}")
        raise typer.Exit(1)


@app.command()
def conduct_assessment(
    child_id: str = typer.Option(..., help="Child identifier"),
    assessor_id: str = typer.Option(..., help="Assessor identifier"),
    tool_id: str = typer.Option(..., help="Assessment tool identifier (asq, ts_gold, etc.)"),
    scores: str = typer.Option(..., help="JSON string of domain scores"),
    observations: str = typer.Option(..., help="Comma-separated list of observations"),
    strengths: str = typer.Option(..., help="Comma-separated list of strengths"),
    areas_for_concern: str = typer.Option(..., help="Comma-separated list of areas for concern"),
    recommendations: str = typer.Option(..., help="Comma-separated list of recommendations"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Conduct an assessment for a child."""
    try:
        manager = ChildAssessmentManager(data_dir)

        # Parse JSON scores
        try:
            scores_dict = json.loads(scores)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for scores. Use format: '{\"cognitive\": 4.5, \"language\": 3.8}'")
            raise typer.Exit(1)

        # Parse lists
        observations_list = [obs.strip() for obs in observations.split(",")]
        strengths_list = [str.strip() for str in strengths.split(",")]
        concerns_list = [area.strip() for area in areas_for_concern.split(",")]
        recommendations_list = [rec.strip() for rec in recommendations.split(",")]

        assessment = manager.conduct_assessment(
            child_id=child_id,
            assessor_id=assessor_id,
            tool_id=tool_id,
            scores=scores_dict,
            observations=observations_list,
            strengths=strengths_list,
            areas_for_concern=concerns_list,
            recommendations=recommendations_list
        )

        print(f"✅ Assessment conducted successfully!")
        print(f"   Assessment ID: {assessment.id}")
        print(f"   Child: {assessment.child_id}")
        print(f"   Tool: {assessment.tool_id}")
        print(f"   Date: {assessment.assessment_date}")
        print(f"   Age at Assessment: {assessment.age_at_assessment} years")
        print(f"   Domains Assessed: {len(assessment.scores)}")
        print(f"   Observations: {len(assessment.observations)}")
        print(f"   Strengths: {len(assessment.strengths)}")
        print(f"   Areas for Concern: {len(assessment.areas_for_concern)}")
        print(f"   Recommendations: {len(assessment.recommendations)}")

        if assessment.next_assessment_date:
            print(f"   Next Assessment Due: {assessment.next_assessment_date}")

    except Exception as e:
        print(f"❌ Error conducting assessment: {e}")
        raise typer.Exit(1)


@app.command()
def create_objective(
    child_id: str = typer.Option(..., help="Child identifier"),
    objective: str = typer.Option(..., help="Learning objective description"),
    domain: str = typer.Option(..., help="Developmental domain (cognitive, language, social_emotional, physical, approaches_to_learning)"),
    target_level: str = typer.Option("proficient", help="Target level (emerging, developing, proficient, advanced)"),
    strategies: str = typer.Option("", help="Comma-separated list of strategies"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Create a learning objective for a child."""
    try:
        manager = ChildAssessmentManager(data_dir)

        strategies_list = [strat.strip() for strat in strategies.split(",") if strat.strip()]

        learning_obj = manager.create_learning_objective(
            child_id=child_id,
            objective=objective,
            domain=domain,
            target_level=target_level,
            strategies=strategies_list
        )

        print(f"✅ Learning objective created successfully!")
        print(f"   Objective ID: {learning_obj.id}")
        print(f"   Child: {learning_obj.child_id}")
        print(f"   Objective: {learning_obj.objective}")
        print(f"   Domain: {learning_obj.domain}")
        print(f"   Current Level: {learning_obj.current_level}")
        print(f"   Target Level: {learning_obj.target_level}")
        print(f"   Strategies: {len(learning_obj.strategies)}")

    except Exception as e:
        print(f"❌ Error creating learning objective: {e}")
        raise typer.Exit(1)


@app.command()
def update_progress(
    objective_id: str = typer.Option(..., help="Learning objective identifier"),
    progress_note: str = typer.Option(..., help="Progress note or observation"),
    new_level: str = typer.Option("", help="New current level (emerging, developing, proficient, advanced)"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Update progress on a learning objective."""
    try:
        manager = ChildAssessmentManager(data_dir)

        final_level = new_level if new_level else None

        manager.update_learning_progress(
            objective_id=objective_id,
            progress_note=progress_note,
            new_level=final_level
        )

        print(f"✅ Learning progress updated successfully!")
        print(f"   Objective: {objective_id}")
        print(f"   Progress Note: Added")

        if final_level:
            print(f"   New Level: {final_level}")

    except Exception as e:
        print(f"❌ Error updating progress: {e}")
        raise typer.Exit(1)


@app.command()
def generate_report(
    child_id: str = typer.Option(..., help="Child identifier"),
    report_period: str = typer.Option("quarterly", help="Report period (quarterly, annual, monthly)"),
    output_file: Optional[str] = typer.Option(None, help="Output file path"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Generate a comprehensive progress report for a child."""
    try:
        manager = ChildAssessmentManager(data_dir)

        report = manager.generate_progress_report(
            child_id=child_id,
            report_period=report_period
        )

        # Determine output file
        if output_file is None:
            output_file = f"progress_{child_id}_{report_period}_report.json"

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "id": report.id,
                "child_id": report.child_id,
                "report_period": report.report_period,
                "start_date": report.start_date,
                "end_date": report.end_date,
                "overall_summary": report.overall_summary,
                "domain_summaries": report.domain_summaries,
                "achievements": report.achievements,
                "goals": report.goals,
                "recommendations": report.recommendations,
                "parent_signature_date": report.parent_signature_date,
                "teacher_signature_date": report.teacher_signature_date
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ Progress report generated successfully!")
        print(f"   Child: {report.child_id}")
        print(f"   Report Period: {report.report_period}")
        print(f"   Start Date: {report.start_date}")
        print(f"   End Date: {report.end_date}")
        print(f"   Report saved to: {output_file}")

        # Print key metrics
        if report.achievements:
            print(f"   🏆 Achievements: {len(report.achievements)}")

        if report.goals:
            print(f"   🎯 Goals: {len(report.goals)}")

        if report.recommendations:
            print(f"   💡 Recommendations: {len(report.recommendations)}")

    except Exception as e:
        print(f"❌ Error generating progress report: {e}")
        raise typer.Exit(1)


@app.command()
def get_database_summary(
    child_id: str = typer.Option(..., help="Child identifier"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """Get comprehensive database summary for a child."""
    try:
        manager = ChildAssessmentManager(data_dir)

        summary = manager.get_child_database_summary(child_id)

        if "error" in summary:
            print(f"❌ {summary['error']}")
            raise typer.Exit(1)

        profile = summary["child_profile"]

        print(f"📊 Database Summary for {profile['name']}")
        print("=" * 60)

        print("👶 Child Information:")
        print(f"   ID: {profile['id']}")
        print(f"   Age: {profile['age']} years")
        print(f"   Classroom: {profile['classroom']}")
        print(f"   Enrollment Date: {profile['enrollment_date']}")

        print("\n📋 Assessment Summary:")
        assess_summary = summary["assessment_summary"]
        print(f"   Total Assessments: {assess_summary['total_assessments']}")
        if assess_summary['latest_assessment']:
            print(f"   Latest Assessment: {assess_summary['latest_assessment']}")
        if assess_summary['next_assessment']:
            print(f"   Next Assessment Due: {assess_summary['next_assessment']}")

        print("\n🎯 Learning Objectives:")
        obj_summary = summary["learning_objectives"]
        print(f"   Total Objectives: {obj_summary['total']}")
        print(f"   Active Objectives: {obj_summary['active']}")
        print(f"   Achieved Objectives: {obj_summary['achieved']}")
        if obj_summary['domains']:
            print(f"   Domains: {', '.join(obj_summary['domains'])}")

        print("\n📄 Progress Reports:")
        report_summary = summary["progress_reports"]
        print(f"   Total Reports: {report_summary['total']}")
        if report_summary['latest']:
            print(f"   Latest Report: {report_summary['latest']}")

        print("\n📊 Data Completeness:")
        completeness = summary["data_completeness"]
        print(f"   {completeness}% complete")

    except Exception as e:
        print(f"❌ Error getting database summary: {e}")
        raise typer.Exit(1)


@app.command()
def list_tools() -> None:
    """List available assessment tools."""
    try:
        manager = ChildAssessmentManager()

        print("🔧 Available Assessment Tools")
        print("=" * 50)

        for tool_id, tool in manager.assessment_tools.items():
            print(f"\n📝 {tool.name} ({tool_id})")
            print(f"   {tool.description}")
            print(f"   Age Range: {tool.age_range}")
            print(f"   Domains: {', '.join(tool.domains)}")
            print(f"   Administration Time: {tool.administration_time} minutes")
            print(f"   Frequency: {tool.frequency}")
            print(f"   Scoring: {tool.scoring_method}")
            print(f"   Standards: {', '.join(tool.standards_alignment)}")

    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        raise typer.Exit(1)


@app.command()
def list_children(
    classroom_id: Optional[str] = typer.Option(None, help="Filter by classroom ID"),
    data_dir: str = typer.Option("data/assessments", help="Data directory")
) -> None:
    """List children with optional filtering."""
    try:
        manager = ChildAssessmentManager(data_dir)

        # Get all profile files
        profile_files = list(Path(data_dir).glob("profile_*.json"))

        if not profile_files:
            print("👶 No child profiles found")
            return

        children = []
        for profile_file in profile_files:
            try:
                profile_data = json.loads(profile_file.read_text())
                child = ChildProfile(**profile_data)

                # Apply filters
                if classroom_id and child.classroom_id != classroom_id:
                    continue

                children.append(child)
            except Exception:
                continue

        if not children:
            print("👶 No children match the specified filters")
            return

        print(f"👶 Children ({len(children)} total)")
        print("=" * 80)

        for child in sorted(children, key=lambda x: x.enrollment_date, reverse=True):
            age = manager._calculate_age(child.date_of_birth)
            print(f"🧒 {child.id}")
            print(f"   Name: {child.first_name} {child.last_name}")
            print(f"   Age: {age} years")
            print(f"   Classroom: {child.classroom_id}")
            print(f"   Enrollment: {child.enrollment_date}")
            print(f"   Language: {child.primary_language}")

            if child.special_needs:
                print(f"   Special Needs: {len(child.special_needs)}")
            if child.ifsp_iep:
                print(f"   IFSP/IEP: Yes")

            print()

    except Exception as e:
        print(f"❌ Error listing children: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
