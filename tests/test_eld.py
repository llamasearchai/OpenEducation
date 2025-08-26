"""
Tests for English Language Development (ELD) module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from openeducation.eld.eld_core import (
    ELDManager, EnglishProficiencyLevel, ELDDomain,
    ELDStudentProfile, ELDLessonPlan, ELDProgressRecord,
    ELDCollaborationRecord, ELDInstructionalStrategy
)


class TestELDManager:
    """Test ELD Manager functionality."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create ELD manager with temporary directory."""
        return ELDManager(str(tmp_path / "eld_data"))

    def test_create_eld_profile(self, manager):
        """Test creating ELD student profile."""
        profile = manager.create_eld_profile(
            student_id="student_001",
            current_level=EnglishProficiencyLevel.DEVELOPING,
            primary_language="Spanish",
            overall_score=2.8,
            domain_scores={"Social_Interpersonal": 3.2},
            program_entry_date="2024-01-15"
        )

        assert profile.id.startswith("eld_")
        assert profile.student_id == "student_001"
        assert profile.current_level == EnglishProficiencyLevel.DEVELOPING
        assert profile.overall_score == 2.8
        assert profile.primary_language == "Spanish"

    def test_create_lesson_plan(self, manager):
        """Test creating ELD lesson plan."""
        plan = manager.create_lesson_plan(
            title="Spanish Greetings",
            proficiency_level=EnglishProficiencyLevel.DEVELOPING,
            domain=ELDDomain.SOCIAL_INTERPERSONAL,
            grade_level="3rd Grade",
            duration_minutes=45,
            objective="Students will practice Spanish greetings",
            language_objectives=["I can greet others in Spanish"],
            content_objectives=["I can understand Spanish greetings"],
            created_by="teacher_smith"
        )

        assert plan.id.startswith("lesson_")
        assert plan.title == "Spanish Greetings"
        assert plan.proficiency_level == EnglishProficiencyLevel.DEVELOPING
        assert plan.duration_minutes == 45
        assert len(plan.key_vocabulary) > 0
        assert len(plan.instructional_strategies) > 0

    def test_assess_eld_progress(self, manager):
        """Test ELD progress assessment."""
        record = manager.assess_eld_progress(
            student_id="student_001",
            assessment_type="progress",
            proficiency_level=EnglishProficiencyLevel.DEVELOPING,
            overall_score=3.2,
            domain_scores={"Social_Interpersonal": 3.5},
            can_do_descriptors={"Social_Interpersonal": "I can participate in discussions"},
            strengths=["Good participation"],
            areas_for_growth=["Vocabulary"],
            recommendations=["More vocabulary practice"],
            assessed_by="eld_specialist"
        )

        assert record.id.startswith("progress_")
        assert record.student_id == "student_001"
        assert record.proficiency_level == EnglishProficiencyLevel.DEVELOPING
        assert len(record.next_steps) > 0

    def test_collaborate_with_teacher(self, manager):
        """Test teacher-ELD specialist collaboration."""
        record = manager.collaborate_with_teacher(
            teacher_id="teacher_smith",
            eld_specialist_id="eld_specialist_001",
            student_ids=["student_001", "student_002"],
            focus_area="vocabulary_development",
            discussion_topics=["Spanish vocabulary strategies"],
            agreed_actions=["Implement word walls"],
            resources_shared=["Vocabulary lists"]
        )

        assert record.id.startswith("collab_")
        assert record.teacher_id == "teacher_smith"
        assert record.eld_specialist_id == "eld_specialist_001"
        assert len(record.student_ids) == 2
        assert record.follow_up_date is not None

    def test_generate_eld_report(self, manager):
        """Test ELD report generation."""
        # First create a profile
        manager.create_eld_profile(
            student_id="student_001",
            current_level=EnglishProficiencyLevel.DEVELOPING,
            primary_language="Spanish",
            overall_score=2.8,
            domain_scores={"Social_Interpersonal": 3.2},
            program_entry_date="2024-01-15"
        )

        report = manager.generate_eld_report("student_001", "annual")

        assert "student_id" in report
        assert "profile" in report
        assert "progress_summary" in report
        assert report["profile"]["current_level"] == "Developing"

    def test_get_content_access_strategies(self, manager):
        """Test content access strategies generation."""
        strategies = manager.get_content_access_strategies(
            EnglishProficiencyLevel.DEVELOPING,
            "mathematics"
        )

        assert len(strategies) > 0
        assert any("manipulative" in strategy.lower() for strategy in strategies)

    def test_can_do_descriptors(self, manager):
        """Test WIDA Can-Do descriptors."""
        descriptors = manager.can_do_descriptors

        assert "Developing" in descriptors
        assert "Social_Interpersonal" in descriptors["Developing"]
        assert len(descriptors["Developing"]["Social_Interpersonal"]) > 0

    def test_instructional_strategies(self, manager):
        """Test research-based instructional strategies."""
        strategies = manager.instructional_strategies

        assert "scaffolded_reading" in strategies
        strategy = strategies["scaffolded_reading"]
        assert isinstance(strategy, ELDInstructionalStrategy)
        assert len(strategy.implementation_steps) > 0
        assert len(strategy.materials_required) > 0


class TestELDDataModels:
    """Test ELD data model functionality."""

    def test_english_proficiency_level_enum(self):
        """Test proficiency level enum."""
        level = EnglishProficiencyLevel.DEVELOPING
        assert level.value == "Developing"
        assert str(level) == "EnglishProficiencyLevel.DEVELOPING"

    def test_eld_domain_enum(self):
        """Test ELD domain enum."""
        domain = ELDDomain.ACADEMIC_LANGUAGE
        assert domain.value == "Academic Language"

    def test_eld_student_profile_creation(self):
        """Test ELD student profile creation."""
        profile = ELDStudentProfile(
            id="test_profile",
            student_id="student_001",
            current_level=EnglishProficiencyLevel.EMERGING,
            overall_score=2.5,
            primary_language="Spanish",
            program_entry_date="2024-01-15"
        )

        assert profile.id == "test_profile"
        assert profile.status == "active"  # Default value
        assert profile.individualized_learning_goals == []  # Default empty list

    def test_eld_lesson_plan_creation(self):
        """Test ELD lesson plan creation."""
        plan = ELDLessonPlan(
            id="test_plan",
            title="Test Lesson",
            proficiency_level=EnglishProficiencyLevel.DEVELOPING,
            domain=ELDDomain.INSTRUCTIONAL,
            grade_level="5th Grade",
            duration_minutes=45,
            objective="Test objective",
            created_by="test_teacher",
            created_date="2024-01-15",
            last_modified="2024-01-15"
        )

        assert plan.id == "test_plan"
        assert plan.duration_minutes == 45
        assert plan.alignment_standards == []  # Default empty list

    def test_eld_progress_record_creation(self):
        """Test ELD progress record creation."""
        record = ELDProgressRecord(
            id="test_record",
            student_id="student_001",
            assessment_date="2024-01-15",
            assessment_type="progress",
            proficiency_level=EnglishProficiencyLevel.DEVELOPING,
            overall_score=3.2,
            assessed_by="test_assessor"
        )

        assert record.id == "test_record"
        assert record.assessment_type == "progress"
        assert record.notes == ""  # Default empty string

    def test_eld_collaboration_record_creation(self):
        """Test ELD collaboration record creation."""
        record = ELDCollaborationRecord(
            id="test_collab",
            teacher_id="teacher_001",
            eld_specialist_id="eld_001",
            collaboration_date="2024-01-15",
            focus_area="lesson_planning",
            discussion_topics=["Vocabulary development"],
            agreed_actions=["Create word wall"],
            resources_shared=["Vocabulary lists"]
        )

        assert record.id == "test_collab"
        assert len(record.discussion_topics) == 1
        assert record.follow_up_date is None  # Default None


class TestELDIntegration:
    """Test ELD module integration."""

    def test_eld_cli_import(self):
        """Test ELD CLI can be imported."""
        from openeducation.eld import cli_integration
        assert cli_integration.app is not None

    def test_eld_core_import(self):
        """Test ELD core can be imported."""
        from openeducation.eld import eld_core
        assert eld_core.ELDManager is not None

    def test_main_cli_integration(self):
        """Test ELD integration with main CLI."""
        from openeducation.cli import app
        assert app is not None

        # Check if ELD commands are registered
        command_names = [cmd.name for cmd in app.commands.values()]
        assert "eld" in command_names
