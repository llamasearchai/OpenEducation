from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from ..utils.io import write_json, read_json


@dataclass
class ChildProfile:
    """Child profile with demographic and developmental information."""
    id: str
    first_name: str
    last_name: str
    date_of_birth: str
    classroom_id: str
    enrollment_date: str
    primary_language: str = "English"
    special_needs: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    medical_notes: str = ""
    developmental_milestones: Dict[str, str] = field(default_factory=dict)
    ifsp_iep: bool = False  # Individualized Family Service Plan / Individualized Education Program


@dataclass
class AssessmentTool:
    """Research-based assessment tool definition."""
    id: str
    name: str
    description: str
    age_range: str  # e.g., "3-5 years"
    domains: List[str] = field(default_factory=list)  # cognitive, language, social-emotional, etc.
    administration_time: int = 30  # minutes
    frequency: str = "quarterly"  # weekly, monthly, quarterly, annually
    scoring_method: str = "scale_1_5"  # scale_1_5, percentage, checklist, narrative
    standards_alignment: List[str] = field(default_factory=list)  # Head Start, NAEYC, etc.


@dataclass
class AssessmentRecord:
    """Individual assessment record for a child."""
    id: str
    child_id: str
    assessor_id: str
    tool_id: str
    assessment_date: str
    age_at_assessment: float  # age in years
    setting: str = "classroom"  # classroom, home, clinical
    scores: Dict[str, Any] = field(default_factory=dict)  # domain scores
    observations: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    areas_for_concern: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_assessment_date: Optional[str] = None
    parent_input: str = ""
    additional_notes: str = ""
    status: str = "completed"  # draft, completed, reviewed, shared_with_family


@dataclass
class LearningObjective:
    """Individual learning objective with progress tracking."""
    id: str
    child_id: str
    objective: str
    domain: str  # cognitive, language, social-emotional, physical, approaches_to_learning
    current_level: str = "emerging"  # emerging, developing, proficient, advanced
    target_level: str = "proficient"
    strategies: List[str] = field(default_factory=list)
    progress_notes: List[str] = field(default_factory=list)
    target_date: Optional[str] = None
    achieved_date: Optional[str] = None
    status: str = "active"  # active, achieved, discontinued


@dataclass
class ProgressReport:
    """Comprehensive progress report for a child."""
    id: str
    child_id: str
    report_period: str  # quarterly, annual, etc.
    start_date: str
    end_date: str
    overall_summary: str
    domain_summaries: Dict[str, str] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    parent_signature_date: Optional[str] = None
    teacher_signature_date: str = ""


class ChildAssessmentManager:
    """Manage child assessment and progress tracking."""

    def __init__(self, data_dir: str = "data/assessments"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.assessment_tools = self._load_standard_tools()

    def _load_standard_tools(self) -> Dict[str, AssessmentTool]:
        """Load standard assessment tools."""
        return {
            "asq": AssessmentTool(
                id="asq",
                name="Ages & Stages Questionnaire",
                description="Parent-completed developmental screener",
                age_range="1 month - 5.5 years",
                domains=["communication", "gross_motor", "fine_motor", "problem_solving", "personal_social"],
                administration_time=15,
                frequency="quarterly",
                scoring_method="pass_fail",
                standards_alignment=["CDC", "AAP"]
            ),
            "asq_se": AssessmentTool(
                id="asq_se",
                name="ASQ:SE-2",
                description="Social-Emotional screening tool",
                age_range="1 month - 6 years",
                domains=["social_emotional"],
                administration_time=10,
                frequency="quarterly",
                scoring_method="scale_0_3",
                standards_alignment=["CDC", "Zero to Three"]
            ),
            "ts_gold": AssessmentTool(
                id="ts_gold",
                name="Teaching Strategies GOLD",
                description="Comprehensive assessment system",
                age_range="Birth - 8 years",
                domains=["social_emotional", "physical", "language", "cognitive", "literacy", "mathematics", "science", "social_studies", "arts", "english_language_acquisition"],
                administration_time=45,
                frequency="monthly",
                scoring_method="scale_1_9",
                standards_alignment=["NAEYC", "Head Start", "State Standards"]
            ),
            "ecers": AssessmentTool(
                id="ecers",
                name="Early Childhood Environment Rating Scale",
                description="Environment quality assessment",
                age_range="0-5 years",
                domains=["space_and_furnishings", "personal_care_routines", "language_and_reasoning", "activities", "interaction", "program_structure", "parents_and_staff"],
                administration_time=60,
                frequency="annually",
                scoring_method="scale_1_7",
                standards_alignment=["NAEYC"]
            ),
            "class": AssessmentTool(
                id="class",
                name="CLASS - Classroom Assessment Scoring System",
                description="Teacher-child interaction quality",
                age_range="3-5 years",
                domains=["emotional_support", "classroom_organization", "instructional_support"],
                administration_time=120,
                frequency="annually",
                scoring_method="scale_1_7",
                standards_alignment=["NAEYC", "Head Start"]
            )
        }

    def create_child_profile(self, first_name: str, last_name: str, date_of_birth: str,
                           classroom_id: str, **kwargs) -> ChildProfile:
        """Create a new child profile."""
        child_id = f"child_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        profile = ChildProfile(
            id=child_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            classroom_id=classroom_id,
            enrollment_date=datetime.now().strftime('%Y-%m-%d')
        )

        # Apply additional kwargs
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        self._save_child_profile(profile)
        return profile

    def conduct_assessment(self, child_id: str, assessor_id: str, tool_id: str,
                         scores: Dict[str, Any], observations: List[str],
                         strengths: List[str], areas_for_concern: List[str],
                         recommendations: List[str]) -> AssessmentRecord:
        """Conduct an assessment for a child."""
        child = self._load_child_profile(child_id)
        if not child:
            raise ValueError(f"Child {child_id} not found")

        # Calculate age at assessment
        birth_date = datetime.fromisoformat(child.date_of_birth)
        assessment_date = datetime.now()
        age_years = (assessment_date - birth_date).days / 365.25

        assessment_id = f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        assessment = AssessmentRecord(
            id=assessment_id,
            child_id=child_id,
            assessor_id=assessor_id,
            tool_id=tool_id,
            assessment_date=datetime.now().strftime('%Y-%m-%d'),
            age_at_assessment=round(age_years, 2),
            scores=scores,
            observations=observations,
            strengths=strengths,
            areas_for_concern=areas_for_concern,
            recommendations=recommendations
        )

        # Set next assessment date based on tool frequency
        if tool_id in self.assessment_tools:
            tool = self.assessment_tools[tool_id]
            if tool.frequency == "weekly":
                next_date = assessment_date + timedelta(weeks=1)
            elif tool.frequency == "monthly":
                next_date = assessment_date + timedelta(days=30)
            elif tool.frequency == "quarterly":
                next_date = assessment_date + timedelta(days=90)
            else:  # annually
                next_date = assessment_date + timedelta(days=365)

            assessment.next_assessment_date = next_date.strftime('%Y-%m-%d')

        self._save_assessment(assessment)
        return assessment

    def create_learning_objective(self, child_id: str, objective: str, domain: str,
                                target_level: str = "proficient", strategies: List[str] = None) -> LearningObjective:
        """Create a learning objective for a child."""
        obj_id = f"obj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        learning_obj = LearningObjective(
            id=obj_id,
            child_id=child_id,
            objective=objective,
            domain=domain,
            target_level=target_level,
            strategies=strategies or []
        )

        self._save_learning_objective(learning_obj)
        return learning_obj

    def update_learning_progress(self, objective_id: str, progress_note: str,
                               new_level: str = None) -> None:
        """Update progress on a learning objective."""
        objective = self._load_learning_objective(objective_id)
        if objective:
            objective.progress_notes.append(f"{datetime.now().isoformat()}: {progress_note}")

            if new_level:
                objective.current_level = new_level
                if new_level == objective.target_level:
                    objective.achieved_date = datetime.now().strftime('%Y-%m-%d')
                    objective.status = "achieved"

            self._save_learning_objective(objective)

    def generate_progress_report(self, child_id: str, report_period: str = "quarterly") -> ProgressReport:
        """Generate a comprehensive progress report for a child."""
        child = self._load_child_profile(child_id)
        if not child:
            raise ValueError(f"Child {child_id} not found")

        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate report period
        if report_period == "quarterly":
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        elif report_period == "annual":
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        else:  # monthly
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        end_date = datetime.now().strftime('%Y-%m-%d')

        # Get assessments in period
        assessments = self._get_assessments_in_period(child_id, start_date, end_date)

        # Get learning objectives
        objectives = self._get_child_learning_objectives(child_id)

        # Generate summaries
        domain_summaries = self._generate_domain_summaries(assessments, objectives)
        achievements = self._extract_achievements(assessments, objectives)
        goals = self._extract_goals(objectives)
        recommendations = self._generate_recommendations(assessments, objectives)

        # Create overall summary
        overall_summary = self._generate_overall_summary(child, assessments, objectives)

        report = ProgressReport(
            id=report_id,
            child_id=child_id,
            report_period=report_period,
            start_date=start_date,
            end_date=end_date,
            overall_summary=overall_summary,
            domain_summaries=domain_summaries,
            achievements=achievements,
            goals=goals,
            recommendations=recommendations,
            teacher_signature_date=datetime.now().strftime('%Y-%m-%d')
        )

        self._save_progress_report(report)
        return report

    def _generate_domain_summaries(self, assessments: List[AssessmentRecord],
                                 objectives: List[LearningObjective]) -> Dict[str, str]:
        """Generate summaries for each developmental domain."""
        domains = {}
        all_domains = ["cognitive", "language", "social_emotional", "physical", "approaches_to_learning"]

        for domain in all_domains:
            # Get assessments for this domain
            domain_assessments = [a for a in assessments if domain in str(a.scores.keys())]
            domain_objectives = [o for o in objectives if o.domain == domain]

            if domain_assessments or domain_objectives:
                summary = f"{domain.replace('_', ' ').title()}: "

                if domain_assessments:
                    avg_score = sum([sum(a.scores.values()) / len(a.scores) for a in domain_assessments]) / len(domain_assessments)
                    summary += ".1f"

                if domain_objectives:
                    achieved = len([o for o in domain_objectives if o.status == "achieved"])
                    total = len(domain_objectives)
                    summary += f" | {achieved}/{total} objectives achieved"

                domains[domain] = summary

        return domains

    def _extract_achievements(self, assessments: List[AssessmentRecord],
                            objectives: List[LearningObjective]) -> List[str]:
        """Extract achievements from assessments and objectives."""
        achievements = []

        # Check achieved objectives
        for objective in objectives:
            if objective.status == "achieved" and objective.achieved_date:
                achievements.append(f"Achieved: {objective.objective}")

        # Check assessment strengths
        for assessment in assessments:
            achievements.extend(assessment.strengths[:2])  # Limit to 2 per assessment

        return list(set(achievements))  # Remove duplicates

    def _extract_goals(self, objectives: List[LearningObjective]) -> List[str]:
        """Extract current goals from learning objectives."""
        return [obj.objective for obj in objectives if obj.status == "active"]

    def _generate_recommendations(self, assessments: List[AssessmentRecord],
                                objectives: List[LearningObjective]) -> List[str]:
        """Generate recommendations based on assessments and objectives."""
        recommendations = []

        # Collect recommendations from assessments
        for assessment in assessments:
            recommendations.extend(assessment.recommendations)

        # Add recommendations for unachieved objectives
        for objective in objectives:
            if objective.status == "active":
                recommendations.append(f"Continue working on: {objective.objective}")

        return list(set(recommendations))[:5]  # Limit to 5 recommendations

    def _generate_overall_summary(self, child: ChildProfile, assessments: List[AssessmentRecord],
                                objectives: List[LearningObjective]) -> str:
        """Generate overall summary for the progress report."""
        total_objectives = len(objectives)
        achieved_objectives = len([o for o in objectives if o.status == "achieved"])
        total_assessments = len(assessments)

        summary = f"{child.first_name} {child.last_name} has participated in {total_assessments} assessments "
        summary += f"and has {total_objectives} learning objectives. "
        summary += f"{achieved_objectives} objectives have been achieved. "

        if assessments:
            recent_assessment = max(assessments, key=lambda x: x.assessment_date)
            summary += f"Most recent assessment shows age-appropriate development in most areas."

        return summary

    def get_child_database_summary(self, child_id: str) -> Dict[str, Any]:
        """Get comprehensive database summary for a child."""
        child = self._load_child_profile(child_id)
        if not child:
            return {"error": "Child not found"}

        assessments = self._get_child_assessments(child_id)
        objectives = self._get_child_learning_objectives(child_id)
        reports = self._get_child_progress_reports(child_id)

        return {
            "child_profile": {
                "id": child.id,
                "name": f"{child.first_name} {child.last_name}",
                "age": self._calculate_age(child.date_of_birth),
                "classroom": child.classroom_id,
                "enrollment_date": child.enrollment_date
            },
            "assessment_summary": {
                "total_assessments": len(assessments),
                "latest_assessment": max([a.assessment_date for a in assessments]) if assessments else None,
                "next_assessment": min([a.next_assessment_date for a in assessments if a.next_assessment_date]) if assessments else None
            },
            "learning_objectives": {
                "total": len(objectives),
                "active": len([o for o in objectives if o.status == "active"]),
                "achieved": len([o for o in objectives if o.status == "achieved"]),
                "domains": list(set([o.domain for o in objectives]))
            },
            "progress_reports": {
                "total": len(reports),
                "latest": max([r.end_date for r in reports]) if reports else None
            },
            "data_completeness": self._calculate_data_completeness(assessments, objectives, reports)
        }

    def _calculate_data_completeness(self, assessments: List[AssessmentRecord],
                                   objectives: List[LearningObjective],
                                   reports: List[ProgressReport]) -> float:
        """Calculate data completeness percentage."""
        total_items = 3  # assessments, objectives, reports
        completed_items = 0

        if assessments:
            completed_items += 1
        if objectives:
            completed_items += 1
        if reports:
            completed_items += 1

        return (completed_items / total_items) * 100

    def _calculate_age(self, date_of_birth: str) -> float:
        """Calculate age in years."""
        birth_date = datetime.fromisoformat(date_of_birth)
        today = datetime.now()
        return round((today - birth_date).days / 365.25, 2)

    def _get_assessments_in_period(self, child_id: str, start_date: str, end_date: str) -> List[AssessmentRecord]:
        """Get assessments within a specific period."""
        assessments = self._get_child_assessments(child_id)
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        return [a for a in assessments if start <= datetime.fromisoformat(a.assessment_date) <= end]

    def _get_child_assessments(self, child_id: str) -> List[AssessmentRecord]:
        """Get all assessments for a child."""
        assessments = []
        for assess_file in self.data_dir.glob("assessment_*.json"):
            try:
                assess_data = read_json(str(assess_file))
                if assess_data.get("child_id") == child_id:
                    assessments.append(AssessmentRecord(**assess_data))
            except Exception:
                continue

        return sorted(assessments, key=lambda x: x.assessment_date, reverse=True)

    def _get_child_learning_objectives(self, child_id: str) -> List[LearningObjective]:
        """Get all learning objectives for a child."""
        objectives = []
        for obj_file in self.data_dir.glob("objective_*.json"):
            try:
                obj_data = read_json(str(obj_file))
                if obj_data.get("child_id") == child_id:
                    objectives.append(LearningObjective(**obj_data))
            except Exception:
                continue

        return sorted(objectives, key=lambda x: x.id)

    def _get_child_progress_reports(self, child_id: str) -> List[ProgressReport]:
        """Get all progress reports for a child."""
        reports = []
        for report_file in self.data_dir.glob("report_*.json"):
            try:
                report_data = read_json(str(report_file))
                if report_data.get("child_id") == child_id:
                    reports.append(ProgressReport(**report_data))
            except Exception:
                continue

        return sorted(reports, key=lambda x: x.end_date, reverse=True)

    def _save_child_profile(self, profile: ChildProfile) -> None:
        """Save child profile."""
        filename = f"profile_{profile.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": profile.id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "date_of_birth": profile.date_of_birth,
            "classroom_id": profile.classroom_id,
            "enrollment_date": profile.enrollment_date,
            "primary_language": profile.primary_language,
            "special_needs": profile.special_needs,
            "allergies": profile.allergies,
            "emergency_contacts": profile.emergency_contacts,
            "medical_notes": profile.medical_notes,
            "developmental_milestones": profile.developmental_milestones,
            "ifsp_iep": profile.ifsp_iep
        }

        write_json(str(filepath), data)

    def _load_child_profile(self, child_id: str) -> Optional[ChildProfile]:
        """Load child profile."""
        filename = f"profile_{child_id}.json"
        filepath = self.data_dir / filename

        if filepath.exists():
            try:
                data = read_json(str(filepath))
                return ChildProfile(**data)
            except Exception:
                pass

        return None

    def _save_assessment(self, assessment: AssessmentRecord) -> None:
        """Save assessment record."""
        filename = f"assessment_{assessment.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": assessment.id,
            "child_id": assessment.child_id,
            "assessor_id": assessment.assessor_id,
            "tool_id": assessment.tool_id,
            "assessment_date": assessment.assessment_date,
            "age_at_assessment": assessment.age_at_assessment,
            "setting": assessment.setting,
            "scores": assessment.scores,
            "observations": assessment.observations,
            "strengths": assessment.strengths,
            "areas_for_concern": assessment.areas_for_concern,
            "recommendations": assessment.recommendations,
            "next_assessment_date": assessment.next_assessment_date,
            "parent_input": assessment.parent_input,
            "additional_notes": assessment.additional_notes,
            "status": assessment.status
        }

        write_json(str(filepath), data)

    def _save_learning_objective(self, objective: LearningObjective) -> None:
        """Save learning objective."""
        filename = f"objective_{objective.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": objective.id,
            "child_id": objective.child_id,
            "objective": objective.objective,
            "domain": objective.domain,
            "current_level": objective.current_level,
            "target_level": objective.target_level,
            "strategies": objective.strategies,
            "progress_notes": objective.progress_notes,
            "target_date": objective.target_date,
            "achieved_date": objective.achieved_date,
            "status": objective.status
        }

        write_json(str(filepath), data)

    def _load_learning_objective(self, objective_id: str) -> Optional[LearningObjective]:
        """Load learning objective."""
        filename = f"objective_{objective_id}.json"
        filepath = self.data_dir / filename

        if filepath.exists():
            try:
                data = read_json(str(filepath))
                return LearningObjective(**data)
            except Exception:
                pass

        return None

    def _save_progress_report(self, report: ProgressReport) -> None:
        """Save progress report."""
        filename = f"report_{report.id}.json"
        filepath = self.data_dir / filename

        data = {
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
        }

        write_json(str(filepath), data)
