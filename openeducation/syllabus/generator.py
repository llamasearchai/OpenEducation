from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models.card import Card
from ..utils.io import write_json, read_json


@dataclass
class LearningObjective:
    """Individual learning objective with assessment criteria."""
    id: str
    title: str
    description: str
    standard: str
    difficulty: str = "medium"
    estimated_time: int = 30  # minutes
    prerequisites: List[str] = field(default_factory=list)
    assessment_criteria: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)


@dataclass
class SyllabusUnit:
    """A unit within a syllabus containing multiple objectives."""
    id: str
    title: str
    description: str
    duration_weeks: int
    objectives: List[LearningObjective] = field(default_factory=list)
    assessment_methods: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)


@dataclass
class Syllabus:
    """Complete syllabus for a subject."""
    id: str
    subject: str
    grade_level: str
    title: str
    description: str
    duration_weeks: int
    instructor: str
    units: List[SyllabusUnit] = field(default_factory=list)
    standards: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    grading_policy: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)


class SyllabusGenerator:
    """Generate comprehensive syllabi for various educational subjects."""

    def __init__(self):
        self.subject_templates = self._load_subject_templates()

    def _load_subject_templates(self) -> Dict[str, Dict]:
        """Load predefined templates for each subject area."""
        return {
            "science": self._get_science_template(),
            "visual_performing_arts": self._get_arts_template(),
            "social_studies": self._get_social_studies_template(),
            "service_learning": self._get_service_learning_template(),
            "mathematics": self._get_math_template(),
            "language_literacy": self._get_language_template(),
            "biliteracy_dual_language": self._get_biliteracy_template(),
            "social_justice": self._get_social_justice_template(),
            "classroom_management": self._get_classroom_management_template(),
            "health_fitness": self._get_health_template()
        }

    def generate_syllabus(self, subject: str, grade_level: str = "9-12",
                         duration_weeks: int = 36, instructor: str = "Teacher") -> Syllabus:
        """Generate a complete syllabus for the specified subject."""
        if subject not in self.subject_templates:
            raise ValueError(f"Subject '{subject}' not supported. Available: {list(self.subject_templates.keys())}")

        template = self.subject_templates[subject]

        syllabus = Syllabus(
            id=f"syllabus_{subject}_{grade_level.replace('-', '_')}",
            subject=subject,
            grade_level=grade_level,
            title=template["title"],
            description=template["description"],
            duration_weeks=duration_weeks,
            instructor=instructor,
            standards=template["standards"],
            materials=template["materials"],
            grading_policy=template["grading_policy"],
            prerequisites=template["prerequisites"],
            learning_outcomes=template["learning_outcomes"]
        )

        # Generate units based on template
        syllabus.units = self._generate_units(template, duration_weeks)

        return syllabus

    def _generate_units(self, template: Dict, total_weeks: int) -> List[SyllabusUnit]:
        """Generate syllabus units based on template and duration."""
        units = []
        unit_templates = template["units"]
        weeks_per_unit = max(1, total_weeks // len(unit_templates))

        for i, unit_template in enumerate(unit_templates):
            unit = SyllabusUnit(
                id=f"unit_{i+1}",
                title=unit_template["title"],
                description=unit_template["description"],
                duration_weeks=weeks_per_unit,
                assessment_methods=unit_template["assessment_methods"],
                resources=unit_template["resources"],
                projects=unit_template["projects"]
            )

            # Generate learning objectives for this unit
            unit.objectives = self._generate_objectives(unit_template, unit.id)

            units.append(unit)

        return units

    def _generate_objectives(self, unit_template: Dict, unit_id: str) -> List[LearningObjective]:
        """Generate learning objectives for a unit."""
        objectives = []
        obj_templates = unit_template.get("objectives", [])

        for i, obj_template in enumerate(obj_templates):
            objective = LearningObjective(
                id=f"{unit_id}_obj_{i+1}",
                title=obj_template["title"],
                description=obj_template["description"],
                standard=obj_template["standard"],
                difficulty=obj_template.get("difficulty", "medium"),
                estimated_time=obj_template.get("estimated_time", 30),
                prerequisites=obj_template.get("prerequisites", []),
                assessment_criteria=obj_template.get("assessment_criteria", []),
                resources=obj_template.get("resources", [])
            )
            objectives.append(objective)

        return objectives

    def generate_anki_deck_from_syllabus(self, syllabus: Syllabus, output_dir: str = "data/decks") -> str:
        """Generate Anki decks from syllabus content."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        all_cards = []

        for unit in syllabus.units:
            # Unit overview card
            unit_card = Card.basic(
                front=f"What are the main topics covered in {unit.title}?",
                back=f"{unit.description}\n\nAssessment methods: {', '.join(unit.assessment_methods)}",
                source_id=syllabus.id,
                deck_id=syllabus.id,
                tags=["syllabus", "unit_overview", syllabus.subject]
            )
            all_cards.append(unit_card)

            # Learning objective cards
            for objective in unit.objectives:
                obj_card = Card.basic(
                    front=f"Learning Objective: {objective.title}",
                    back=f"{objective.description}\n\nStandard: {objective.standard}\n\nAssessment: {', '.join(objective.assessment_criteria)}",
                    source_id=syllabus.id,
                    deck_id=syllabus.id,
                    tags=["syllabus", "learning_objective", syllabus.subject, unit.id]
                )
                all_cards.append(obj_card)

        # Save cards to JSON
        cards_path = Path(output_dir) / f"{syllabus.id}_cards.json"
        cards_dict = [card.to_dict() for card in all_cards]
        write_json(str(cards_path), cards_dict)

        return str(cards_path)

    def create_learning_schedule(self, syllabus: Syllabus, start_date: str = None) -> Dict[str, Any]:
        """Create a learning schedule based on syllabus."""
        if start_date is None:
            start_date = datetime.now().date()
        else:
            start_date = datetime.fromisoformat(start_date).date()

        schedule = {
            "syllabus_id": syllabus.id,
            "subject": syllabus.subject,
            "start_date": start_date.isoformat(),
            "schedule": []
        }

        current_date = start_date

        for unit in syllabus.units:
            unit_schedule = {
                "unit_id": unit.id,
                "unit_title": unit.title,
                "start_date": current_date.isoformat(),
                "objectives": []
            }

            # Schedule objectives within the unit
            obj_start = current_date
            for objective in unit.objectives:
                obj_schedule = {
                    "objective_id": objective.id,
                    "title": objective.title,
                    "start_date": obj_start.isoformat(),
                    "estimated_completion": (obj_start + timedelta(days=3)).isoformat(),
                    "estimated_time": objective.estimated_time
                }
                unit_schedule["objectives"].append(obj_schedule)
                obj_start += timedelta(days=4)  # Space objectives

            unit_schedule["end_date"] = obj_start.isoformat()
            schedule["schedule"].append(unit_schedule)
            current_date = obj_start + timedelta(days=1)  # Gap between units

        schedule["end_date"] = current_date.isoformat()
        return schedule

    # Subject-specific templates
    def _get_science_template(self) -> Dict[str, Any]:
        return {
            "title": "High School Science: Integrated Science",
            "description": "Comprehensive study of scientific principles, methods, and applications across multiple disciplines.",
            "standards": ["NGSS", "Common Core"],
            "materials": ["Textbook", "Lab equipment", "Digital microscope", "Science journal"],
            "grading_policy": {
                "labs": 30,
                "tests": 35,
                "homework": 20,
                "projects": 15
            },
            "prerequisites": ["Basic math skills", "Reading comprehension"],
            "learning_outcomes": [
                "Understand scientific method and inquiry",
                "Apply scientific principles to real-world problems",
                "Design and conduct scientific investigations",
                "Communicate scientific information effectively"
            ],
            "units": [
                {
                    "title": "Introduction to Scientific Inquiry",
                    "description": "Foundational principles of scientific method, hypothesis testing, and data analysis.",
                    "assessment_methods": ["Lab reports", "Hypothesis testing", "Data analysis"],
                    "resources": ["Scientific method worksheets", "Lab safety guide"],
                    "projects": ["Design simple experiment"],
                    "objectives": [
                        {
                            "title": "Scientific Method",
                            "description": "Understand and apply the steps of scientific inquiry",
                            "standard": "NGSS.SCI-HS.1",
                            "estimated_time": 45,
                            "assessment_criteria": ["Identify variables", "Form testable hypotheses"]
                        }
                    ]
                },
                {
                    "title": "Chemistry Fundamentals",
                    "description": "Atomic structure, chemical bonding, reactions, and stoichiometry.",
                    "assessment_methods": ["Lab experiments", "Chemical calculations", "Reaction analysis"],
                    "resources": ["Periodic table", "Molecular model kit"],
                    "projects": ["Chemical reaction demonstrations"],
                    "objectives": [
                        {
                            "title": "Atomic Structure",
                            "description": "Understand atomic structure and electron configuration",
                            "standard": "NGSS.SCI-HS.2",
                            "estimated_time": 60,
                            "assessment_criteria": ["Draw electron configurations", "Predict element properties"]
                        }
                    ]
                },
                {
                    "title": "Biology: Life Systems",
                    "description": "Cell structure, genetics, evolution, and ecology.",
                    "assessment_methods": ["Microscopy labs", "Genetic crosses", "Ecosystem analysis"],
                    "resources": ["Microscope", "DNA model", "Field guides"],
                    "projects": ["Ecosystem study", "Genetic inheritance project"],
                    "objectives": [
                        {
                            "title": "Cell Biology",
                            "description": "Understand cell structure and function",
                            "standard": "NGSS.SCI-HS.3",
                            "estimated_time": 75,
                            "assessment_criteria": ["Identify cell organelles", "Explain cellular processes"]
                        }
                    ]
                },
                {
                    "title": "Physics: Forces and Motion",
                    "description": "Mechanics, energy, waves, and electricity.",
                    "assessment_methods": ["Physics labs", "Problem solving", "Demonstrations"],
                    "resources": ["Physics equipment", "Calculator", "Video analysis software"],
                    "projects": ["Physics demonstration", "Energy efficiency analysis"],
                    "objectives": [
                        {
                            "title": "Newton's Laws",
                            "description": "Apply Newton's laws to real-world situations",
                            "standard": "NGSS.SCI-HS.4",
                            "estimated_time": 90,
                            "assessment_criteria": ["Solve force problems", "Design force experiments"]
                        }
                    ]
                },
                {
                    "title": "Environmental Science",
                    "description": "Ecosystems, sustainability, and environmental impact.",
                    "assessment_methods": ["Field studies", "Impact assessments", "Solution proposals"],
                    "resources": ["Environmental monitoring tools", "GIS software"],
                    "projects": ["Environmental impact study", "Sustainability plan"],
                    "objectives": [
                        {
                            "title": "Ecosystem Dynamics",
                            "description": "Understand ecosystem interactions and energy flow",
                            "standard": "NGSS.SCI-HS.5",
                            "estimated_time": 60,
                            "assessment_criteria": ["Analyze food webs", "Predict environmental changes"]
                        }
                    ]
                }
            ]
        }

    def _get_arts_template(self) -> Dict[str, Any]:
        return {
            "title": "Visual and Performing Arts",
            "description": "Creative expression through visual arts, music, theater, and digital media.",
            "standards": ["National Core Arts Standards", "ISTE"],
            "materials": ["Art supplies", "Musical instruments", "Digital media tools", "Performance space"],
            "grading_policy": {
                "projects": 40,
                "performances": 30,
                "critiques": 20,
                "participation": 10
            },
            "prerequisites": ["Basic creativity skills"],
            "learning_outcomes": [
                "Create original artistic works",
                "Analyze and critique art",
                "Understand art history and cultural context",
                "Present and perform artistic works"
            ],
            "units": [
                {
                    "title": "Visual Arts Fundamentals",
                    "description": "Elements of art, principles of design, and basic techniques.",
                    "assessment_methods": ["Portfolio reviews", "Technique demonstrations", "Artist statements"],
                    "resources": ["Art supplies", "Digital cameras", "Art history books"],
                    "projects": ["Personal artwork series", "Art technique exploration"],
                    "objectives": [
                        {
                            "title": "Elements of Art",
                            "description": "Master the basic elements: line, shape, color, texture, space",
                            "standard": "VA.1",
                            "estimated_time": 60,
                            "assessment_criteria": ["Create compositions", "Analyze artwork elements"]
                        }
                    ]
                },
                {
                    "title": "Digital Media Arts",
                    "description": "Digital photography, graphic design, and multimedia creation.",
                    "assessment_methods": ["Digital portfolios", "Design critiques", "Technical proficiency"],
                    "resources": ["Digital cameras", "Design software", "Tablets"],
                    "projects": ["Digital art series", "Multimedia presentation"],
                    "objectives": [
                        {
                            "title": "Digital Composition",
                            "description": "Create compelling digital compositions using various media",
                            "standard": "VA.2",
                            "estimated_time": 75,
                            "assessment_criteria": ["Apply design principles", "Use digital tools effectively"]
                        }
                    ]
                },
                {
                    "title": "Performing Arts: Theater",
                    "description": "Acting, stagecraft, and theatrical production.",
                    "assessment_methods": ["Performances", "Script analysis", "Production roles"],
                    "resources": ["Stage props", "Lighting equipment", "Costume materials"],
                    "projects": ["One-act play production", "Character development exercises"],
                    "objectives": [
                        {
                            "title": "Acting Techniques",
                            "description": "Develop acting skills and character interpretation",
                            "standard": "TH.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Demonstrate character work", "Collaborate in ensemble"]
                        }
                    ]
                },
                {
                    "title": "Music and Sound",
                    "description": "Music theory, composition, and audio production.",
                    "assessment_methods": ["Compositions", "Performances", "Music analysis"],
                    "resources": ["Musical instruments", "Recording equipment", "Music software"],
                    "projects": ["Original composition", "Audio production piece"],
                    "objectives": [
                        {
                            "title": "Music Theory",
                            "description": "Understand music theory and composition principles",
                            "standard": "MU.1",
                            "estimated_time": 60,
                            "assessment_criteria": ["Analyze musical works", "Create original compositions"]
                        }
                    ]
                }
            ]
        }

    def _get_social_studies_template(self) -> Dict[str, Any]:
        return {
            "title": "Social Studies: World History and Cultures",
            "description": "Study of human societies, cultures, and historical development.",
            "standards": ["C3 Framework", "Common Core"],
            "materials": ["Textbooks", "Maps", "Primary sources", "Documentary films"],
            "grading_policy": {
                "essays": 30,
                "projects": 25,
                "tests": 25,
                "participation": 20
            },
            "prerequisites": ["Basic reading and writing skills"],
            "learning_outcomes": [
                "Understand historical causation and continuity",
                "Analyze complex historical sources",
                "Evaluate historical interpretations",
                "Communicate historical arguments effectively"
            ],
            "units": [
                {
                    "title": "Ancient Civilizations",
                    "description": "Development of early human societies and civilizations.",
                    "assessment_methods": ["Document analysis", "Timeline creation", "Cultural comparisons"],
                    "resources": ["Primary source documents", "Maps", "Artifacts"],
                    "projects": ["Civilization comparison project", "Ancient technology analysis"],
                    "objectives": [
                        {
                            "title": "River Valley Civilizations",
                            "description": "Analyze the development of early civilizations",
                            "standard": "SS.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Compare civilizations", "Explain cultural achievements"]
                        }
                    ]
                },
                {
                    "title": "World Religions and Philosophies",
                    "description": "Major world religions and philosophical traditions.",
                    "assessment_methods": ["Comparative analysis", "Philosophy debates", "Ethical discussions"],
                    "resources": ["Religious texts", "Philosophy readings", "Discussion guides"],
                    "projects": ["Religious comparison", "Philosophy symposium"],
                    "objectives": [
                        {
                            "title": "Major World Religions",
                            "description": "Understand beliefs, practices, and cultural impact",
                            "standard": "SS.2",
                            "estimated_time": 75,
                            "assessment_criteria": ["Compare religious beliefs", "Analyze cultural impacts"]
                        }
                    ]
                },
                {
                    "title": "Modern World History",
                    "description": "Global interactions and modern historical developments.",
                    "assessment_methods": ["Primary source analysis", "Historical debates", "Research projects"],
                    "resources": ["Primary documents", "Historical maps", "Multimedia resources"],
                    "projects": ["Historical research paper", "Modern conflicts analysis"],
                    "objectives": [
                        {
                            "title": "Industrial Revolution",
                            "description": "Analyze causes and effects of industrialization",
                            "standard": "SS.3",
                            "estimated_time": 90,
                            "assessment_criteria": ["Explain economic changes", "Analyze social impacts"]
                        }
                    ]
                },
                {
                    "title": "Contemporary Global Issues",
                    "description": "Current global challenges and international relations.",
                    "assessment_methods": ["Policy analysis", "Debates", "Solution proposals"],
                    "resources": ["News sources", "Policy documents", "Global data"],
                    "projects": ["Global issue research", "International relations simulation"],
                    "objectives": [
                        {
                            "title": "Global Challenges",
                            "description": "Understand contemporary global issues and solutions",
                            "standard": "SS.4",
                            "estimated_time": 75,
                            "assessment_criteria": ["Analyze global problems", "Propose solutions"]
                        }
                    ]
                }
            ]
        }

    def _get_service_learning_template(self) -> Dict[str, Any]:
        return {
            "title": "Service Learning: Community Engagement and Leadership",
            "description": "Hands-on learning through community service and civic engagement.",
            "standards": ["Service Learning Standards", "Leadership Standards"],
            "materials": ["Service log books", "Project planning tools", "Community resources"],
            "grading_policy": {
                "service_hours": 30,
                "reflection_essays": 25,
                "project_planning": 20,
                "presentation": 15,
                "leadership": 10
            },
            "prerequisites": ["Community service interest", "Basic communication skills"],
            "learning_outcomes": [
                "Develop leadership and teamwork skills",
                "Understand community needs and resources",
                "Apply academic knowledge to real-world problems",
                "Reflect on personal growth and social responsibility"
            ],
            "units": [
                {
                    "title": "Service Learning Foundations",
                    "description": "Understanding service learning principles and community needs.",
                    "assessment_methods": ["Needs assessment", "Service plans", "Reflection journals"],
                    "resources": ["Community directories", "Service organization guides"],
                    "projects": ["Community needs assessment", "Personal service plan"],
                    "objectives": [
                        {
                            "title": "Service Learning Principles",
                            "description": "Understand the principles and benefits of service learning",
                            "standard": "SL.1",
                            "estimated_time": 45,
                            "assessment_criteria": ["Explain service learning", "Identify community needs"]
                        }
                    ]
                },
                {
                    "title": "Project Planning and Implementation",
                    "description": "Planning and executing community service projects.",
                    "assessment_methods": ["Project proposals", "Implementation logs", "Progress reports"],
                    "resources": ["Project planning templates", "Community partner contacts"],
                    "projects": ["Community service project", "Leadership initiative"],
                    "objectives": [
                        {
                            "title": "Project Management",
                            "description": "Plan and manage community service projects effectively",
                            "standard": "SL.2",
                            "estimated_time": 90,
                            "assessment_criteria": ["Create project plans", "Manage project execution"]
                        }
                    ]
                },
                {
                    "title": "Leadership and Collaboration",
                    "description": "Developing leadership skills and working in teams.",
                    "assessment_methods": ["Leadership assessments", "Team evaluations", "Peer reviews"],
                    "resources": ["Leadership development materials", "Team building activities"],
                    "projects": ["Leadership workshop", "Team collaboration project"],
                    "objectives": [
                        {
                            "title": "Leadership Skills",
                            "description": "Develop and demonstrate leadership abilities",
                            "standard": "SL.3",
                            "estimated_time": 60,
                            "assessment_criteria": ["Demonstrate leadership", "Collaborate effectively"]
                        }
                    ]
                },
                {
                    "title": "Reflection and Impact Assessment",
                    "description": "Reflecting on service experiences and assessing impact.",
                    "assessment_methods": ["Reflection portfolios", "Impact assessments", "Presentations"],
                    "resources": ["Reflection guides", "Impact assessment tools"],
                    "projects": ["Service impact study", "Personal growth portfolio"],
                    "objectives": [
                        {
                            "title": "Critical Reflection",
                            "description": "Reflect deeply on service experiences and personal growth",
                            "standard": "SL.4",
                            "estimated_time": 75,
                            "assessment_criteria": ["Analyze experiences", "Assess personal growth"]
                        }
                    ]
                }
            ]
        }

    def _get_math_template(self) -> Dict[str, Any]:
        return {
            "title": "Mathematics: Algebra and Beyond",
            "description": "Advanced mathematical reasoning, problem-solving, and applications.",
            "standards": ["Common Core Math", "Mathematical Practices"],
            "materials": ["Graphing calculator", "Mathematics software", "Manipulatives"],
            "grading_policy": {
                "problem_sets": 30,
                "tests": 35,
                "projects": 20,
                "participation": 15
            },
            "prerequisites": ["Basic algebra", "Geometry"],
            "learning_outcomes": [
                "Solve complex mathematical problems",
                "Apply mathematics to real-world situations",
                "Use technology effectively in mathematics",
                "Communicate mathematical reasoning clearly"
            ],
            "units": [
                {
                    "title": "Advanced Algebra",
                    "description": "Polynomial functions, rational expressions, and systems of equations.",
                    "assessment_methods": ["Problem solving", "Equation solving", "Function analysis"],
                    "resources": ["Graphing calculator", "Algebra software"],
                    "projects": ["Mathematical modeling project", "Function analysis study"],
                    "objectives": [
                        {
                            "title": "Polynomial Functions",
                            "description": "Analyze and solve polynomial equations and inequalities",
                            "standard": "Math.A.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Solve polynomial equations", "Graph polynomial functions"]
                        }
                    ]
                },
                {
                    "title": "Trigonometry and Analytic Geometry",
                    "description": "Trigonometric functions, identities, and coordinate geometry.",
                    "assessment_methods": ["Trigonometric proofs", "Coordinate geometry", "Modeling problems"],
                    "resources": ["Graphing software", "Trigonometry tables"],
                    "projects": ["Trigonometric modeling", "Geometry proofs"],
                    "objectives": [
                        {
                            "title": "Trigonometric Functions",
                            "description": "Understand and apply trigonometric functions and identities",
                            "standard": "Math.T.1",
                            "estimated_time": 75,
                            "assessment_criteria": ["Solve trigonometric equations", "Prove trigonometric identities"]
                        }
                    ]
                },
                {
                    "title": "Statistics and Probability",
                    "description": "Data analysis, statistical inference, and probability theory.",
                    "assessment_methods": ["Statistical analysis", "Probability problems", "Data interpretation"],
                    "resources": ["Statistics software", "Data sets", "Calculator"],
                    "projects": ["Statistical research project", "Probability simulations"],
                    "objectives": [
                        {
                            "title": "Statistical Analysis",
                            "description": "Apply statistical methods to analyze and interpret data",
                            "standard": "Math.S.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Calculate statistics", "Interpret data patterns"]
                        }
                    ]
                },
                {
                    "title": "Calculus Preparation",
                    "description": "Limits, derivatives, and integrals - introduction to calculus.",
                    "assessment_methods": ["Limit problems", "Derivative calculations", "Integration problems"],
                    "resources": ["Graphing calculator", "Calculus software"],
                    "projects": ["Rate of change analysis", "Area calculations"],
                    "objectives": [
                        {
                            "title": "Limits and Continuity",
                            "description": "Understand limits and continuity in functions",
                            "standard": "Math.C.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Evaluate limits", "Analyze function continuity"]
                        }
                    ]
                }
            ]
        }

    def _get_language_template(self) -> Dict[str, Any]:
        return {
            "title": "Language Arts and Literacy",
            "description": "Advanced reading, writing, speaking, and critical thinking skills.",
            "standards": ["Common Core ELA", "Writing Standards"],
            "materials": ["Literature anthologies", "Writing journals", "Research databases"],
            "grading_policy": {
                "essays": 30,
                "reading_responses": 20,
                "presentations": 20,
                "tests": 15,
                "participation": 15
            },
            "prerequisites": ["Basic reading and writing skills"],
            "learning_outcomes": [
                "Analyze complex literary works",
                "Write clear and effective arguments",
                "Communicate effectively in various contexts",
                "Think critically about language and literature"
            ],
            "units": [
                {
                    "title": "Literary Analysis and Interpretation",
                    "description": "Close reading and analysis of literary texts from various genres.",
                    "assessment_methods": ["Literary analysis essays", "Textual evidence", "Discussion participation"],
                    "resources": ["Literary texts", "Analysis guides", "Discussion protocols"],
                    "projects": ["Literary analysis paper", "Genre study project"],
                    "objectives": [
                        {
                            "title": "Text Analysis",
                            "description": "Analyze literary texts using various critical approaches",
                            "standard": "ELA.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Identify literary devices", "Support interpretations with evidence"]
                        }
                    ]
                },
                {
                    "title": "Argumentative Writing",
                    "description": "Developing and defending arguments through writing.",
                    "assessment_methods": ["Argumentative essays", "Research papers", "Peer review"],
                    "resources": ["Writing guides", "Research databases", "Citation tools"],
                    "projects": ["Research argument paper", "Policy analysis essay"],
                    "objectives": [
                        {
                            "title": "Argument Development",
                            "description": "Develop and defend arguments with evidence and reasoning",
                            "standard": "ELA.2",
                            "estimated_time": 120,
                            "assessment_criteria": ["Present clear arguments", "Support claims with evidence"]
                        }
                    ]
                },
                {
                    "title": "Public Speaking and Communication",
                    "description": "Effective oral communication and presentation skills.",
                    "assessment_methods": ["Presentations", "Debates", "Discussion leadership"],
                    "resources": ["Presentation tools", "Debate guides", "Video recording"],
                    "projects": ["Major presentation", "Debate tournament"],
                    "objectives": [
                        {
                            "title": "Oral Communication",
                            "description": "Deliver effective oral presentations and participate in discussions",
                            "standard": "ELA.3",
                            "estimated_time": 60,
                            "assessment_criteria": ["Deliver presentations", "Participate effectively in discussions"]
                        }
                    ]
                },
                {
                    "title": "Research and Information Literacy",
                    "description": "Conducting research and evaluating information sources.",
                    "assessment_methods": ["Research projects", "Source evaluation", "Information synthesis"],
                    "resources": ["Research databases", "Citation guides", "Information evaluation tools"],
                    "projects": ["Major research project", "Information literacy portfolio"],
                    "objectives": [
                        {
                            "title": "Research Skills",
                            "description": "Conduct effective research and evaluate information sources",
                            "standard": "ELA.4",
                            "estimated_time": 90,
                            "assessment_criteria": ["Conduct thorough research", "Evaluate source credibility"]
                        }
                    ]
                }
            ]
        }

    def _get_biliteracy_template(self) -> Dict[str, Any]:
        return {
            "title": "Biliteracy/Dual Language Program",
            "description": "Development of proficiency in two languages with academic content.",
            "standards": ["WIDA", "Common Core", "Language Standards"],
            "materials": ["Dual language texts", "Language learning software", "Cultural resources"],
            "grading_policy": {
                "language_assessment": 25,
                "content_assessment": 35,
                "cultural_projects": 20,
                "participation": 20
            },
            "prerequisites": ["Basic proficiency in one language"],
            "learning_outcomes": [
                "Develop proficiency in two languages",
                "Understand cultural contexts and perspectives",
                "Apply academic content in multiple languages",
                "Value and respect linguistic diversity"
            ],
            "units": [
                {
                    "title": "Language Fundamentals",
                    "description": "Basic vocabulary, grammar, and communication in both languages.",
                    "assessment_methods": ["Language assessments", "Conversational practice", "Vocabulary quizzes"],
                    "resources": ["Language learning apps", "Dual language dictionaries"],
                    "projects": ["Language immersion activity", "Cultural presentation"],
                    "objectives": [
                        {
                            "title": "Basic Communication",
                            "description": "Develop basic communication skills in both languages",
                            "standard": "BL.1",
                            "estimated_time": 60,
                            "assessment_criteria": ["Use basic vocabulary", "Form simple sentences"]
                        }
                    ]
                },
                {
                    "title": "Academic Language Development",
                    "description": "Academic vocabulary and concepts in both languages.",
                    "assessment_methods": ["Academic writing", "Content discussions", "Vocabulary building"],
                    "resources": ["Academic texts", "Vocabulary builders", "Language support tools"],
                    "projects": ["Academic presentation", "Bilingual research project"],
                    "objectives": [
                        {
                            "title": "Academic Vocabulary",
                            "description": "Build academic vocabulary in both languages",
                            "standard": "BL.2",
                            "estimated_time": 75,
                            "assessment_criteria": ["Use academic terms", "Explain concepts in both languages"]
                        }
                    ]
                },
                {
                    "title": "Cultural Understanding",
                    "description": "Cultural perspectives, traditions, and cross-cultural communication.",
                    "assessment_methods": ["Cultural analysis", "Cross-cultural projects", "Cultural presentations"],
                    "resources": ["Cultural materials", "Multicultural literature", "Media resources"],
                    "projects": ["Cultural exchange project", "Multicultural festival"],
                    "objectives": [
                        {
                            "title": "Cultural Perspectives",
                            "description": "Understand and appreciate different cultural perspectives",
                            "standard": "BL.3",
                            "estimated_time": 90,
                            "assessment_criteria": ["Compare cultural practices", "Demonstrate cultural understanding"]
                        }
                    ]
                },
                {
                    "title": "Advanced Biliteracy Skills",
                    "description": "Advanced reading, writing, and thinking in both languages.",
                    "assessment_methods": ["Biliteracy assessments", "Advanced projects", "Portfolio reviews"],
                    "resources": ["Advanced texts", "Writing support", "Assessment tools"],
                    "projects": ["Biliteracy portfolio", "Advanced research project"],
                    "objectives": [
                        {
                            "title": "Advanced Biliteracy",
                            "description": "Demonstrate advanced proficiency in both languages",
                            "standard": "BL.4",
                            "estimated_time": 120,
                            "assessment_criteria": ["Read complex texts", "Write academic content in both languages"]
                        }
                    ]
                }
            ]
        }

    def _get_social_justice_template(self) -> Dict[str, Any]:
        return {
            "title": "Social Justice Education",
            "description": "Understanding inequality, promoting equity, and advocating for justice.",
            "standards": ["Social Justice Standards", "Civic Engagement"],
            "materials": ["Social justice texts", "Documentary films", "Case studies"],
            "grading_policy": {
                "research_projects": 30,
                "activism_projects": 25,
                "reflections": 20,
                "discussions": 15,
                "participation": 10
            },
            "prerequisites": ["Open mind", "Respect for diverse perspectives"],
            "learning_outcomes": [
                "Understand systemic inequality and injustice",
                "Analyze power dynamics and privilege",
                "Develop strategies for social change",
                "Advocate effectively for justice"
            ],
            "units": [
                {
                    "title": "Understanding Inequality",
                    "description": "Exploring different forms of inequality and their root causes.",
                    "assessment_methods": ["Issue analysis", "Inequality mapping", "Personal reflections"],
                    "resources": ["Inequality data", "Personal narratives", "Historical documents"],
                    "projects": ["Inequality analysis project", "Privilege assessment"],
                    "objectives": [
                        {
                            "title": "Types of Inequality",
                            "description": "Identify and analyze different forms of social inequality",
                            "standard": "SJ.1",
                            "estimated_time": 90,
                            "assessment_criteria": ["Identify inequality types", "Explain root causes"]
                        }
                    ]
                },
                {
                    "title": "Power and Privilege",
                    "description": "Understanding power dynamics, privilege, and intersectionality.",
                    "assessment_methods": ["Privilege analysis", "Power mapping", "Intersectional analysis"],
                    "resources": ["Privilege exercises", "Power analysis tools", "Intersectionality frameworks"],
                    "projects": ["Privilege inventory", "Power analysis project"],
                    "objectives": [
                        {
                            "title": "Privilege Awareness",
                            "description": "Develop awareness of personal and systemic privilege",
                            "standard": "SJ.2",
                            "estimated_time": 75,
                            "assessment_criteria": ["Identify personal privilege", "Analyze power dynamics"]
                        }
                    ]
                },
                {
                    "title": "Social Justice Movements",
                    "description": "Historical and contemporary movements for social justice.",
                    "assessment_methods": ["Movement analysis", "Activist biographies", "Strategy evaluation"],
                    "resources": ["Movement histories", "Activist writings", "Documentary films"],
                    "projects": ["Movement timeline", "Activist research project"],
                    "objectives": [
                        {
                            "title": "Movement Analysis",
                            "description": "Analyze social justice movements and their strategies",
                            "standard": "SJ.3",
                            "estimated_time": 90,
                            "assessment_criteria": ["Explain movement goals", "Evaluate movement strategies"]
                        }
                    ]
                },
                {
                    "title": "Taking Action",
                    "description": "Developing and implementing strategies for social change.",
                    "assessment_methods": ["Action plans", "Implementation logs", "Impact assessment"],
                    "resources": ["Action planning guides", "Community resources", "Evaluation tools"],
                    "projects": ["Social action project", "Advocacy campaign"],
                    "objectives": [
                        {
                            "title": "Social Action",
                            "description": "Plan and implement effective social justice actions",
                            "standard": "SJ.4",
                            "estimated_time": 120,
                            "assessment_criteria": ["Develop action plans", "Implement social change"]
                        }
                    ]
                }
            ]
        }

    def _get_classroom_management_template(self) -> Dict[str, Any]:
        return {
            "title": "Classroom Management and Instructional Strategies",
            "description": "Effective classroom management and evidence-based teaching strategies.",
            "standards": ["Teaching Standards", "Classroom Management Standards"],
            "materials": ["Management resources", "Strategy guides", "Observation tools"],
            "grading_policy": {
                "management_plan": 25,
                "strategy_implementation": 25,
                "reflections": 20,
                "peer_observations": 15,
                "final_project": 15
            },
            "prerequisites": ["Education coursework", "Classroom observation experience"],
            "learning_outcomes": [
                "Create positive classroom environments",
                "Implement effective management strategies",
                "Use evidence-based instructional methods",
                "Reflect on and improve teaching practice"
            ],
            "units": [
                {
                    "title": "Classroom Environment and Culture",
                    "description": "Creating positive, inclusive classroom environments.",
                    "assessment_methods": ["Environment plans", "Culture assessments", "Student feedback"],
                    "resources": ["Environment design tools", "Culture building activities"],
                    "projects": ["Classroom design project", "Culture building plan"],
                    "objectives": [
                        {
                            "title": "Positive Environment",
                            "description": "Create and maintain positive classroom environments",
                            "standard": "CM.1",
                            "estimated_time": 60,
                            "assessment_criteria": ["Design classroom layout", "Establish classroom norms"]
                        }
                    ]
                },
                {
                    "title": "Behavior Management",
                    "description": "Preventing and addressing student behavior challenges.",
                    "assessment_methods": ["Management plans", "Behavior scenarios", "Strategy implementation"],
                    "resources": ["Behavior management guides", "Scenario training", "Intervention strategies"],
                    "projects": ["Behavior management plan", "Intervention case study"],
                    "objectives": [
                        {
                            "title": "Behavior Strategies",
                            "description": "Implement effective behavior management strategies",
                            "standard": "CM.2",
                            "estimated_time": 75,
                            "assessment_criteria": ["Develop behavior plans", "Apply intervention strategies"]
                        }
                    ]
                },
                {
                    "title": "Instructional Strategies",
                    "description": "Evidence-based teaching methods and strategies.",
                    "assessment_methods": ["Lesson planning", "Strategy implementation", "Student outcomes"],
                    "resources": ["Strategy guides", "Lesson planning tools", "Assessment methods"],
                    "projects": ["Strategy implementation project", "Lesson study"],
                    "objectives": [
                        {
                            "title": "Teaching Strategies",
                            "description": "Apply evidence-based instructional strategies",
                            "standard": "CM.3",
                            "estimated_time": 90,
                            "assessment_criteria": ["Implement strategies", "Assess student learning"]
                        }
                    ]
                },
                {
                    "title": "Assessment and Reflection",
                    "description": "Assessment design and reflective teaching practice.",
                    "assessment_methods": ["Assessment creation", "Teaching reflections", "Improvement plans"],
                    "resources": ["Assessment tools", "Reflection guides", "Data analysis tools"],
                    "projects": ["Assessment design project", "Teaching portfolio"],
                    "objectives": [
                        {
                            "title": "Reflective Practice",
                            "description": "Reflect on teaching practice and make improvements",
                            "standard": "CM.4",
                            "estimated_time": 60,
                            "assessment_criteria": ["Analyze teaching practice", "Develop improvement plans"]
                        }
                    ]
                }
            ]
        }

    def _get_health_template(self) -> Dict[str, Any]:
        return {
            "title": "Health and Fitness Education",
            "description": "Comprehensive health education and physical fitness development.",
            "standards": ["National Health Standards", "Physical Education Standards"],
            "materials": ["Fitness equipment", "Health education resources", "Assessment tools"],
            "grading_policy": {
                "fitness_assessments": 25,
                "health_projects": 25,
                "participation": 20,
                "knowledge_tests": 15,
                "reflections": 15
            },
            "prerequisites": ["Basic movement skills"],
            "learning_outcomes": [
                "Understand health concepts and behaviors",
                "Develop physical fitness and skills",
                "Make healthy lifestyle choices",
                "Understand mental and emotional health"
            ],
            "units": [
                {
                    "title": "Personal Health and Wellness",
                    "description": "Understanding personal health, nutrition, and wellness.",
                    "assessment_methods": ["Health assessments", "Nutrition logs", "Wellness plans"],
                    "resources": ["Health assessment tools", "Nutrition guides", "Wellness resources"],
                    "projects": ["Personal wellness plan", "Nutrition analysis project"],
                    "objectives": [
                        {
                            "title": "Health Concepts",
                            "description": "Understand basic health concepts and behaviors",
                            "standard": "HE.1",
                            "estimated_time": 60,
                            "assessment_criteria": ["Explain health concepts", "Identify healthy behaviors"]
                        }
                    ]
                },
                {
                    "title": "Physical Fitness",
                    "description": "Developing cardiovascular, muscular, and flexibility fitness.",
                    "assessment_methods": ["Fitness tests", "Skill assessments", "Progress tracking"],
                    "resources": ["Fitness equipment", "Assessment tools", "Training guides"],
                    "projects": ["Fitness improvement plan", "Skill development project"],
                    "objectives": [
                        {
                            "title": "Fitness Components",
                            "description": "Develop all components of physical fitness",
                            "standard": "HE.2",
                            "estimated_time": 90,
                            "assessment_criteria": ["Demonstrate fitness skills", "Show fitness improvement"]
                        }
                    ]
                },
                {
                    "title": "Mental and Emotional Health",
                    "description": "Understanding mental health, stress management, and emotional wellness.",
                    "assessment_methods": ["Mental health surveys", "Stress management logs", "Emotional awareness"],
                    "resources": ["Mental health resources", "Stress management tools", "Mindfulness activities"],
                    "projects": ["Mental health awareness project", "Stress management plan"],
                    "objectives": [
                        {
                            "title": "Emotional Wellness",
                            "description": "Understand and promote mental and emotional health",
                            "standard": "HE.3",
                            "estimated_time": 75,
                            "assessment_criteria": ["Identify mental health strategies", "Practice stress management"]
                        }
                    ]
                },
                {
                    "title": "Health Education and Advocacy",
                    "description": "Health education, disease prevention, and health advocacy.",
                    "assessment_methods": ["Health presentations", "Advocacy projects", "Health campaigns"],
                    "resources": ["Health education materials", "Advocacy tools", "Community resources"],
                    "projects": ["Health education campaign", "Disease prevention project"],
                    "objectives": [
                        {
                            "title": "Health Advocacy",
                            "description": "Promote health education and advocate for healthy communities",
                            "standard": "HE.4",
                            "estimated_time": 90,
                            "assessment_criteria": ["Create health campaigns", "Advocate for health issues"]
                        }
                    ]
                }
            ]
        }
