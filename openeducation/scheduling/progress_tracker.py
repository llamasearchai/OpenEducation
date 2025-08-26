from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..utils.io import write_json, read_json


@dataclass
class AnkiPerformance:
    """Detailed performance metrics for a single Anki card review."""
    card_id: str
    deck_name: str
    lapses: int
    ease_factor: float
    review_date: str
    review_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class StudySession:
    """A single study session with objectives and progress."""
    id: str
    syllabus_id: str
    unit_id: str
    objective_id: str
    scheduled_date: str
    duration_planned: int  # minutes
    actual_date: Optional[str] = None
    duration_actual: Optional[int] = None
    completed: bool = False
    notes: str = ""
    resources_used: List[str] = field(default_factory=list)
    difficulty_rating: Optional[int] = None  # 1-5 scale
    understanding_level: Optional[int] = None  # 1-5 scale
    anki_performance: List[AnkiPerformance] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """A comprehensive analysis of learner performance."""
    student_id: str
    syllabus_id: str
    report_date: str
    overall_completion_rate: float
    weak_topics: Dict[str, float]  # Topic ID to performance score (0-1)
    strong_topics: Dict[str, float]
    detailed_feedback: List[str]


@dataclass
class LearningProgress:
    """Overall learning progress tracking."""
    syllabus_id: str
    student_id: str
    start_date: str
    last_updated: str
    total_sessions: int = 0
    completed_sessions: int = 0
    total_study_time: int = 0  # minutes
    average_difficulty: Optional[float] = None
    average_understanding: Optional[float] = None
    sessions: List[StudySession] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)


class ProgressTracker:
    """Track learning progress and study sessions."""

    def __init__(self, data_dir: str = "data/progress"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def import_anki_reviews(self, syllabus_id: str, student_id: str, anki_reviews: List[AnkiPerformance]) -> None:
        """Import Anki review data and associate with study sessions."""
        progress = self._load_progress(syllabus_id, student_id)
        # Simple association: associate with the most recent session for the deck
        for review in anki_reviews:
            for session in reversed(progress.sessions):
                # This logic can be improved with more context
                if review.deck_name in session.notes or syllabus_id in review.deck_name:
                    session.anki_performance.append(review)
                    break
        progress.last_updated = datetime.now().isoformat()
        self._save_progress(progress)

    def start_tracking(self, syllabus_id: str, student_id: str) -> LearningProgress:
        """Start tracking progress for a syllabus."""
        progress = LearningProgress(
            syllabus_id=syllabus_id,
            student_id=student_id,
            start_date=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )

        self._save_progress(progress)
        return progress

    def log_session(self, session: StudySession) -> None:
        """Log a completed study session."""
        # Load current progress
        progress = self._load_progress(session.syllabus_id, session.id.split('_')[0])

        # Add session
        progress.sessions.append(session)
        progress.total_sessions += 1
        progress.last_updated = datetime.now().isoformat()

        if session.completed:
            progress.completed_sessions += 1

        if session.duration_actual:
            progress.total_study_time += session.duration_actual

        # Update averages
        self._update_averages(progress)

        self._save_progress(progress)

    def generate_performance_report(self, syllabus_id: str, student_id: str) -> PerformanceReport:
        """Generate a comprehensive performance report for adaptive learning."""
        try:
            progress = self._load_progress(syllabus_id, student_id)
        except FileNotFoundError:
            return PerformanceReport(
                student_id=student_id,
                syllabus_id=syllabus_id,
                report_date=datetime.now().isoformat(),
                overall_completion_rate=0.0,
                weak_topics={},
                strong_topics={},
                detailed_feedback=["No progress data found."]
            )

        # Calculate completion rate
        completion_rate = (progress.completed_sessions / progress.total_sessions * 100) if progress.total_sessions > 0 else 0

        # Analyze Anki performance to find weak/strong topics
        topic_performance = {}
        for session in progress.sessions:
            if not session.anki_performance:
                continue

            topic_id = session.objective_id  # Assuming objective_id maps to a topic
            if topic_id not in topic_performance:
                topic_performance[topic_id] = []

            for card in session.anki_performance:
                # Simple metric: high lapses = poor performance.
                # Score: 1.0 = perfect, lower is worse.
                score = 1.0 / (1 + card.lapses)
                topic_performance[topic_id].append(score)

        avg_topic_scores = {topic: sum(scores) / len(scores) for topic, scores in topic_performance.items()}
        weak_topics = {topic: score for topic, score in avg_topic_scores.items() if score < 0.6}
        strong_topics = {topic: score for topic, score in avg_topic_scores.items() if score >= 0.8}

        feedback = self._generate_feedback(weak_topics, strong_topics)

        return PerformanceReport(
            student_id=student_id,
            syllabus_id=syllabus_id,
            report_date=datetime.now().isoformat(),
            overall_completion_rate=round(completion_rate, 2),
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            detailed_feedback=feedback
        )

    def get_progress_report(self, syllabus_id: str, student_id: str) -> Dict[str, Any]:
        """Generate a comprehensive progress report."""
        try:
            progress = self._load_progress(syllabus_id, student_id)
        except FileNotFoundError:
            return {"error": "No progress data found"}

        # Calculate completion rates
        completion_rate = (progress.completed_sessions / progress.total_sessions * 100) if progress.total_sessions > 0 else 0

        # Group sessions by unit
        unit_progress = {}
        for session in progress.sessions:
            if session.unit_id not in unit_progress:
                unit_progress[session.unit_id] = {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "total_time": 0,
                    "objectives": set()
                }

            unit_progress[session.unit_id]["total_sessions"] += 1
            unit_progress[session.unit_id]["objectives"].add(session.objective_id)

            if session.completed:
                unit_progress[session.unit_id]["completed_sessions"] += 1

            if session.duration_actual:
                unit_progress[session.unit_id]["total_time"] += session.duration_actual

        # Calculate study streaks
        streak = self._calculate_study_streak(progress.sessions)

        return {
            "syllabus_id": syllabus_id,
            "student_id": student_id,
            "overall_progress": {
                "completion_rate": round(completion_rate, 1),
                "total_sessions": progress.total_sessions,
                "completed_sessions": progress.completed_sessions,
                "total_study_time": progress.total_study_time,
                "average_session_time": round(progress.total_study_time / progress.total_sessions, 1) if progress.total_sessions > 0 else 0,
                "current_streak": streak
            },
            "performance_metrics": {
                "average_difficulty": round(progress.average_difficulty or 0, 1),
                "average_understanding": round(progress.average_understanding or 0, 1)
            },
            "unit_breakdown": {
                unit_id: {
                    "completion_rate": round((stats["completed_sessions"] / stats["total_sessions"] * 100), 1),
                    "total_time": stats["total_time"],
                    "objectives_covered": len(stats["objectives"])
                }
                for unit_id, stats in unit_progress.items()
            },
            "achievements": progress.achievements,
            "challenges": progress.challenges,
            "last_updated": progress.last_updated
        }

    def generate_study_schedule(self, syllabus_schedule: Dict[str, Any], student_id: str) -> List[StudySession]:
        """Generate personalized study sessions from syllabus schedule."""
        sessions = []

        for unit in syllabus_schedule["schedule"]:
            for objective in unit["objectives"]:
                session = StudySession(
                    id=f"{student_id}_{objective['objective_id']}_{objective['start_date']}",
                    syllabus_id=syllabus_schedule["syllabus_id"],
                    unit_id=unit["unit_id"],
                    objective_id=objective["objective_id"],
                    scheduled_date=objective["start_date"],
                    duration_planned=objective["estimated_time"]
                )
                sessions.append(session)

        return sessions

    def update_achievement(self, syllabus_id: str, student_id: str, achievement: str) -> None:
        """Add an achievement to the student's progress."""
        progress = self._load_progress(syllabus_id, student_id)
        if achievement not in progress.achievements:
            progress.achievements.append(achievement)
            progress.last_updated = datetime.now().isoformat()
            self._save_progress(progress)

    def log_challenge(self, syllabus_id: str, student_id: str, challenge: str) -> None:
        """Log a challenge or difficulty encountered."""
        progress = self._load_progress(syllabus_id, student_id)
        progress.challenges.append(
            {
                "date": datetime.now().isoformat(),
                "description": challenge
            }
        )
        progress.last_updated = datetime.now().isoformat()
        self._save_progress(progress)

    def _update_averages(self, progress: LearningProgress) -> None:
        """Update average performance metrics."""
        difficulty_ratings = [s.difficulty_rating for s in progress.sessions if s.difficulty_rating]
        understanding_ratings = [s.understanding_level for s in progress.sessions if s.understanding_level]

        if difficulty_ratings:
            progress.average_difficulty = sum(difficulty_ratings) / len(difficulty_ratings)
        if understanding_ratings:
            progress.average_understanding = sum(understanding_ratings) / len(understanding_ratings)

    def _generate_feedback(self, weak_topics: Dict[str, float], strong_topics: Dict[str, float]) -> List[str]:
        """Generate textual feedback based on performance."""
        feedback = []
        if weak_topics:
            feedback.append(f"Focus on improving these topics: {', '.join(weak_topics.keys())}.")
        if strong_topics:
            feedback.append(f"You're doing great in these areas: {', '.join(strong_topics.keys())}.")
        if not weak_topics and not strong_topics:
            feedback.append("Consistent effort is showing! Keep up the great work across all topics.")
        return feedback

    def _calculate_study_streak(self, sessions: List[StudySession]) -> int:
        """Calculate current study streak in days."""
        if not sessions:
            return 0

        # Get completed sessions sorted by date
        completed_sessions = [s for s in sessions if s.completed and s.actual_date]
        if not completed_sessions:
            return 0

        completed_sessions.sort(key=lambda s: s.actual_date, reverse=True)

        streak = 0
        current_date = datetime.now().date()

        for session in completed_sessions:
            session_date = datetime.fromisoformat(session.actual_date).date()

            # If this session is from today or yesterday (allowing for one day gap)
            if (current_date - session_date).days <= 1:
                streak += 1
                current_date = session_date - timedelta(days=1)
            else:
                break

        return streak

    def _load_progress(self, syllabus_id: str, student_id: str) -> LearningProgress:
        """Load progress data from file."""
        progress_file = self.data_dir / f"{syllabus_id}_{student_id}_progress.json"
        if progress_file.exists():
            data = read_json(str(progress_file))
            return LearningProgress(**data)
        else:
            raise FileNotFoundError(f"Progress file not found: {progress_file}")

    def _save_progress(self, progress: LearningProgress) -> None:
        """Save progress data to file."""
        progress_file = self.data_dir / f"{progress.syllabus_id}_{progress.student_id}_progress.json"

        # Convert to dict for JSON serialization
        data = {
            "syllabus_id": progress.syllabus_id,
            "student_id": progress.student_id,
            "start_date": progress.start_date,
            "last_updated": progress.last_updated,
            "total_sessions": progress.total_sessions,
            "completed_sessions": progress.completed_sessions,
            "total_study_time": progress.total_study_time,
            "average_difficulty": progress.average_difficulty,
            "average_understanding": progress.average_understanding,
            "sessions": [
                {
                    "id": s.id,
                    "syllabus_id": s.syllabus_id,
                    "unit_id": s.unit_id,
                    "objective_id": s.objective_id,
                    "scheduled_date": s.scheduled_date,
                    "actual_date": s.actual_date,
                    "duration_planned": s.duration_planned,
                    "duration_actual": s.duration_actual,
                    "completed": s.completed,
                    "notes": s.notes,
                    "resources_used": s.resources_used,
                    "difficulty_rating": s.difficulty_rating,
                    "understanding_level": s.understanding_level,
                    "anki_performance": [
                        {
                            "card_id": p.card_id,
                            "deck_name": p.deck_name,
                            "lapses": p.lapses,
                            "ease_factor": p.ease_factor,
                            "review_date": p.review_date,
                            "review_history": p.review_history,
                        } for p in s.anki_performance
                    ]
                }
                for s in progress.sessions
            ],
            "achievements": progress.achievements,
            "challenges": progress.challenges,
        }

        write_json(str(progress_file), data)
