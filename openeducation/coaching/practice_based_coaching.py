from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from ..utils.io import write_json, read_json
from ..observations.observation_tools import ObservationToolsManager
from ..rag.embeddings import OpenAIEmbedding
from ..llm.openai_wrapper import OpenAIWrapper
import numpy as np


@dataclass
class CoachingCycle:
    """A complete coaching cycle with goals, actions, and outcomes."""
    id: str
    teacher_id: str
    coach_id: str
    start_date: str
    target_completion_date: str
    focus_area: str  # specific skill or practice being developed
    current_level: str  # baseline assessment of current practice
    goal_level: str  # desired level of practice
    strategies: List[str] = field(default_factory=list)  # coaching strategies to use
    action_steps: List[str] = field(default_factory=list)  # specific actions teacher will take
    resources_needed: List[str] = field(default_factory=list)
    evidence_of_progress: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    supports_provided: List[str] = field(default_factory=list)
    status: str = "active"  # active, completed, paused, cancelled
    completion_date: Optional[str] = None
    outcome_notes: str = ""


@dataclass
class CoachingSession:
    """Individual coaching session record."""
    id: str
    coaching_cycle_id: str
    session_date: str
    session_type: str  # planning, observation, feedback, reflection, check_in
    duration_minutes: int
    location: str  # classroom, office, remote
    agenda_items: List[str] = field(default_factory=list)
    discussion_topics: List[str] = field(default_factory=list)
    teacher_reflections: List[str] = field(default_factory=list)
    coach_feedback: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    next_session_date: Optional[str] = None
    session_notes: str = ""
    teacher_goals_addressed: List[str] = field(default_factory=list)


@dataclass
class CoachingPlan:
    """Comprehensive coaching plan for an individual or team."""
    id: str
    teacher_id: str
    coach_id: str
    plan_type: str  # individual, team, program_wide
    start_date: str
    end_date: str
    overall_goal: str
    focus_areas: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)
    coaching_cycles: List[str] = field(default_factory=list)  # IDs of related cycles
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    resources_allocated: List[str] = field(default_factory=list)
    evaluation_methods: List[str] = field(default_factory=list)
    status: str = "active"


class PracticeBasedCoachingManager:
    """Manage Practice Based Coaching implementation."""

    def __init__(self, data_dir: str = "data/coaching"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.observation_manager = ObservationToolsManager()
        self.embedding_model = OpenAIEmbedding()
        self.llm = OpenAIWrapper()

    def analyze_observation_notes(self, notes: str, top_k: int = 3) -> Dict[str, Any]:
        """Analyze unstructured observation notes using AI."""
        # 1. Embed the observation notes
        notes_embedding = self.embedding_model.embed([notes])[0]

        # 2. Find the most relevant criteria via semantic search
        criteria_embeddings = self.observation_manager.criteria_embeddings
        
        # Ensure there are criteria to compare against
        if not criteria_embeddings:
            return {"error": "No observation criteria embeddings found. Please initialize the ObservationToolsManager correctly."}

        similarities = self._cosine_similarity(notes_embedding, list(criteria_embeddings.values()))
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matched_criteria_ids = [list(criteria_embeddings.keys())[i] for i in top_indices]
        
        all_criteria = {c.id: c for cat in self.observation_manager.observation_criteria.values() for c in cat}
        matched_criteria = [all_criteria[cid] for cid in matched_criteria_ids]

        # 3. Use LLM to generate a structured analysis
        prompt = self._build_analysis_prompt(notes, matched_criteria)
        analysis_text = self.llm.get_response(prompt)
        
        try:
            analysis_json = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis_json = {"error": "Failed to parse LLM response.", "raw_response": analysis_text}

        return analysis_json

    def _build_analysis_prompt(self, notes: str, criteria: List[Any]) -> str:
        """Build the LLM prompt for analyzing observation notes."""
        criteria_text = "\n\n".join(
            [f"- **{c.name}** (Category: {c.category}): {c.description}" for c in criteria]
        )
        prompt = f"""
        Analyze the following unstructured classroom observation notes.
        Based on the notes, identify strengths, areas for growth, and suggest concrete next steps for a coaching cycle.
        The analysis should be guided by the most relevant observation criteria provided below.

        **Observation Notes:**
        "{notes}"

        **Relevant Observation Criteria:**
        {criteria_text}

        **Output Format:**
        Provide the output as a single JSON object with the following keys:
        - "summary": A brief, one-paragraph summary of the observation.
        - "strengths": A list of observed strengths, directly referencing the notes and criteria.
        - "areas_for_growth": A list of areas for professional growth, referencing the notes and criteria.
        - "suggested_next_steps": A list of actionable next steps for the teacher and coach.
        
        Ensure the output is only the JSON object, with no other text.
        """
        return prompt

    def _cosine_similarity(self, query_vec: np.ndarray, doc_vecs: List[np.ndarray]) -> np.ndarray:
        """Calculate cosine similarity between a query vector and a list of document vectors."""
        query_vec = np.array(query_vec)
        doc_vecs = np.array(doc_vecs)
        
        query_norm = np.linalg.norm(query_vec)
        doc_norms = np.linalg.norm(doc_vecs, axis=1)
        
        # Handle zero vectors to avoid division by zero
        if query_norm == 0 or np.any(doc_norms == 0):
            return np.zeros(len(doc_vecs))
            
        return np.dot(doc_vecs, query_vec) / (doc_norms * query_norm)

    def create_coaching_cycle(self, teacher_id: str, coach_id: str, focus_area: str,
                             current_level: str, goal_level: str, duration_weeks: int = 8) -> CoachingCycle:
        """Create a new coaching cycle following Practice Based Coaching model."""
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cycle = CoachingCycle(
            id=cycle_id,
            teacher_id=teacher_id,
            coach_id=coach_id,
            start_date=datetime.now().strftime('%Y-%m-%d'),
            target_completion_date=(datetime.now() + timedelta(weeks=duration_weeks)).strftime('%Y-%m-%d'),
            focus_area=focus_area,
            current_level=current_level,
            goal_level=goal_level
        )

        # Generate initial strategies based on focus area and levels
        cycle.strategies = self._generate_coaching_strategies(focus_area, current_level, goal_level)
        cycle.action_steps = self._generate_action_steps(focus_area, goal_level)

        self._save_coaching_cycle(cycle)
        return cycle

    def _generate_coaching_strategies(self, focus_area: str, current_level: str, goal_level: str) -> List[str]:
        """Generate evidence-based coaching strategies."""
        strategies = []

        # Practice Based Coaching strategies based on focus area
        if focus_area.lower() == "classroom management":
            strategies.extend([
                "Model effective classroom routines and transitions",
                "Use video self-reflection to identify management patterns",
                "Implement specific behavior management techniques",
                "Practice positive behavior supports"
            ])
        elif focus_area.lower() == "instructional strategies":
            strategies.extend([
                "Demonstrate differentiated instruction techniques",
                "Use questioning strategies to promote higher-order thinking",
                "Implement inquiry-based learning approaches",
                "Model effective lesson planning and implementation"
            ])
        elif focus_area.lower() == "child assessment":
            strategies.extend([
                "Train in authentic assessment methods",
                "Practice observation and documentation techniques",
                "Develop individualized learning plans",
                "Use assessment data to inform instruction"
            ])
        else:
            strategies.extend([
                "Joint planning of learning experiences",
                "Modeling of effective practices",
                "Practice with feedback and reflection",
                "Resource identification and utilization"
            ])

        return strategies

    def _generate_action_steps(self, focus_area: str, goal_level: str) -> List[str]:
        """Generate specific action steps for the teacher."""
        action_steps = []

        # Generate specific, measurable action steps
        if "classroom management" in focus_area.lower():
            action_steps.extend([
                "Establish consistent daily routines and transitions",
                "Create and implement a classroom behavior plan",
                "Set up learning centers that promote independence",
                "Develop clear classroom expectations with children"
            ])
        elif "instruction" in focus_area.lower():
            action_steps.extend([
                "Plan lessons with clear learning objectives",
                "Incorporate multiple learning modalities",
                "Use assessment data to differentiate instruction",
                "Implement inquiry-based learning activities"
            ])
        elif "assessment" in focus_area.lower():
            action_steps.extend([
                "Conduct daily observations of child learning",
                "Document children's progress in specific skill areas",
                "Use assessment data to plan individualized activities",
                "Share assessment results with families"
            ])
        else:
            action_steps.extend([
                f"Identify specific practices to achieve {goal_level} level",
                "Set up opportunities to practice target skills",
                "Collect evidence of implementation",
                "Reflect on progress and adjust approach"
            ])

        return action_steps

    def log_coaching_session(self, cycle_id: str, session_type: str, duration_minutes: int,
                            location: str, agenda_items: List[str], discussion_topics: List[str],
                            teacher_reflections: List[str], coach_feedback: List[str],
                            action_items: List[str]) -> CoachingSession:
        """Log a coaching session with detailed information."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = CoachingSession(
            id=session_id,
            coaching_cycle_id=cycle_id,
            session_date=datetime.now().strftime('%Y-%m-%d'),
            session_type=session_type,
            duration_minutes=duration_minutes,
            location=location,
            agenda_items=agenda_items,
            discussion_topics=discussion_topics,
            teacher_reflections=teacher_reflections,
            coach_feedback=coach_feedback,
            action_items=action_items
        )

        # Update coaching cycle with session data
        cycle = self._load_coaching_cycle(cycle_id)
        if cycle:
            if session_type == "feedback":
                cycle.evidence_of_progress.extend(teacher_reflections)
                cycle.supports_provided.extend(coach_feedback)
            elif session_type == "planning":
                cycle.action_steps.extend(action_items)

            self._save_coaching_cycle(cycle)

        self._save_coaching_session(session)
        return session

    def update_coaching_cycle_progress(self, cycle_id: str, progress_notes: str,
                                      challenges: List[str], new_action_items: List[str]) -> None:
        """Update coaching cycle with progress information."""
        cycle = self._load_coaching_cycle(cycle_id)
        if cycle:
            cycle.evidence_of_progress.append(f"{datetime.now().isoformat()}: {progress_notes}")
            cycle.challenges.extend(challenges)
            cycle.action_steps.extend(new_action_items)
            self._save_coaching_cycle(cycle)

    def complete_coaching_cycle(self, cycle_id: str, outcome_notes: str,
                               achieved_level: str) -> None:
        """Mark a coaching cycle as completed."""
        cycle = self._load_coaching_cycle(cycle_id)
        if cycle:
            cycle.status = "completed"
            cycle.completion_date = datetime.now().strftime('%Y-%m-%d')
            cycle.outcome_notes = outcome_notes

            # Update goal level if achieved
            if achieved_level:
                cycle.goal_level = achieved_level

            self._save_coaching_cycle(cycle)

    def generate_coaching_report(self, cycle_id: str) -> Dict[str, Any]:
        """Generate comprehensive coaching cycle report."""
        cycle = self._load_coaching_cycle(cycle_id)
        if not cycle:
            return {"error": "Coaching cycle not found"}

        # Get related sessions
        sessions = self._get_cycle_sessions(cycle_id)

        # Calculate progress metrics
        progress_metrics = self._calculate_progress_metrics(cycle, sessions)

        report = {
            "cycle_id": cycle.id,
            "teacher_id": cycle.teacher_id,
            "coach_id": cycle.coach_id,
            "focus_area": cycle.focus_area,
            "start_date": cycle.start_date,
            "target_completion": cycle.target_completion_date,
            "actual_completion": cycle.completion_date,
            "current_level": cycle.current_level,
            "goal_level": cycle.goal_level,
            "status": cycle.status,
            "strategies_used": cycle.strategies,
            "action_steps": cycle.action_steps,
            "progress_metrics": progress_metrics,
            "challenges_encountered": cycle.challenges,
            "supports_provided": cycle.supports_provided,
            "evidence_of_progress": cycle.evidence_of_progress,
            "session_summary": {
                "total_sessions": len(sessions),
                "session_types": self._count_session_types(sessions),
                "total_time": sum(s.duration_minutes for s in sessions)
            },
            "outcome_notes": cycle.outcome_notes,
            "generated_at": datetime.now().isoformat()
        }

        return report

    def _calculate_progress_metrics(self, cycle: CoachingCycle, sessions: List[CoachingSession]) -> Dict[str, Any]:
        """Calculate progress metrics for the coaching cycle."""
        metrics = {
            "action_steps_completed": 0,
            "strategies_implemented": 0,
            "challenges_addressed": len(cycle.challenges),
            "evidence_collected": len(cycle.evidence_of_progress),
            "sessions_completed": len(sessions)
        }

        # Simple progress calculation based on evidence and sessions
        total_indicators = 3  # action steps, strategies, evidence
        completed_indicators = 0

        if len(cycle.action_steps) > 0:
            completed_indicators += 1
        if len(cycle.strategies) > 0:
            completed_indicators += 1
        if len(cycle.evidence_of_progress) > 0:
            completed_indicators += 1

        metrics["overall_progress_percentage"] = (completed_indicators / total_indicators) * 100

        return metrics

    def _count_session_types(self, sessions: List[CoachingSession]) -> Dict[str, int]:
        """Count different types of coaching sessions."""
        types = {}
        for session in sessions:
            session_type = session.session_type
            types[session_type] = types.get(session_type, 0) + 1
        return types

    def get_teacher_coaching_history(self, teacher_id: str) -> List[CoachingCycle]:
        """Get all coaching cycles for a specific teacher."""
        cycles = []
        for cycle_file in self.data_dir.glob("cycle_*.json"):
            try:
                cycle_data = read_json(str(cycle_file))
                if cycle_data.get("teacher_id") == teacher_id:
                    cycles.append(CoachingCycle(**cycle_data))
            except Exception:
                continue

        return sorted(cycles, key=lambda x: x.start_date, reverse=True)

    def _get_cycle_sessions(self, cycle_id: str) -> List[CoachingSession]:
        """Get all sessions for a coaching cycle."""
        sessions = []
        for session_file in self.data_dir.glob("session_*.json"):
            try:
                session_data = read_json(str(session_file))
                if session_data.get("coaching_cycle_id") == cycle_id:
                    sessions.append(CoachingSession(**session_data))
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x.session_date)

    def _save_coaching_cycle(self, cycle: CoachingCycle) -> None:
        """Save coaching cycle to file."""
        filename = f"cycle_{cycle.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": cycle.id,
            "teacher_id": cycle.teacher_id,
            "coach_id": cycle.coach_id,
            "start_date": cycle.start_date,
            "target_completion_date": cycle.target_completion_date,
            "focus_area": cycle.focus_area,
            "current_level": cycle.current_level,
            "goal_level": cycle.goal_level,
            "strategies": cycle.strategies,
            "action_steps": cycle.action_steps,
            "resources_needed": cycle.resources_needed,
            "evidence_of_progress": cycle.evidence_of_progress,
            "challenges": cycle.challenges,
            "supports_provided": cycle.supports_provided,
            "status": cycle.status,
            "completion_date": cycle.completion_date,
            "outcome_notes": cycle.outcome_notes
        }

        write_json(str(filepath), data)

    def _load_coaching_cycle(self, cycle_id: str) -> Optional[CoachingCycle]:
        """Load coaching cycle from file."""
        filename = f"cycle_{cycle_id}.json"
        filepath = self.data_dir / filename

        if filepath.exists():
            try:
                data = read_json(str(filepath))
                return CoachingCycle(**data)
            except Exception:
                pass

        return None

    def _save_coaching_session(self, session: CoachingSession) -> None:
        """Save coaching session to file."""
        filename = f"session_{session.id}.json"
        filepath = self.data_dir / filename

        data = {
            "id": session.id,
            "coaching_cycle_id": session.coaching_cycle_id,
            "session_date": session.session_date,
            "session_type": session.session_type,
            "duration_minutes": session.duration_minutes,
            "location": session.location,
            "agenda_items": session.agenda_items,
            "discussion_topics": session.discussion_topics,
            "teacher_reflections": session.teacher_reflections,
            "coach_feedback": session.coach_feedback,
            "action_items": session.action_items,
            "next_session_date": session.next_session_date,
            "session_notes": session.session_notes,
            "teacher_goals_addressed": session.teacher_goals_addressed
        }

        write_json(str(filepath), data)
