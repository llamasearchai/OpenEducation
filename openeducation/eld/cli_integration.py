from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .eld_core import ELDManager, EnglishProficiencyLevel, ELDDomain

app = typer.Typer(help="English Language Development (ELD) instruction and support")


@app.command()
def create_profile(
    student_id: str = typer.Option(..., help="Student identifier"),
    current_level: str = typer.Option(..., help="Current proficiency level (Entering, Emerging, Developing, Expanding, Bridging, Reaching)"),
    primary_language: str = typer.Option(..., help="Primary language"),
    overall_score: float = typer.Option(..., help="Overall proficiency score (1.0-6.0)"),
    domain_scores: str = typer.Option(..., help="JSON string of domain scores"),
    program_entry_date: str = typer.Option(..., help="Program entry date (YYYY-MM-DD)"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Create a new ELD student profile."""
    try:
        manager = ELDManager(data_dir)

        # Parse proficiency level
        proficiency_level = EnglishProficiencyLevel(current_level)

        # Parse domain scores
        try:
            scores_dict = json.loads(domain_scores)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for domain scores. Use format: '{\"Social_Interpersonal\": 3.5, \"Instructional\": 2.8}'")
            raise typer.Exit(1)

        profile = manager.create_eld_profile(
            student_id=student_id,
            current_level=proficiency_level,
            primary_language=primary_language,
            overall_score=overall_score,
            domain_scores=scores_dict,
            program_entry_date=program_entry_date
        )

        print(f"✅ ELD profile created successfully!")
        print(f"   Profile ID: {profile.id}")
        print(f"   Student: {profile.student_id}")
        print(f"   Current Level: {profile.current_level.value}")
        print(f"   Overall Score: {profile.overall_score}")
        print(f"   Primary Language: {profile.primary_language}")
        print(f"   Program Entry: {profile.program_entry_date}")

    except Exception as e:
        print(f"❌ Error creating ELD profile: {e}")
        raise typer.Exit(1)


@app.command()
def create_lesson_plan(
    title: str = typer.Option(..., help="Lesson plan title"),
    proficiency_level: str = typer.Option(..., help="Target proficiency level"),
    domain: str = typer.Option(..., help="ELD domain (Social_Interpersonal, Instructional, Academic_Language)"),
    grade_level: str = typer.Option(..., help="Grade level"),
    duration_minutes: int = typer.Option(45, help="Lesson duration in minutes"),
    objective: str = typer.Option(..., help="Main lesson objective"),
    language_objectives: str = typer.Option(..., help="Comma-separated language objectives"),
    content_objectives: str = typer.Option(..., help="Comma-separated content objectives"),
    created_by: str = typer.Option(..., help="Creator identifier"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Create a comprehensive ELD lesson plan."""
    try:
        manager = ELDManager(data_dir)

        # Parse enums
        level = EnglishProficiencyLevel(proficiency_level)
        domain_enum = ELDDomain(domain.replace("_", " & "))

        # Parse objectives
        lang_objs = [obj.strip() for obj in language_objectives.split(",")]
        content_objs = [obj.strip() for obj in content_objectives.split(",")]

        lesson_plan = manager.create_lesson_plan(
            title=title,
            proficiency_level=level,
            domain=domain_enum,
            grade_level=grade_level,
            duration_minutes=duration_minutes,
            objective=objective,
            language_objectives=lang_objs,
            content_objectives=content_objs,
            created_by=created_by
        )

        print(f"✅ ELD lesson plan created successfully!")
        print(f"   Plan ID: {lesson_plan.id}")
        print(f"   Title: {lesson_plan.title}")
        print(f"   Level: {lesson_plan.proficiency_level.value}")
        print(f"   Domain: {lesson_plan.domain.value}")
        print(f"   Duration: {lesson_plan.duration_minutes} minutes")
        print(f"   Key Vocabulary: {len(lesson_plan.key_vocabulary)} words")
        print(f"   Strategies: {len(lesson_plan.instructional_strategies)}")
        print(f"   Assessment Methods: {len(lesson_plan.assessment_methods)}")

    except Exception as e:
        print(f"❌ Error creating lesson plan: {e}")
        raise typer.Exit(1)


@app.command()
def assess_progress(
    student_id: str = typer.Option(..., help="Student identifier"),
    assessment_type: str = typer.Option("progress", help="Assessment type (initial, progress, annual, exit)"),
    proficiency_level: str = typer.Option(..., help="Current proficiency level"),
    overall_score: float = typer.Option(..., help="Overall proficiency score"),
    domain_scores: str = typer.Option(..., help="JSON string of domain scores"),
    can_do_descriptors: str = typer.Option(..., help="JSON string of Can-Do descriptors"),
    strengths: str = typer.Option(..., help="Comma-separated strengths"),
    areas_for_growth: str = typer.Option(..., help="Comma-separated areas for growth"),
    recommendations: str = typer.Option(..., help="Comma-separated recommendations"),
    assessed_by: str = typer.Option(..., help="Assessor identifier"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Conduct ELD progress assessment."""
    try:
        manager = ELDManager(data_dir)

        # Parse enums and JSON
        level = EnglishProficiencyLevel(proficiency_level)

        try:
            scores_dict = json.loads(domain_scores)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for domain scores")
            raise typer.Exit(1)

        try:
            can_do_dict = json.loads(can_do_descriptors)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for Can-Do descriptors")
            raise typer.Exit(1)

        # Parse lists
        strengths_list = [s.strip() for s in strengths.split(",")]
        growth_list = [g.strip() for g in areas_for_growth.split(",")]
        recommendations_list = [r.strip() for r in recommendations.split(",")]

        record = manager.assess_eld_progress(
            student_id=student_id,
            assessment_type=assessment_type,
            proficiency_level=level,
            overall_score=overall_score,
            domain_scores=scores_dict,
            can_do_descriptors=can_do_dict,
            strengths=strengths_list,
            areas_for_growth=growth_list,
            recommendations=recommendations_list,
            assessed_by=assessed_by
        )

        print(f"✅ ELD progress assessment completed!")
        print(f"   Assessment ID: {record.id}")
        print(f"   Student: {record.student_id}")
        print(f"   Type: {record.assessment_type}")
        print(f"   Level: {record.proficiency_level.value}")
        print(f"   Overall Score: {record.overall_score}")
        print(f"   Next Steps: {len(record.next_steps)}")

    except Exception as e:
        print(f"❌ Error conducting assessment: {e}")
        raise typer.Exit(1)


@app.command()
def collaborate(
    teacher_id: str = typer.Option(..., help="Teacher identifier"),
    eld_specialist_id: str = typer.Option(..., help="ELD specialist identifier"),
    student_ids: str = typer.Option(..., help="Comma-separated student IDs"),
    focus_area: str = typer.Option("lesson_planning", help="Focus area"),
    discussion_topics: str = typer.Option(..., help="Comma-separated discussion topics"),
    agreed_actions: str = typer.Option(..., help="Comma-separated agreed actions"),
    resources_shared: str = typer.Option("", help="Comma-separated resources shared"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Record teacher-ELD specialist collaboration."""
    try:
        manager = ELDManager(data_dir)

        # Parse lists
        student_list = [s.strip() for s in student_ids.split(",")]
        topics_list = [t.strip() for t in discussion_topics.split(",")]
        actions_list = [a.strip() for a in agreed_actions.split(",")]
        resources_list = [r.strip() for r in resources_shared.split(",") if r.strip()]

        record = manager.collaborate_with_teacher(
            teacher_id=teacher_id,
            eld_specialist_id=eld_specialist_id,
            student_ids=student_list,
            focus_area=focus_area,
            discussion_topics=topics_list,
            agreed_actions=actions_list,
            resources_shared=resources_list
        )

        print(f"✅ Teacher collaboration recorded successfully!")
        print(f"   Collaboration ID: {record.id}")
        print(f"   Teacher: {record.teacher_id}")
        print(f"   ELD Specialist: {record.eld_specialist_id}")
        print(f"   Students: {len(record.student_ids)}")
        print(f"   Focus Area: {record.focus_area}")
        print(f"   Discussion Topics: {len(record.discussion_topics)}")
        print(f"   Agreed Actions: {len(record.agreed_actions)}")
        print(f"   Follow-up Date: {record.follow_up_date}")

    except Exception as e:
        print(f"❌ Error recording collaboration: {e}")
        raise typer.Exit(1)


@app.command()
def generate_report(
    student_id: str = typer.Option(..., help="Student identifier"),
    report_period: str = typer.Option("annual", help="Report period (annual, quarterly, monthly)"),
    output_file: Optional[str] = typer.Option(None, help="Output file path"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Generate comprehensive ELD progress report."""
    try:
        manager = ELDManager(data_dir)

        report = manager.generate_eld_report(
            student_id=student_id,
            report_period=report_period
        )

        if "error" in report:
            print(f"❌ {report['error']}")
            raise typer.Exit(1)

        # Determine output file
        if output_file is None:
            output_file = f"eld_report_{student_id}_{report_period}.json"

        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        profile = report["profile"]
        progress = report["progress_summary"]

        print(f"✅ ELD progress report generated successfully!")
        print(f"   Student: {student_id}")
        print(f"   Report Period: {report_period}")
        print(f"   Current Level: {profile['current_level']}")
        print(f"   Overall Score: {profile['overall_score']}")
        print(f"   Total Assessments: {progress['total_assessments']}")
        print(f"   Score Change: {progress['score_change']}")
        print(f"   Growth Indicators: {len(progress['growth_indicators'])}")
        print(f"   Report saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        raise typer.Exit(1)


@app.command()
def get_content_strategies(
    proficiency_level: str = typer.Option(..., help="Proficiency level"),
    content_area: str = typer.Option("general", help="Content area (mathematics, science, etc.)"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Get strategies for providing meaningful access to grade-level content."""
    try:
        manager = ELDManager(data_dir)

        level = EnglishProficiencyLevel(proficiency_level)

        strategies = manager.get_content_access_strategies(level, content_area)

        print(f"📚 Content Access Strategies for {proficiency_level} ELs")
        if content_area != "general":
            print(f"   Content Area: {content_area.title()}")
        print("=" * 60)

        for i, strategy in enumerate(strategies, 1):
            print(f"   {i}. {strategy}")

        print(f"\n💡 Total Strategies: {len(strategies)}")

    except Exception as e:
        print(f"❌ Error getting content strategies: {e}")
        raise typer.Exit(1)


@app.command()
def show_can_do_descriptors(
    proficiency_level: Optional[str] = typer.Option(None, help="Specific proficiency level"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """Show WIDA Can-Do descriptors for different proficiency levels."""
    try:
        manager = ELDManager(data_dir)

        descriptors = manager.can_do_descriptors

        if proficiency_level:
            level = proficiency_level
            if level in descriptors:
                print(f"🎯 WIDA Can-Do Descriptors - {level}")
                print("=" * 50)

                level_data = descriptors[level]
                for domain, can_dos in level_data.items():
                    print(f"\n📂 {domain.replace('_', ' ')}")
                    print("-" * 30)
                    for can_do in can_dos:
                        print(f"   • {can_do}")
            else:
                print(f"❌ Proficiency level '{proficiency_level}' not found")
                print("Available levels: Entering, Emerging, Developing, Expanding")
        else:
            print("🎯 WIDA Can-Do Descriptors Overview")
            print("=" * 50)
            print("Available proficiency levels:")
            for level in descriptors.keys():
                print(f"   • {level}")

            print("\n💡 Use --proficiency-level to see specific descriptors")
            print("   Example: --proficiency-level Emerging")

    except Exception as e:
        print(f"❌ Error showing Can-Do descriptors: {e}")
        raise typer.Exit(1)


@app.command()
def list_strategies(
    proficiency_level: Optional[str] = typer.Option(None, help="Filter by proficiency level"),
    domain: Optional[str] = typer.Option(None, help="Filter by ELD domain"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """List available ELD instructional strategies."""
    try:
        manager = ELDManager(data_dir)

        strategies = manager.instructional_strategies

        print("🎓 Research-Based ELD Instructional Strategies")
        print("=" * 60)

        filtered_count = 0
        for strategy_id, strategy in strategies.items():
            # Apply filters
            if proficiency_level:
                level = EnglishProficiencyLevel(proficiency_level)
                if level not in strategy.proficiency_levels:
                    continue

            if domain:
                domain_enum = ELDDomain(domain.replace("_", " & "))
                if domain_enum not in strategy.domains:
                    continue

            print(f"\n🔸 {strategy.name}")
            print(f"   ID: {strategy_id}")
            print(f"   Description: {strategy.description}")
            print(f"   Proficiency Levels: {[l.value for l in strategy.proficiency_levels]}")
            print(f"   Domains: {[d.value for d in strategy.domains]}")
            print(f"   Evidence Base: {strategy.evidence_base}")
            print(f"   Implementation Steps: {len(strategy.implementation_steps)}")
            print(f"   Materials Required: {len(strategy.materials_required)}")

            filtered_count += 1

        print(f"\n💡 Total Strategies: {filtered_count}")

        if proficiency_level or domain:
            print("\n🔍 Filters Applied:")
            if proficiency_level:
                print(f"   Proficiency Level: {proficiency_level}")
            if domain:
                print(f"   Domain: {domain}")

    except Exception as e:
        print(f"❌ Error listing strategies: {e}")
        raise typer.Exit(1)


@app.command()
def list_profiles(
    proficiency_level: Optional[str] = typer.Option(None, help="Filter by proficiency level"),
    primary_language: Optional[str] = typer.Option(None, help="Filter by primary language"),
    data_dir: str = typer.Option("data/eld", help="Data directory")
) -> None:
    """List ELD student profiles with optional filtering."""
    try:
        manager = ELDManager(data_dir)

        # Get all profile files
        profile_files = list(Path(data_dir).glob("eld_profile_*.json"))

        if not profile_files:
            print("👶 No ELD profiles found")
            return

        profiles = []
        for profile_file in profile_files:
            try:
                profile_data = json.loads(profile_file.read_text())
                # Convert string level back to enum for filtering
                profile_data["current_level"] = EnglishProficiencyLevel(profile_data["current_level"])
                profile = manager._load_eld_profile_by_student(profile_data["student_id"])

                if profile:
                    # Apply filters
                    if proficiency_level:
                        target_level = EnglishProficiencyLevel(proficiency_level)
                        if profile.current_level != target_level:
                            continue

                    if primary_language and profile.primary_language != primary_language:
                        if primary_language.lower() not in profile.primary_language.lower():
                            continue

                    profiles.append(profile)
            except Exception:
                continue

        if not profiles:
            print("👶 No ELD profiles match the specified filters")
            return

        print(f"👶 ELD Student Profiles ({len(profiles)} total)")
        print("=" * 80)

        for profile in sorted(profiles, key=lambda x: x.program_entry_date, reverse=True):
            print(f"🧒 Profile ID: {profile.id}")
            print(f"   Student: {profile.student_id}")
            print(f"   Current Level: {profile.current_level.value}")
            print(f"   Overall Score: {profile.overall_score}")
            print(f"   Primary Language: {profile.primary_language}")
            print(f"   Program Entry: {profile.program_entry_date}")

            if profile.domain_scores:
                print(f"   Domain Scores: {len(profile.domain_scores)} domains")

            if profile.individualized_learning_goals:
                print(f"   Learning Goals: {len(profile.individualized_learning_goals)}")

            print()

    except Exception as e:
        print(f"❌ Error listing profiles: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
