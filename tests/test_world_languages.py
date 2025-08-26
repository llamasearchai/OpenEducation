"""
Tests for World Languages instruction module.
"""


import pytest

from openeducation.world_languages.language_core import (
    ACTFLMode,
    CulturalActivity,
    Language,
    LanguageAssessment,
    LanguageCurriculum,
    LessonPlan,
    ProficiencyLevel,
    StudentProgress,
    WorldLanguagesManager,
)


class TestWorldLanguagesManager:
    """Test World Languages Manager functionality."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create world languages manager with temporary directory."""
        return WorldLanguagesManager(str(tmp_path / "world_languages_data"))

    def test_get_curriculum(self, manager):
        """Test getting curriculum for specific language and level."""
        curriculum = manager.get_curriculum("Japanese", "middle_school")

        assert isinstance(curriculum, LanguageCurriculum)
        assert curriculum.language == Language.JAPANESE
        assert curriculum.level == "Middle School"
        assert curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(curriculum.units) > 0

    def test_get_all_curricula(self, manager):
        """Test getting all curricula."""
        curricula = manager.get_all_curricula()

        assert "Japanese" in curricula
        assert "Mandarin" in curricula
        assert "Korean" in curricula
        assert "French" in curricula
        assert "Spanish" in curricula

        assert "middle_school" in curricula["Japanese"]
        assert "high_school" in curricula["Japanese"]

    def test_create_lesson_plan(self, manager):
        """Test creating lesson plan."""
        goals = {
            "Interpersonal": ["Practice greetings"],
            "Presentational": ["Create cultural presentation"]
        }

        lesson_plan = manager.create_lesson_plan(
            curriculum_id="jp_ms_curriculum",
            title="Japanese Greetings",
            grade_level="Middle School",
            duration_minutes=45,
            objective="Students will learn Japanese greetings",
            communicative_goals=goals,
            language_functions=["Greet others", "Introduce oneself"],
            vocabulary_focus=["konnichiwa", "hajimemashite"],
            cultural_elements=["Bowing etiquette", "Social hierarchy"],
            technology_tools=["Video conferencing"]
        )

        assert lesson_plan.id.startswith("lesson_")
        assert lesson_plan.title == "Japanese Greetings"
        assert lesson_plan.duration_minutes == 45
        assert len(lesson_plan.communicative_goals) == 2
        assert len(lesson_plan.procedures) > 0
        assert len(lesson_plan.assessment) > 0

    def test_create_cultural_activity(self, manager):
        """Test creating cultural activity."""
        activity = manager.create_cultural_activity(
            language=Language.JAPANESE,
            title="Tea Ceremony Experience",
            description="Traditional Japanese tea ceremony workshop",
            activity_type="cultural_event",
            grade_levels=["Middle School", "High School"],
            objectives=[
                "Experience Japanese cultural traditions",
                "Practice respectful behavior",
                "Understand tea ceremony significance"
            ],
            duration_hours=2
        )

        assert activity.id.startswith("activity_")
        assert activity.language == Language.JAPANESE
        assert activity.title == "Tea Ceremony Experience"
        assert len(activity.objectives) == 3
        assert activity.duration_hours == 2
        assert len(activity.preparation_needed) > 0
        assert len(activity.materials_required) > 0

    def test_assess_student_progress(self, manager):
        """Test student progress assessment."""
        assessment = manager.assess_student_progress(
            student_id="student_001",
            language=Language.JAPANESE,
            proficiency_level=ProficiencyLevel.INTERMEDIATE_LOW,
            assessment_type="progress",
            scores={"vocabulary": 3.5, "grammar": 2.8, "culture": 4.0},
            strengths=["Cultural understanding", "Motivation"],
            areas_for_growth=["Grammar accuracy", "Speaking fluency"],
            recommendations=["Grammar practice", "Speaking opportunities"]
        )

        assert assessment.id.startswith("assess_")
        assert assessment.student_id == "student_001"
        assert assessment.language == Language.JAPANESE
        assert assessment.proficiency_level == ProficiencyLevel.INTERMEDIATE_LOW
        assert len(assessment.strengths) == 2
        assert len(assessment.areas_for_growth) == 2

    def test_load_lesson_plan_from_data(self, manager):
        """Test loading lesson plan from data."""
        data = {
            "id": "test_plan",
            "curriculum_id": "jp_ms_curriculum",
            "title": "Test Plan",
            "grade_level": "Middle School",
            "duration_minutes": 45,
            "objective": "Test objective",
            "communicative_goals": {"Interpersonal": ["Test goal"]},
            "language_functions": ["Test function"],
            "vocabulary_focus": ["test"],
            "cultural_elements": ["test culture"],
            "materials": ["test material"],
            "technology_tools": ["test tool"],
            "procedures": ["Test procedure"],
            "differentiation": ["Test differentiation"],
            "assessment": {"formative": [], "summative": [], "self_assessment": []},
            "homework": "Test homework",
            "extensions": ["Test extension"],
            "created_by": "test_teacher",
            "created_date": "2024-01-15"
        }

        lesson_plan = manager._load_lesson_plan_from_data(data)

        assert lesson_plan.id == "test_plan"
        assert lesson_plan.title == "Test Plan"
        assert lesson_plan.duration_minutes == 45

    def test_load_cultural_activity_from_data(self, manager):
        """Test loading cultural activity from data."""
        data = {
            "id": "test_activity",
            "language": "Japanese",
            "title": "Test Activity",
            "description": "Test description",
            "type": "cultural_event",
            "grade_levels": ["Middle School"],
            "objectives": ["Test objective"],
            "duration_hours": 2,
            "preparation_needed": ["Test prep"],
            "materials_required": ["Test material"],
            "assessment_methods": ["Test assessment"],
            "collaboration_partners": ["Test partner"],
            "scheduled_date": None,
            "status": "planned"
        }

        activity = manager._load_cultural_activity_from_data(data)

        assert activity.id == "test_activity"
        assert activity.language == Language.JAPANESE
        assert activity.title == "Test Activity"


class TestLanguageDataModels:
    """Test language data model functionality."""

    def test_language_enum(self):
        """Test language enum."""
        assert Language.JAPANESE.value == "Japanese"
        assert Language.MANDARIN.value == "Mandarin"
        assert Language.KOREAN.value == "Korean"
        assert Language.FRENCH.value == "French"
        assert Language.SPANISH.value == "Spanish"

    def test_proficiency_level_enum(self):
        """Test proficiency level enum."""
        assert ProficiencyLevel.NOVICE_LOW.value == "Novice Low"
        assert ProficiencyLevel.INTERMEDIATE_HIGH.value == "Intermediate High"
        assert ProficiencyLevel.ADVANCED_LOW.value == "Advanced Low"

    def test_actfl_mode_enum(self):
        """Test ACTFL mode enum."""
        assert ACTFLMode.INTERPERSONAL.value == "Interpersonal"
        assert ACTFLMode.INTERPRETIVE.value == "Interpretive"
        assert ACTFLMode.PRESENTATIONAL.value == "Presentational"

    def test_language_curriculum_creation(self):
        """Test language curriculum creation."""
        curriculum = LanguageCurriculum(
            id="test_curriculum",
            language=Language.JAPANESE,
            level="Middle School",
            proficiency_target=ProficiencyLevel.NOVICE_HIGH,
            title="Test Japanese Curriculum",
            description="Test description",
            units=[],
            essential_questions=["Test question"],
            enduring_understandings=["Test understanding"],
            cultural_competencies=["Test competency"],
            technology_integration=["Test tech"],
            assessment_methods=["Test assessment"],
            differentiation_strategies=["Test strategy"],
            created_by="test_author",
            created_date="2024-01-15",
            alignment_standards=["ACTFL", "CCSS"]
        )

        assert curriculum.id == "test_curriculum"
        assert curriculum.language == Language.JAPANESE
        assert curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(curriculum.essential_questions) == 1

    def test_lesson_plan_creation(self):
        """Test lesson plan creation."""
        lesson_plan = LessonPlan(
            id="test_plan",
            curriculum_id="test_curriculum",
            title="Test Lesson",
            grade_level="Middle School",
            duration_minutes=45,
            objective="Test objective",
            communicative_goals={"Interpersonal": ["Test goal"]},
            language_functions=["Test function"],
            vocabulary_focus=["test"],
            cultural_elements=["test culture"],
            technology_tools=["test tool"],
            procedures=["Test procedure"],
            differentiation=["Test differentiation"],
            assessment={"formative": [], "summative": [], "self_assessment": []},
            created_by="test_teacher",
            created_date="2024-01-15"
        )

        assert lesson_plan.id == "test_plan"
        assert lesson_plan.duration_minutes == 45
        assert len(lesson_plan.communicative_goals) == 1

    def test_cultural_activity_creation(self):
        """Test cultural activity creation."""
        activity = CulturalActivity(
            id="test_activity",
            language=Language.JAPANESE,
            title="Test Activity",
            description="Test description",
            type="cultural_event",
            grade_levels=["Middle School"],
            objectives=["Test objective"],
            duration_hours=2,
            preparation_needed=["Test prep"],
            materials_required=["Test material"],
            assessment_methods=["Test assessment"],
            collaboration_partners=["Test partner"]
        )

        assert activity.id == "test_activity"
        assert activity.language == Language.JAPANESE
        assert activity.type == "cultural_event"
        assert len(activity.objectives) == 1

    def test_language_assessment_creation(self):
        """Test language assessment creation."""
        assessment = LanguageAssessment(
            id="test_assessment",
            student_id="student_001",
            language=Language.JAPANESE,
            assessment_type="progress",
            proficiency_level=ProficiencyLevel.INTERMEDIATE_LOW,
            mode=ACTFLMode.INTERPERSONAL,
            assessment_date="2024-01-15",
            scores={"vocabulary": 3.5},
            strengths=["Good participation"],
            areas_for_growth=["Grammar"],
            recommendations=["More practice"],
            administered_by="test_assessor"
        )

        assert assessment.id == "test_assessment"
        assert assessment.student_id == "student_001"
        assert assessment.proficiency_level == ProficiencyLevel.INTERMEDIATE_LOW
        assert len(assessment.strengths) == 1

    def test_student_progress_creation(self):
        """Test student progress creation."""
        progress = StudentProgress(
            id="test_progress",
            student_id="student_001",
            language=Language.JAPANESE,
            start_date="2024-01-15",
            current_level=ProficiencyLevel.NOVICE_HIGH,
            target_level=ProficiencyLevel.INTERMEDIATE_LOW,
            courses_completed=["Japanese 1"],
            assessments=["assessment_001"],
            cultural_activities=["activity_001"],
            achievements=["Completed first unit"],
            challenges=["Grammar"],
            interests=["Anime", "Culture"],
            learning_goals=["Improve speaking"],
            mentor_notes=["Shows great interest"],
            last_updated="2024-01-15"
        )

        assert progress.id == "test_progress"
        assert progress.student_id == "student_001"
        assert progress.current_level == ProficiencyLevel.NOVICE_HIGH
        assert len(progress.courses_completed) == 1


class TestWorldLanguagesIntegration:
    """Test world languages module integration."""

    def test_cli_import(self):
        """Test world languages CLI can be imported."""
        from openeducation.world_languages import cli_integration
        assert cli_integration.app is not None

    def test_core_import(self):
        """Test world languages core can be imported."""
        from openeducation.world_languages import language_core
        assert language_core.WorldLanguagesManager is not None

    def test_main_cli_integration(self):
        """Test world languages integration with main CLI."""
        from openeducation.cli import app
        assert app is not None

        # Check if world languages commands are registered
        command_names = [cmd.name for cmd in app.commands.values()]
        assert "languages" in command_names


class TestCurriculumContent:
    """Test curriculum content and structure."""

    @pytest.fixture
    def manager(self):
        """Create world languages manager."""
        return WorldLanguagesManager()

    def test_japanese_curricula_structure(self, manager):
        """Test Japanese curricula structure."""
        ms_curriculum = manager.get_curriculum("Japanese", "middle_school")
        hs_curriculum = manager.get_curriculum("Japanese", "high_school")

        # Middle school
        assert ms_curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(ms_curriculum.units) == 3
        assert "Greetings" in ms_curriculum.units[0]["title"]
        assert "Family" in ms_curriculum.units[1]["title"]
        assert "School" in ms_curriculum.units[2]["title"]

        # High school
        assert hs_curriculum.proficiency_target == ProficiencyLevel.INTERMEDIATE_HIGH
        assert len(hs_curriculum.units) == 3
        assert "Society" in hs_curriculum.units[0]["title"]
        assert "Literature" in hs_curriculum.units[1]["title"]
        assert "Professions" in hs_curriculum.units[2]["title"]

    def test_mandarin_curricula_structure(self, manager):
        """Test Mandarin curricula structure."""
        ms_curriculum = manager.get_curriculum("Mandarin", "middle_school")
        hs_curriculum = manager.get_curriculum("Mandarin", "high_school")

        # Middle school
        assert ms_curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(ms_curriculum.units) == 2
        assert "Characters" in ms_curriculum.units[0]["title"]
        assert "Family" in ms_curriculum.units[1]["title"]

        # High school
        assert hs_curriculum.proficiency_target == ProficiencyLevel.INTERMEDIATE_HIGH
        assert len(hs_curriculum.units) == 1
        assert "Media" in hs_curriculum.units[0]["title"]

    def test_french_curricula_structure(self, manager):
        """Test French curricula structure."""
        ms_curriculum = manager.get_curriculum("French", "middle_school")
        hs_curriculum = manager.get_curriculum("French", "high_school")

        # Middle school
        assert ms_curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(ms_curriculum.units) == 2
        assert "Bonjour" in ms_curriculum.units[0]["title"]
        assert "Famille" in ms_curriculum.units[1]["title"]

        # High school
        assert hs_curriculum.proficiency_target == ProficiencyLevel.INTERMEDIATE_HIGH
        assert len(hs_curriculum.units) == 1
        assert "Literature" in hs_curriculum.units[0]["title"]

    def test_spanish_curricula_structure(self, manager):
        """Test Spanish curricula structure."""
        ms_curriculum = manager.get_curriculum("Spanish", "middle_school")
        hs_curriculum = manager.get_curriculum("Spanish", "high_school")

        # Middle school
        assert ms_curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(ms_curriculum.units) == 2
        assert "Hola" in ms_curriculum.units[0]["title"]
        assert "Familia" in ms_curriculum.units[1]["title"]

        # High school
        assert hs_curriculum.proficiency_target == ProficiencyLevel.INTERMEDIATE_HIGH
        assert len(hs_curriculum.units) == 1
        assert "Literature" in hs_curriculum.units[0]["title"]

    def test_korean_curricula_structure(self, manager):
        """Test Korean curricula structure."""
        ms_curriculum = manager.get_curriculum("Korean", "middle_school")
        hs_curriculum = manager.get_curriculum("Korean", "high_school")

        # Middle school
        assert ms_curriculum.proficiency_target == ProficiencyLevel.NOVICE_HIGH
        assert len(ms_curriculum.units) == 1
        assert "Hangul" in ms_curriculum.units[0]["title"]

        # High school
        assert hs_curriculum.proficiency_target == ProficiencyLevel.INTERMEDIATE_HIGH
        assert len(hs_curriculum.units) == 1
        assert "Society" in hs_curriculum.units[0]["title"]

    def test_curriculum_metadata(self, manager):
        """Test curriculum metadata and standards."""
        curriculum = manager.get_curriculum("Japanese", "middle_school")

        assert curriculum.created_by == "curriculum_system"
        assert "ACTFL" in curriculum.alignment_standards
        assert "CCSS" in curriculum.alignment_standards
        assert len(curriculum.essential_questions) > 0
        assert len(curriculum.enduring_understandings) > 0
        assert len(curriculum.cultural_competencies) > 0
        assert len(curriculum.technology_integration) > 0
