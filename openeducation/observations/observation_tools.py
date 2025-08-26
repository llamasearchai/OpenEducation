from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..rag.embeddings import OpenAIEmbedding
from ..utils.io import read_json, write_json


@dataclass
class ObservationCriteria:
    """Research-based observation criteria for classroom assessment."""
    id: str
    category: str
    name: str
    description: str
    indicators: List[str] = field(default_factory=list)
    scoring_method: str = "scale_1_5"  # scale_1_5, yes_no, frequency
    weight: float = 1.0
    standard: str = ""  # NAEYC, CLASS, ECERS, etc.


@dataclass
class ClassroomObservation:
    """Complete classroom observation record."""
    id: str
    classroom_id: str
    teacher_id: str
    observer_id: str
    observation_date: str
    start_time: str
    end_time: str
    duration_minutes: int
    focus_area: str  # curriculum, instruction, environment, interactions
    observation_type: str  # announced, unannounced, focused
    notes: str = ""
    criteria_scores: Dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    follow_up_date: Optional[str] = None
    status: str = "draft"  # draft, completed, reviewed, action_plan_created


@dataclass
class TeacherProfile:
    """Teacher profile with observation history and development data."""
    id: str
    name: str
    email: str
    classroom_id: str
    hire_date: str
    credentials: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    development_goals: List[str] = field(default_factory=list)
    coaching_history: List[str] = field(default_factory=list)
    observation_history: List[str] = field(default_factory=list)
    last_observation: Optional[str] = None
    next_observation: Optional[str] = None


class ObservationToolsManager:
    """Manage classroom observation tools and data collection."""

    def __init__(self, data_dir: str = "data/observations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.observation_criteria = self._load_default_criteria()
        self.criteria_embeddings = self.vectorize_criteria()

    def vectorize_criteria(self) -> Dict[str, List[float]]:
        """Generate and store vector embeddings for all observation criteria."""
        embedding_model = OpenAIEmbedding()
        embeddings = {}
        
        all_criteria = [item for sublist in self.observation_criteria.values() for item in sublist]
        
        texts_to_embed = []
        for criteria in all_criteria:
            text = f"Category: {criteria.category}. Criteria: {criteria.name}. Description: {criteria.description}. Indicators: {', '.join(criteria.indicators)}"
            texts_to_embed.append(text)
            
        vectors = embedding_model.embed(texts_to_embed)
        
        for criteria, vector in zip(all_criteria, vectors):
            embeddings[criteria.id] = vector
            
        return embeddings

    def _load_default_criteria(self) -> Dict[str, List[ObservationCriteria]]:
        """Load research-based observation criteria."""
        return {
            "classroom_environment": [
                ObservationCriteria(
                    id="env_1",
                    category="classroom_environment",
                    name="Learning Centers",
                    description="Organization and accessibility of learning centers",
                    indicators=[
                        "Centers are well-organized and labeled",
                        "Materials are accessible to children",
                        "Centers promote different types of learning",
                        "Safety considerations are evident"
                    ],
                    standard="NAEYC"
                ),
                ObservationCriteria(
                    id="env_2",
                    category="classroom_environment",
                    name="Room Arrangement",
                    description="Physical layout supports learning and interaction",
                    indicators=[
                        "Furniture arrangement encourages interaction",
                        "Traffic flow is smooth and safe",
                        "Space utilization is efficient",
                        "Visual access to teacher is maintained"
                    ],
                    standard="ECERS"
                )
            ],
            "teacher_child_interactions": [
                ObservationCriteria(
                    id="int_1",
                    category="teacher_child_interactions",
                    name="Responsive Interactions",
                    description="Teacher responds appropriately to children's needs and interests",
                    indicators=[
                        "Teacher follows children's lead",
                        "Responses are timely and appropriate",
                        "Teacher expands on children's ideas",
                        "Emotional support is provided"
                    ],
                    standard="CLASS"
                ),
                ObservationCriteria(
                    id="int_2",
                    category="teacher_child_interactions",
                    name="Language Modeling",
                    description="Teacher models rich language and extends children's communication",
                    indicators=[
                        "Expands on children's vocabulary",
                        "Uses open-ended questions",
                        "Narrates activities and experiences",
                        "Encourages peer communication"
                    ],
                    standard="CLASS"
                )
            ],
            "curriculum_implementation": [
                ObservationCriteria(
                    id="curr_1",
                    category="curriculum_implementation",
                    name="Intentional Teaching",
                    description="Teaching is purposeful and connected to learning goals",
                    indicators=[
                        "Activities align with curriculum goals",
                        "Teacher has clear learning objectives",
                        "Instruction is differentiated",
                        "Assessment informs teaching"
                    ],
                    standard="NAEYC"
                ),
                ObservationCriteria(
                    id="curr_2",
                    category="curriculum_implementation",
                    name="Child Engagement",
                    description="Children are actively engaged in meaningful learning",
                    indicators=[
                        "Children show interest and enthusiasm",
                        "Multiple learning modalities are used",
                        "Children take initiative in learning",
                        "Deep engagement in activities is evident"
                    ],
                    standard="NAEYC"
                )
            ]
        }

    def create_observation(self, classroom_id: str, teacher_id: str, observer_id: str,
                          focus_area: str, duration_minutes: int = 30) -> ClassroomObservation:
        """Create a new classroom observation."""
        obs_id = f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        observation = ClassroomObservation(
            id=obs_id,
            classroom_id=classroom_id,
            teacher_id=teacher_id,
            observer_id=observer_id,
            observation_date=datetime.now().strftime('%Y-%m-%d'),
            start_time=datetime.now().strftime('%H:%M'),
            end_time=(datetime.now() + timedelta(minutes=duration_minutes)).strftime('%H:%M'),
            duration_minutes=duration_minutes,
            focus_area=focus_area,
            observation_type="announced"
        )

        self._save_observation(observation)
        return observation

    def record_criteria_score(self, observation_id: str, criteria_id: str,
                            score: Any, notes: str = "") -> None:
        """Record a score for specific observation criteria."""
        observation = self._load_observation(observation_id)
        if observation:
            observation.criteria_scores[criteria_id] = {
                "score": score,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            self._save_observation(observation)

    def complete_observation(self, observation_id: str, strengths: List[str],
                           areas_for_growth: List[str], recommendations: List[str],
                           follow_up_date: Optional[str] = None) -> None:
        """Complete an observation with summary data."""
        observation = self._load_observation(observation_id)
        if observation:
            observation.strengths = strengths
            observation.areas_for_growth = areas_for_growth
            observation.recommendations = recommendations
            observation.follow_up_date = follow_up_date
            observation.status = "completed"
            observation.end_time = datetime.now().strftime('%H:%M')
            self._save_observation(observation)

    def generate_observation_report(self, observation_id: str) -> Dict[str, Any]:
        """Generate a comprehensive observation report."""
        observation = self._load_observation(observation_id)
        if not observation:
            return {"error": "Observation not found"}

        # Calculate scores summary
        scores_summary = self._calculate_scores_summary(observation)

        report = {
            "observation_id": observation.id,
            "classroom_id": observation.classroom_id,
            "teacher_id": observation.teacher_id,
            "observer_id": observation.observer_id,
            "date": observation.observation_date,
            "focus_area": observation.focus_area,
            "duration": observation.duration_minutes,
            "scores_summary": scores_summary,
            "strengths": observation.strengths,
            "areas_for_growth": observation.areas_for_growth,
            "recommendations": observation.recommendations,
            "follow_up_date": observation.follow_up_date,
            "status": observation.status,
            "generated_at": datetime.now().isoformat()
        }

        return report

    def _calculate_scores_summary(self, observation: ClassroomObservation) -> Dict[str, Any]:
        """Calculate summary statistics for observation scores."""
        scores = observation.criteria_scores
        if not scores:
            return {"total_criteria": 0, "average_score": 0, "scored_criteria": 0}

        total_score = 0
        valid_scores = 0

        for criteria_id, score_data in scores.items():
            score = score_data.get("score", 0)
            if isinstance(score, (int, float)) and score > 0:
                total_score += score
                valid_scores += 1

        average_score = total_score / valid_scores if valid_scores > 0 else 0

        return {
            "total_criteria": len(scores),
            "scored_criteria": valid_scores,
            "average_score": round(average_score, 2),
            "score_distribution": self._get_score_distribution(scores)
        }

    def _get_score_distribution(self, scores: Dict[str, Any]) -> Dict[str, int]:
        """Get distribution of scores across rating levels."""
        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

        for criteria_id, score_data in scores.items():
            score = score_data.get("score", 0)
            if isinstance(score, (int, float)):
                score_key = str(min(5, max(1, int(score))))
                distribution[score_key] += 1

        return distribution

    def get_teacher_observations(self, teacher_id: str) -> List[ClassroomObservation]:
        """Get all observations for a specific teacher."""
        observations = []
        for obs_file in self.data_dir.glob("observation_*.json"):
            try:
                obs_data = read_json(str(obs_file))
                if obs_data.get("teacher_id") == teacher_id:
                    observations.append(ClassroomObservation(**obs_data))
            except Exception:
                continue

        return sorted(observations, key=lambda x: x.observation_date, reverse=True)

    def _save_observation(self, observation: ClassroomObservation) -> None:
        """Save observation to file."""
        filename = f"observation_{observation.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": observation.id,
            "classroom_id": observation.classroom_id,
            "teacher_id": observation.teacher_id,
            "observer_id": observation.observer_id,
            "observation_date": observation.observation_date,
            "start_time": observation.start_time,
            "end_time": observation.end_time,
            "duration_minutes": observation.duration_minutes,
            "focus_area": observation.focus_area,
            "observation_type": observation.observation_type,
            "notes": observation.notes,
            "criteria_scores": observation.criteria_scores,
            "strengths": observation.strengths,
            "areas_for_growth": observation.areas_for_growth,
            "recommendations": observation.recommendations,
            "follow_up_date": observation.follow_up_date,
            "status": observation.status
        }

        write_json(str(filepath), data)

    def _load_observation(self, observation_id: str) -> Optional[ClassroomObservation]:
        """Load observation from file."""
        filename = f"observation_{observation_id}.json"
        filepath = self.data_dir / filename

        if filepath.exists():
            try:
                data = read_json(str(filepath))
                return ClassroomObservation(**data)
            except Exception:
                pass

        return None
