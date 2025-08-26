from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from ..utils.io import write_json, read_json


class EnglishProficiencyLevel(Enum):
    """WIDA English proficiency levels."""
    ENTERING = "Entering"
    EMERGING = "Emerging"
    DEVELOPING = "Developing"
    EXPANDING = "Expanding"
    BRIDGING = "Bridging"
    REACHING = "Reaching"


class ELDDomain(Enum):
    """WIDA ELD domains."""
    SOCIAL_INTERPERSONAL = "Social & Interpersonal"
    INSTRUCTIONAL = "Instructional"
    ACADEMIC_LANGUAGE = "Academic Language"


@dataclass
class ELDStudentProfile:
    """ELD student profile with proficiency tracking."""
    id: str
    student_id: str  # Reference to main student profile
    current_level: EnglishProficiencyLevel
    overall_score: float  # 1.0-6.0 scale
    domain_scores: Dict[str, float] = field(default_factory=dict)
    primary_language: str = ""
    years_in_us_schools: Optional[int] = None
    program_entry_date: str = ""
    program_exit_date: Optional[str] = None
    language_assessment_date: str = ""
    next_assessment_date: str = ""
    individualized_learning_goals: List[str] = field(default_factory=list)
    accommodations: List[str] = field(default_factory=list)
    status: str = "active"  # active, exited, monitored


@dataclass
class ELDLessonPlan:
    """ELD lesson plan with content and strategies."""
    id: str
    title: str
    proficiency_level: EnglishProficiencyLevel
    domain: ELDDomain
    grade_level: str
    duration_minutes: int
    objective: str
    language_objectives: List[str] = field(default_factory=list)  # WIDA Can-Do descriptors
    content_objectives: List[str] = field(default_factory=list)
    key_vocabulary: List[str] = field(default_factory=list)
    materials_needed: List[str] = field(default_factory=list)
    instructional_strategies: List[str] = field(default_factory=list)
    differentiation_strategies: List[str] = field(default_factory=list)
    assessment_methods: List[str] = field(default_factory=list)
    created_by: str = ""
    created_date: str = ""
    last_modified: str = ""
    alignment_standards: List[str] = field(default_factory=list)


@dataclass
class ELDInstructionalStrategy:
    """Research-based ELD instructional strategy."""
    id: str
    name: str
    description: str
    proficiency_levels: List[EnglishProficiencyLevel] = field(default_factory=list)
    domains: List[ELDDomain] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    materials_required: List[str] = field(default_factory=list)
    evidence_base: str = ""
    differentiation_options: List[str] = field(default_factory=list)


@dataclass
class ELDProgressRecord:
    """ELD progress and assessment record."""
    id: str
    student_id: str
    assessment_date: str
    assessment_type: str  # initial, progress, annual, exit
    proficiency_level: EnglishProficiencyLevel
    overall_score: float
    domain_scores: Dict[str, float] = field(default_factory=dict)
    can_do_descriptors: Dict[str, str] = field(default_factory=dict)  # WIDA Can-Do performance
    strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    assessed_by: str = ""
    notes: str = ""


@dataclass
class ELDCollaborationRecord:
    """Teacher collaboration record for ELD planning."""
    id: str
    teacher_id: str
    eld_specialist_id: str
    collaboration_date: str
    focus_area: str  # lesson planning, strategy development, progress monitoring
    student_ids: List[str] = field(default_factory=list)
    discussion_topics: List[str] = field(default_factory=list)
    agreed_actions: List[str] = field(default_factory=list)
    resources_shared: List[str] = field(default_factory=list)
    follow_up_date: Optional[str] = None
    outcomes: List[str] = field(default_factory=list)
    notes: str = ""


class ELDManager:
    """Comprehensive ELD instruction and support manager."""

    def __init__(self, data_dir: str = "data/eld"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.instructional_strategies = self._load_standard_strategies()
        self.can_do_descriptors = self._load_can_do_descriptors()

    def _load_standard_strategies(self) -> Dict[str, ELDInstructionalStrategy]:
        """Load research-based ELD instructional strategies."""
        return {
            "scaffolded_reading": ELDInstructionalStrategy(
                id="scaffold_read",
                name="Scaffolded Reading",
                description="Structured support to access grade-level text",
                proficiency_levels=[EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING,
                                  EnglishProficiencyLevel.DEVELOPING],
                domains=[ELDDomain.INSTRUCTIONAL, ELDDomain.ACADEMIC_LANGUAGE],
                implementation_steps=[
                    "Pre-teach key vocabulary using visual supports",
                    "Provide sentence starters and stems",
                    "Use graphic organizers for comprehension",
                    "Offer bilingual glossaries and dictionaries",
                    "Implement think-pair-share for comprehension checks"
                ],
                materials_required=["Visual aids", "Graphic organizers", "Bilingual dictionaries"],
                evidence_base="Research shows scaffolding increases comprehension by 35-40%",
                differentiation_options=[
                    "Adjust vocabulary load based on proficiency",
                    "Provide different levels of text complexity",
                    "Use native language support as needed"
                ]
            ),
            "language_experience_approach": ELDInstructionalStrategy(
                id="lea",
                name="Language Experience Approach",
                description="Student-led content creation and language development",
                proficiency_levels=[EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING],
                domains=[ELDDomain.SOCIAL_INTERPERSONAL, ELDDomain.INSTRUCTIONAL],
                implementation_steps=[
                    "Engage students in shared experience or activity",
                    "Have students dictate what happened in experience",
                    "Write down student language as accurately as possible",
                    "Read the text together and discuss",
                    "Use the text for reading and writing activities"
                ],
                materials_required=["Chart paper", "Markers", "Experience materials"],
                evidence_base="LEA develops authentic language use and builds confidence",
                differentiation_options=[
                    "Use pictures and gestures for non-verbal support",
                    "Allow native language contributions initially",
                    "Focus on key vocabulary and phrases"
                ]
            ),
            "academic_conversation_stems": ELDInstructionalStrategy(
                id="conv_stems",
                name="Academic Conversation Stems",
                description="Structured sentence frames for academic discussions",
                proficiency_levels=[EnglishProficiencyLevel.EMERGING, EnglishProficiencyLevel.DEVELOPING,
                                  EnglishProficiencyLevel.EXPANDING],
                domains=[ELDDomain.ACADEMIC_LANGUAGE, ELDDomain.SOCIAL_INTERPERSONAL],
                implementation_steps=[
                    "Introduce conversation stems related to content",
                    "Model use of stems in whole group discussions",
                    "Practice stems in small groups with visuals",
                    "Provide written stems as reference during activities",
                    "Gradually remove supports as proficiency increases"
                ],
                materials_required=["Conversation stem charts", "Visual supports", "Reference cards"],
                evidence_base="Stems increase participation by 50-60% for ELs",
                differentiation_options=[
                    "Start with simple stems and increase complexity",
                    "Use picture supports with stems",
                    "Allow native language translation initially"
                ]
            ),
            "vocabulary_development": ELDInstructionalStrategy(
                id="vocab_dev",
                name="Systematic Vocabulary Development",
                description="Structured approach to academic vocabulary acquisition",
                proficiency_levels=[EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING,
                                  EnglishProficiencyLevel.DEVELOPING, EnglishProficiencyLevel.EXPANDING],
                domains=[ELDDomain.ACADEMIC_LANGUAGE, ELDDomain.INSTRUCTIONAL],
                implementation_steps=[
                    "Identify key academic vocabulary for the unit",
                    "Create word walls with visual representations",
                    "Use vocabulary in context throughout the unit",
                    "Provide multiple exposures and practice opportunities",
                    "Assess vocabulary knowledge regularly"
                ],
                materials_required=["Word walls", "Vocabulary journals", "Visual dictionaries"],
                evidence_base="Systematic vocabulary instruction increases word knowledge by 25-30%",
                differentiation_options=[
                    "Focus on high-frequency words first",
                    "Provide native language translations",
                    "Use technology tools for vocabulary practice"
                ]
            ),
            "content_based_eld": ELDInstructionalStrategy(
                id="content_eld",
                name="Content-Based ELD",
                description="Integrate ELD instruction with academic content",
                proficiency_levels=[EnglishProficiencyLevel.DEVELOPING, EnglishProficiencyLevel.EXPANDING,
                                  EnglishProficiencyLevel.BRIDGING],
                domains=[ELDDomain.INSTRUCTIONAL, ELDDomain.ACADEMIC_LANGUAGE],
                implementation_steps=[
                    "Identify language demands of academic content",
                    "Design language objectives alongside content objectives",
                    "Use SDAIE (Specially Designed Academic Instruction in English)",
                    "Provide graphic organizers for complex content",
                    "Offer multiple means of representation and expression"
                ],
                materials_required=["Graphic organizers", "Visual aids", "Technology tools"],
                evidence_base="Content-based ELD improves both language and content learning",
                differentiation_options=[
                    "Adjust content complexity while maintaining language focus",
                    "Provide multiple text representations",
                    "Use flexible grouping based on needs"
                ]
            )
        }

    def _load_can_do_descriptors(self) -> Dict[str, Dict[str, List[str]]]:
        """Load WIDA Can-Do descriptors for different proficiency levels."""
        return {
            "Entering": {
                "Social_Interpersonal": [
                    "I can greet people and introduce myself",
                    "I can respond to simple questions about myself",
                    "I can follow simple classroom routines"
                ],
                "Instructional": [
                    "I can identify familiar words and phrases in texts",
                    "I can follow simple written instructions",
                    "I can participate in shared reading activities"
                ],
                "Academic_Language": [
                    "I can use basic vocabulary in content areas",
                    "I can respond to simple questions about content",
                    "I can use simple sentences to express ideas"
                ]
            },
            "Emerging": {
                "Social_Interpersonal": [
                    "I can participate in simple conversations",
                    "I can ask for clarification when needed",
                    "I can work with partners on simple tasks"
                ],
                "Instructional": [
                    "I can understand main ideas in simple texts",
                    "I can complete simple graphic organizers",
                    "I can follow multi-step directions"
                ],
                "Academic_Language": [
                    "I can use content-specific vocabulary",
                    "I can explain concepts in simple terms",
                    "I can write simple paragraphs about content"
                ]
            },
            "Developing": {
                "Social_Interpersonal": [
                    "I can participate in group discussions",
                    "I can explain my thinking to others",
                    "I can collaborate on complex tasks"
                ],
                "Instructional": [
                    "I can understand grade-level texts with support",
                    "I can create detailed graphic organizers",
                    "I can synthesize information from multiple sources"
                ],
                "Academic_Language": [
                    "I can use academic language in discussions",
                    "I can write detailed responses to questions",
                    "I can present information to others"
                ]
            },
            "Expanding": {
                "Social_Interpersonal": [
                    "I can lead group discussions",
                    "I can facilitate peer learning",
                    "I can debate topics using evidence"
                ],
                "Instructional": [
                    "I can analyze complex texts independently",
                    "I can create and present projects",
                    "I can evaluate sources for reliability"
                ],
                "Academic_Language": [
                    "I can use advanced academic vocabulary",
                    "I can write analytical essays",
                    "I can present complex ideas clearly"
                ]
            }
        }

    def create_eld_profile(self, student_id: str, current_level: EnglishProficiencyLevel,
                          primary_language: str, overall_score: float,
                          domain_scores: Dict[str, float], program_entry_date: str) -> ELDStudentProfile:
        """Create a new ELD student profile."""
        profile_id = f"eld_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        profile = ELDStudentProfile(
            id=profile_id,
            student_id=student_id,
            current_level=current_level,
            overall_score=overall_score,
            domain_scores=domain_scores,
            primary_language=primary_language,
            program_entry_date=program_entry_date,
            language_assessment_date=datetime.now().strftime('%Y-%m-%d')
        )

        # Set next assessment date (typically annually for WIDA)
        profile.next_assessment_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        self._save_eld_profile(profile)
        return profile

    def create_lesson_plan(self, title: str, proficiency_level: EnglishProficiencyLevel,
                          domain: ELDDomain, grade_level: str, duration_minutes: int,
                          objective: str, language_objectives: List[str],
                          content_objectives: List[str], created_by: str) -> ELDLessonPlan:
        """Create a comprehensive ELD lesson plan."""
        plan_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        lesson_plan = ELDLessonPlan(
            id=plan_id,
            title=title,
            proficiency_level=proficiency_level,
            domain=domain,
            grade_level=grade_level,
            duration_minutes=duration_minutes,
            objective=objective,
            language_objectives=language_objectives,
            content_objectives=content_objectives,
            created_by=created_by,
            created_date=datetime.now().strftime('%Y-%m-%d'),
            last_modified=datetime.now().strftime('%Y-%m-%d')
        )

        # Generate key vocabulary from objectives
        lesson_plan.key_vocabulary = self._extract_key_vocabulary(language_objectives + content_objectives)

        # Generate instructional strategies based on level and domain
        lesson_plan.instructional_strategies = self._generate_strategies_for_plan(proficiency_level, domain)

        # Generate differentiation strategies
        lesson_plan.differentiation_strategies = self._generate_differentiation_strategies(proficiency_level)

        # Generate assessment methods
        lesson_plan.assessment_methods = self._generate_assessment_methods(proficiency_level, domain)

        self._save_lesson_plan(lesson_plan)
        return lesson_plan

    def assess_eld_progress(self, student_id: str, assessment_type: str,
                           proficiency_level: EnglishProficiencyLevel, overall_score: float,
                           domain_scores: Dict[str, float], can_do_descriptors: Dict[str, str],
                           strengths: List[str], areas_for_growth: List[str],
                           recommendations: List[str], assessed_by: str) -> ELDProgressRecord:
        """Conduct ELD progress assessment."""
        record_id = f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        record = ELDProgressRecord(
            id=record_id,
            student_id=student_id,
            assessment_date=datetime.now().strftime('%Y-%m-%d'),
            assessment_type=assessment_type,
            proficiency_level=proficiency_level,
            overall_score=overall_score,
            domain_scores=domain_scores,
            can_do_descriptors=can_do_descriptors,
            strengths=strengths,
            areas_for_growth=areas_for_growth,
            recommendations=recommendations,
            assessed_by=assessed_by
        )

        # Generate next steps based on assessment
        record.next_steps = self._generate_next_steps(record)

        self._save_progress_record(record)

        # Update student profile
        self._update_student_profile_from_assessment(student_id, record)

        return record

    def collaborate_with_teacher(self, teacher_id: str, eld_specialist_id: str,
                               student_ids: List[str], focus_area: str,
                               discussion_topics: List[str], agreed_actions: List[str],
                               resources_shared: List[str]) -> ELDCollaborationRecord:
        """Record teacher-ELD specialist collaboration."""
        collab_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        record = ELDCollaborationRecord(
            id=collab_id,
            teacher_id=teacher_id,
            eld_specialist_id=eld_specialist_id,
            student_ids=student_ids,
            collaboration_date=datetime.now().strftime('%Y-%m-%d'),
            focus_area=focus_area,
            discussion_topics=discussion_topics,
            agreed_actions=agreed_actions,
            resources_shared=resources_shared
        )

        # Set follow-up date (typically 2-4 weeks after collaboration)
        record.follow_up_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

        self._save_collaboration_record(record)
        return record

    def generate_eld_report(self, student_id: str, report_period: str = "annual") -> Dict[str, Any]:
        """Generate comprehensive ELD progress report."""
        profile = self._load_eld_profile_by_student(student_id)
        if not profile:
            return {"error": "ELD profile not found"}

        # Get progress records for the period
        progress_records = self._get_progress_records_for_period(student_id, report_period)

        # Get collaboration records
        collaboration_records = self._get_collaboration_records_for_student(student_id)

        # Calculate growth and progress
        progress_summary = self._calculate_progress_summary(progress_records, profile)

        report = {
            "student_id": student_id,
            "profile": {
                "current_level": profile.current_level.value,
                "overall_score": profile.overall_score,
                "primary_language": profile.primary_language,
                "program_entry_date": profile.program_entry_date
            },
            "progress_summary": progress_summary,
            "assessment_history": [
                {
                    "date": record.assessment_date,
                    "type": record.assessment_type,
                    "level": record.proficiency_level.value,
                    "score": record.overall_score,
                    "domains": record.domain_scores
                } for record in progress_records
            ],
            "can_do_performance": profile.individualized_learning_goals,
            "strengths": list(set([strength for record in progress_records for strength in record.strengths])),
            "areas_for_growth": list(set([area for record in progress_records for area in record.areas_for_growth])),
            "recommendations": list(set([rec for record in progress_records for rec in record.recommendations])),
            "collaboration_summary": {
                "total_sessions": len(collaboration_records),
                "focus_areas": list(set([rec.focus_area for rec in collaboration_records]))
            },
            "generated_at": datetime.now().isoformat(),
            "report_period": report_period
        }

        return report

    def get_content_access_strategies(self, proficiency_level: EnglishProficiencyLevel,
                                    content_area: str) -> List[str]:
        """Get strategies for providing meaningful access to grade-level content."""
        strategies = []

        base_strategies = [
            "Use visual supports and graphic organizers",
            "Provide bilingual glossaries and dictionaries",
            "Pre-teach key academic vocabulary",
            "Use realia and hands-on materials",
            "Implement cooperative learning structures"
        ]

        if proficiency_level in [EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING]:
            strategies.extend([
                "Simplify language while maintaining content complexity",
                "Use picture dictionaries and visual vocabulary supports",
                "Provide sentence starters and stems for responses",
                "Use native language support as a bridge",
                "Focus on key concepts with repeated exposure"
            ])
        elif proficiency_level == EnglishProficiencyLevel.DEVELOPING:
            strategies.extend([
                "Use SDAIE (Specially Designed Academic Instruction in English)",
                "Provide academic language stems and frames",
                "Offer multiple means of representation",
                "Use technology tools for vocabulary building",
                "Implement gradual release of responsibility"
            ])
        elif proficiency_level in [EnglishProficiencyLevel.EXPANDING, EnglishProficiencyLevel.BRIDGING]:
            strategies.extend([
                "Focus on advanced academic language structures",
                "Promote higher-order thinking in English",
                "Encourage academic discussions and debates",
                "Support complex text analysis",
                "Facilitate peer teaching opportunities"
            ])

        # Content-specific strategies
        if content_area.lower() == "mathematics":
            strategies.extend([
                "Use manipulatives and visual representations",
                "Teach math vocabulary explicitly",
                "Provide word problems in simplified English",
                "Use number lines and graphic organizers for problem-solving"
            ])
        elif content_area.lower() == "science":
            strategies.extend([
                "Use hands-on experiments and demonstrations",
                "Create science vocabulary word walls",
                "Provide lab instructions in simplified language",
                "Use visual aids for scientific concepts"
            ])

        return list(set(strategies))  # Remove duplicates

    def _extract_key_vocabulary(self, objectives: List[str]) -> List[str]:
        """Extract key academic vocabulary from objectives."""
        # This is a simplified implementation
        # In a real system, this would use NLP to extract academic vocabulary
        academic_vocab = []

        # Common academic vocabulary patterns
        academic_words = [
            "analyze", "compare", "contrast", "describe", "explain", "identify",
            "predict", "summarize", "evaluate", "create", "design", "investigate",
            "hypothesis", "evidence", "conclusion", "procedure", "variable",
            "function", "structure", "process", "system", "relationship"
        ]

        for objective in objectives:
            for word in academic_words:
                if word in objective.lower():
                    academic_vocab.append(word)

        return list(set(academic_vocab))

    def _generate_strategies_for_plan(self, level: EnglishProficiencyLevel, domain: ELDDomain) -> List[str]:
        """Generate appropriate instructional strategies for the lesson plan."""
        strategies = []

        for strategy in self.instructional_strategies.values():
            if level in strategy.proficiency_levels and domain in strategy.domains:
                strategies.extend(strategy.implementation_steps[:3])  # Take first 3 steps

        return list(set(strategies))[:6]  # Limit to 6 strategies

    def _generate_differentiation_strategies(self, level: EnglishProficiencyLevel) -> List[str]:
        """Generate differentiation strategies based on proficiency level."""
        if level in [EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING]:
            return [
                "Provide visual and hands-on supports",
                "Use simplified English with key vocabulary",
                "Offer native language support",
                "Extend wait time for responses",
                "Use picture dictionaries and visual aids"
            ]
        elif level == EnglishProficiencyLevel.DEVELOPING:
            return [
                "Provide academic language stems",
                "Use graphic organizers for complex content",
                "Offer technology tools for support",
                "Provide peer buddies for language support",
                "Use SDAIE strategies"
            ]
        else:
            return [
                "Focus on advanced academic language",
                "Promote higher-order thinking tasks",
                "Encourage academic discussions",
                "Support complex text analysis",
                "Provide opportunities for leadership"
            ]

    def _generate_assessment_methods(self, level: EnglishProficiencyLevel, domain: ELDDomain) -> List[str]:
        """Generate assessment methods appropriate for level and domain."""
        methods = []

        base_methods = [
            "Observation of participation",
            "Language proficiency checklist",
            "Portfolio of student work"
        ]

        if level in [EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING]:
            methods.extend([
                "Picture-based assessments",
                "Performance assessments",
                "Checklist of key vocabulary use",
                "Oral language samples"
            ])
        else:
            methods.extend([
                "Written responses to prompts",
                "Academic language use in discussions",
                "Content-area assessments with language supports",
                "Self-assessment using Can-Do descriptors"
            ])

        if domain == ELDDomain.ACADEMIC_LANGUAGE:
            methods.extend([
                "Vocabulary assessments",
                "Writing samples with language analysis",
                "Oral presentation rubrics"
            ])
        elif domain == ELDDomain.SOCIAL_INTERPERSONAL:
            methods.extend([
                "Group participation observations",
                "Peer interaction checklists",
                "Communication strategy use"
            ])

        return list(set(methods))[:5]

    def _generate_next_steps(self, record: ELDProgressRecord) -> List[str]:
        """Generate next steps based on progress assessment."""
        next_steps = []

        if record.proficiency_level in [EnglishProficiencyLevel.ENTERING, EnglishProficiencyLevel.EMERGING]:
            next_steps.extend([
                "Continue building basic interpersonal communication skills",
                "Focus on high-frequency academic vocabulary development",
                "Increase opportunities for oral language practice",
                "Provide more visual supports for content access"
            ])
        elif record.proficiency_level == EnglishProficiencyLevel.DEVELOPING:
            next_steps.extend([
                "Develop academic language structures",
                "Increase reading comprehension supports",
                "Focus on written language development",
                "Promote participation in academic discussions"
            ])
        else:
            next_steps.extend([
                "Support advanced academic language use",
                "Encourage leadership in group discussions",
                "Focus on complex text analysis skills",
                "Prepare for grade-level content without supports"
            ])

        # Add recommendations from the record
        next_steps.extend(record.recommendations[:3])

        return list(set(next_steps))[:6]

    def _calculate_progress_summary(self, progress_records: List[ELDProgressRecord],
                                  profile: ELDStudentProfile) -> Dict[str, Any]:
        """Calculate progress summary from assessment records."""
        if not progress_records:
            return {
                "total_assessments": 0,
                "current_level": profile.current_level.value,
                "score_change": 0,
                "growth_indicators": []
            }

        # Sort by date
        sorted_records = sorted(progress_records, key=lambda x: x.assessment_date)

        # Calculate score change
        first_score = sorted_records[0].overall_score
        last_score = sorted_records[-1].overall_score
        score_change = last_score - first_score

        # Determine growth indicators
        growth_indicators = []
        if score_change > 0.5:
            growth_indicators.append("Significant growth in overall proficiency")
        elif score_change > 0:
            growth_indicators.append("Steady progress in language development")

        # Check domain improvements
        if len(sorted_records) >= 2:
            first_domains = sorted_records[0].domain_scores
            last_domains = sorted_records[-1].domain_scores

            for domain in ['Social_Interpersonal', 'Instructional', 'Academic_Language']:
                if domain in first_domains and domain in last_domains:
                    domain_change = last_domains[domain] - first_domains[domain]
                    if domain_change > 0.3:
                        growth_indicators.append(f"Strong growth in {domain}")

        return {
            "total_assessments": len(progress_records),
            "current_level": profile.current_level.value,
            "score_change": round(score_change, 2),
            "growth_indicators": growth_indicators,
            "assessment_period": f"{sorted_records[0].assessment_date} to {sorted_records[-1].assessment_date}"
        }

    def _update_student_profile_from_assessment(self, student_id: str, record: ELDProgressRecord) -> None:
        """Update student profile based on assessment results."""
        profile = self._load_eld_profile_by_student(student_id)
        if profile:
            profile.current_level = record.proficiency_level
            profile.overall_score = record.overall_score
            profile.domain_scores = record.domain_scores
            profile.language_assessment_date = record.assessment_date

            # Update individualized goals based on areas for growth
            profile.individualized_learning_goals.extend(record.areas_for_growth)

            self._save_eld_profile(profile)

    def _get_progress_records_for_period(self, student_id: str, period: str) -> List[ELDProgressRecord]:
        """Get progress records for a specific period."""
        all_records = self._get_all_progress_records_for_student(student_id)

        if period == "annual":
            cutoff_date = datetime.now() - timedelta(days=365)
        elif period == "quarterly":
            cutoff_date = datetime.now() - timedelta(days=90)
        else:  # monthly
            cutoff_date = datetime.now() - timedelta(days=30)

        return [record for record in all_records
                if datetime.fromisoformat(record.assessment_date) >= cutoff_date]

    def _get_all_progress_records_for_student(self, student_id: str) -> List[ELDProgressRecord]:
        """Get all progress records for a student."""
        records = []
        for record_file in self.data_dir.glob("progress_*.json"):
            try:
                record_data = read_json(str(record_file))
                if record_data.get("student_id") == student_id:
                    records.append(ELDProgressRecord(**record_data))
            except Exception:
                continue

        return sorted(records, key=lambda x: x.assessment_date, reverse=True)

    def _get_collaboration_records_for_student(self, student_id: str) -> List[ELDCollaborationRecord]:
        """Get collaboration records for a student."""
        records = []
        for record_file in self.data_dir.glob("collab_*.json"):
            try:
                record_data = read_json(str(record_file))
                if student_id in record_data.get("student_ids", []):
                    records.append(ELDCollaborationRecord(**record_data))
            except Exception:
                continue

        return sorted(records, key=lambda x: x.collaboration_date, reverse=True)

    def _save_eld_profile(self, profile: ELDStudentProfile) -> None:
        """Save ELD profile."""
        filename = f"eld_profile_{profile.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": profile.id,
            "student_id": profile.student_id,
            "current_level": profile.current_level.value,
            "overall_score": profile.overall_score,
            "domain_scores": profile.domain_scores,
            "primary_language": profile.primary_language,
            "years_in_us_schools": profile.years_in_us_schools,
            "program_entry_date": profile.program_entry_date,
            "program_exit_date": profile.program_exit_date,
            "language_assessment_date": profile.language_assessment_date,
            "next_assessment_date": profile.next_assessment_date,
            "individualized_learning_goals": profile.individualized_learning_goals,
            "accommodations": profile.accommodations,
            "status": profile.status
        }

        write_json(str(filepath), data)

    def _load_eld_profile_by_student(self, student_id: str) -> Optional[ELDStudentProfile]:
        """Load ELD profile by student ID."""
        for profile_file in self.data_dir.glob("eld_profile_*.json"):
            try:
                profile_data = read_json(str(profile_file))
                if profile_data.get("student_id") == student_id:
                    # Convert string level back to enum
                    profile_data["current_level"] = EnglishProficiencyLevel(profile_data["current_level"])
                    return ELDStudentProfile(**profile_data)
            except Exception:
                continue

        return None

    def _save_lesson_plan(self, plan: ELDLessonPlan) -> None:
        """Save ELD lesson plan."""
        filename = f"lesson_plan_{plan.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": plan.id,
            "title": plan.title,
            "proficiency_level": plan.proficiency_level.value,
            "domain": plan.domain.value,
            "grade_level": plan.grade_level,
            "duration_minutes": plan.duration_minutes,
            "objective": plan.objective,
            "language_objectives": plan.language_objectives,
            "content_objectives": plan.content_objectives,
            "key_vocabulary": plan.key_vocabulary,
            "materials_needed": plan.materials_needed,
            "instructional_strategies": plan.instructional_strategies,
            "differentiation_strategies": plan.differentiation_strategies,
            "assessment_methods": plan.assessment_methods,
            "created_by": plan.created_by,
            "created_date": plan.created_date,
            "last_modified": plan.last_modified,
            "alignment_standards": plan.alignment_standards
        }

        write_json(str(filepath), data)

    def _save_progress_record(self, record: ELDProgressRecord) -> None:
        """Save progress record."""
        filename = f"progress_{record.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": record.id,
            "student_id": record.student_id,
            "assessment_date": record.assessment_date,
            "assessment_type": record.assessment_type,
            "proficiency_level": record.proficiency_level.value,
            "overall_score": record.overall_score,
            "domain_scores": record.domain_scores,
            "can_do_descriptors": record.can_do_descriptors,
            "strengths": record.strengths,
            "areas_for_growth": record.areas_for_growth,
            "recommendations": record.recommendations,
            "next_steps": record.next_steps,
            "assessed_by": record.assessed_by,
            "notes": record.notes
        }

        write_json(str(filepath), data)

    def _save_collaboration_record(self, record: ELDCollaborationRecord) -> None:
        """Save collaboration record."""
        filename = f"collab_{record.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": record.id,
            "teacher_id": record.teacher_id,
            "eld_specialist_id": record.eld_specialist_id,
            "student_ids": record.student_ids,
            "collaboration_date": record.collaboration_date,
            "focus_area": record.focus_area,
            "discussion_topics": record.discussion_topics,
            "agreed_actions": record.agreed_actions,
            "resources_shared": record.resources_shared,
            "follow_up_date": record.follow_up_date,
            "outcomes": record.outcomes,
            "notes": record.notes
        }

        write_json(str(filepath), data)
