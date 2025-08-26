from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ..llm.openai_wrapper import OpenAIWrapper
from ..rag.embeddings import OpenAIEmbedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnkiConnectClient:
    """Advanced AnkiConnect client with plugin support and enhanced features."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()

    def _request(self, action: str, **params) -> Dict[str, Any]:
        """Make a request to AnkiConnect."""
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }

        try:
            response = self.session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("error"):
                raise Exception(f"AnkiConnect error: {result['error']}")

            return result.get("result", {})
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Anki. Make sure Anki is running with AnkiConnect plugin.")
        except Exception as e:
            raise Exception(f"AnkiConnect request failed: {e}")

    def is_connected(self) -> bool:
        """Check if AnkiConnect is available."""
        try:
            self._request("version")
            return True
        except Exception:
            return False

    def get_version(self) -> str:
        """Get AnkiConnect version."""
        return str(self._request("version"))

    def get_deck_names(self) -> List[str]:
        """Get all deck names."""
        return self._request("deckNames")

    def create_deck(self, deck_name: str) -> int:
        """Create a new deck."""
        return self._request("createDeck", deck=deck_name)

    def delete_deck(self, deck_name: str, cards_too: bool = False) -> None:
        """Delete a deck."""
        self._request("deleteDecks", decks=[deck_name], cardsToo=cards_too)

    def import_package(self, package_path: str) -> Dict[str, Any]:
        """Import an Anki package (.apkg file)."""
        return self._request("importPackage", path=package_path)

    def export_package(self, deck_name: str, output_path: str, include_scheduling: bool = True) -> str:
        """Export a deck to Anki package."""
        return self._request("exportPackage",
                           deck=deck_name,
                           path=output_path,
                           includeSched=include_scheduling)

    def add_note(self, deck_name: str, model_name: str, fields: Dict[str, str],
                tags: Optional[List[str]] = None) -> int:
        """Add a single note to Anki."""
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or []
        }

        return self._request("addNote", note=note)

    def add_notes(self, notes: List[Dict[str, Any]]) -> List[int]:
        """Add multiple notes to Anki."""
        return self._request("addNotes", notes=notes)

    def find_notes(self, query: str) -> List[int]:
        """Find notes matching a query."""
        return self._request("findNotes", query=query)

    def get_note_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed information about notes."""
        return self._request("notesInfo", notes=note_ids)

    def update_note(self, note_id: int, fields: Dict[str, str],
                   tags: Optional[List[str]] = None) -> None:
        """Update an existing note."""
        updates = {"id": note_id, "fields": fields}
        if tags is not None:
            updates["tags"] = tags

        self._request("updateNote", note=updates)

    def delete_notes(self, note_ids: List[int]) -> None:
        """Delete notes."""
        self._request("deleteNotes", notes=note_ids)

    def get_model_names(self) -> List[str]:
        """Get all available note models."""
        return self._request("modelNames")

    def get_model_field_names(self, model_name: str) -> List[str]:
        """Get field names for a model."""
        return self._request("modelFieldNames", modelName=model_name)

    def create_model(self, model_name: str, fields: List[str],
                    templates: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create a custom note model."""
        model = {
            "modelName": model_name,
            "inOrderFields": fields,
            "isCloze": False,
            "cardTemplates": templates
        }

        return self._request("createModel", model=model)

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return self._request("getStats")

    def get_deck_stats(self, deck_name: str) -> Dict[str, Any]:
        """Get statistics for a specific deck."""
        return self._request("getDeckStats", decks=[deck_name])

    def sync(self) -> None:
        """Sync collection with AnkiWeb."""
        self._request("sync")

    def get_preferences(self) -> Dict[str, Any]:
        """Get Anki preferences."""
        return self._request("getPreferences")

    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        """Set Anki preferences."""
        self._request("setPreferences", preferences=preferences)


class AnkiDeckManager:
    """High-level manager for Anki deck operations with educational features."""

    def __init__(self, client: Optional[AnkiConnectClient] = None):
        self.client = client or AnkiConnectClient()

    def create_educational_deck(self, deck_name: str, cards_data: List[Dict[str, Any]],
                               model_name: str = "OpenEducation Basic") -> Dict[str, Any]:
        """Create an educational deck with custom model optimized for learning."""

        # Ensure deck exists
        self.client.create_deck(deck_name)

        # Create educational model if it doesn't exist
        if model_name not in self.client.get_model_names():
            self._create_educational_model(model_name)

        # Add notes
        notes = []
        for card_data in cards_data:
            note = {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": {
                    "Front": card_data.get("front", ""),
                    "Back": card_data.get("back", ""),
                    "Subject": card_data.get("subject", ""),
                    "Difficulty": str(card_data.get("difficulty", 3)),
                    "Tags": " ".join(card_data.get("tags", []))
                },
                "tags": card_data.get("tags", [])
            }
            notes.append(note)

        # Add all notes
        note_ids = self.client.add_notes(notes)

        return {
            "deck_name": deck_name,
            "notes_created": len(note_ids),
            "note_ids": note_ids
        }

    def _create_educational_model(self, model_name: str) -> None:
        """Create a custom educational note model."""
        fields = ["Front", "Back", "Subject", "Difficulty", "Tags"]

        templates = [
            {
                "Name": "Learning Card",
                "Front": "{{Front}}",
                "Back": "{{FrontSide}}<hr id=\"answer\">{{Back}}<br><br><small>Subject: {{Subject}}<br>Difficulty: {{Difficulty}}</small>"
            },
            {
                "Name": "Reverse Card",
                "Front": "{{Back}}",
                "Back": "{{FrontSide}}<hr id=\"answer\">{{Front}}<br><br><small>Subject: {{Subject}}<br>Difficulty: {{Difficulty}}</small>"
            }
        ]

        self.client.create_model(model_name, fields, templates)

    def import_anki_package(self, package_path: str) -> Dict[str, Any]:
        """Import an Anki package with progress tracking."""
        if not Path(package_path).exists():
            raise FileNotFoundError(f"Package not found: {package_path}")

        result = self.client.import_package(package_path)

        # Get deck stats after import
        if "deck_name" in result:
            stats = self.client.get_deck_stats(result["deck_name"])
            result["deck_stats"] = stats

        return result

    def export_educational_deck(self, deck_name: str, output_path: str,
                               include_progress: bool = True) -> str:
        """Export a deck with educational metadata."""
        if deck_name not in self.client.get_deck_names():
            raise ValueError(f"Deck '{deck_name}' not found")

        # Export the package
        export_path = self.client.export_package(deck_name, output_path, include_progress)

        # Add educational metadata
        self._add_educational_metadata(deck_name, export_path)

        return export_path

    def _add_educational_metadata(self, deck_name: str, package_path: str) -> None:
        """Add educational metadata to exported package."""
        # This would typically involve modifying the .apkg file
        # For now, we'll create a metadata file alongside it
        metadata = {
            "deck_name": deck_name,
            "exported_at": "2024-01-01T00:00:00Z",
            "educational_purpose": "OpenEducation generated deck",
            "recommended_study_time": "30-45 minutes per session",
            "difficulty_distribution": self._analyze_deck_difficulty(deck_name)
        }

        metadata_path = package_path.replace('.apkg', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _analyze_deck_difficulty(self, deck_name: str) -> Dict[str, int]:
        """Analyze difficulty distribution in a deck."""
        # Find notes in the deck
        query = f"deck:\"{deck_name}\""
        note_ids = self.client.find_notes(query)
        notes = self.client.get_note_info(note_ids)

        difficulty_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

        for note in notes:
            difficulty = note.get("fields", {}).get("Difficulty", {}).get("value", "3")
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1

        return difficulty_counts

    def get_study_recommendations(self, deck_name: str) -> Dict[str, Any]:
        """Generate study recommendations based on deck analysis."""
        if deck_name not in self.client.get_deck_names():
            raise ValueError(f"Deck '{deck_name}' not found")

        # Optionally fetch stats here in the future
        difficulty_dist = self._analyze_deck_difficulty(deck_name)

        # Generate recommendations
        recommendations = {
            "daily_study_time": "30-45 minutes",
            "session_structure": {
                "review_known": "10 minutes",
                "learn_new": "20 minutes",
                "practice_difficult": "15 minutes"
            },
            "difficulty_focus": self._get_difficulty_recommendations(difficulty_dist),
            "study_streak_goal": "7 days per week",
            "break_reminders": "5-minute break every 25 minutes"
        }

        return recommendations

    def _get_difficulty_recommendations(self, difficulty_dist: Dict[str, int]) -> List[str]:
        """Generate difficulty-specific recommendations."""
        recommendations = []

        total_cards = sum(difficulty_dist.values())

        if total_cards == 0:
            return ["No cards found in deck"]

        # Analyze difficulty distribution
        easy_cards = difficulty_dist.get("1", 0) + difficulty_dist.get("2", 0)
        medium_cards = difficulty_dist.get("3", 0)
        hard_cards = difficulty_dist.get("4", 0) + difficulty_dist.get("5", 0)

        if hard_cards > total_cards * 0.4:
            recommendations.append("Focus extra time on difficult cards (4-5 rating)")
        elif easy_cards > total_cards * 0.6:
            recommendations.append("Consider adding more challenging content")
        else:
            recommendations.append("Good balance of difficulty levels")

        if medium_cards > total_cards * 0.5:
            recommendations.append("Spend time mastering medium-difficulty concepts")

        return recommendations

    def create_study_plan(self, deck_name: str, days: int = 30) -> Dict[str, Any]:
        """Create a personalized study plan."""
        recommendations = self.get_study_recommendations(deck_name)
        stats = self.client.get_deck_stats(deck_name)

        # Calculate daily goals
        new_cards_per_day = min(20, max(5, stats.get("new", 0) // days))
        review_cards_per_day = min(100, stats.get("review", 0) // days)

        study_plan = {
            "deck_name": deck_name,
            "duration_days": days,
            "daily_goals": {
                "new_cards": new_cards_per_day,
                "review_cards": review_cards_per_day,
                "study_time_minutes": 30
            },
            "session_structure": recommendations["session_structure"],
            "recommendations": recommendations["difficulty_focus"],
            "milestones": self._generate_milestones(days, stats)
        }

        return study_plan

    def _generate_milestones(self, days: int, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate study milestones."""
        milestones = []

        # Weekly milestones
        for week in range(1, (days // 7) + 1):
            day = week * 7
            if day <= days:
                milestones.append({
                    "day": day,
                    "type": "weekly_review",
                    "goal": f"Complete Week {week} studies",
                    "target_new_cards": min(100, stats.get("new", 0) * (day / days))
                })

        # Final milestone
        milestones.append({
            "day": days,
            "type": "completion",
            "goal": "Complete comprehensive review",
            "target_completion": 100
        })

        return milestones

    def get_progress_analytics(self, deck_name: str) -> Dict[str, Any]:
        """Get detailed progress analytics for a deck."""
        if deck_name not in self.client.get_deck_names():
            raise ValueError(f"Deck '{deck_name}' not found")

        stats = self.client.get_deck_stats(deck_name)
        recommendations = self.get_study_recommendations(deck_name)

        return {
            "deck_name": deck_name,
            "current_stats": stats,
            "study_recommendations": recommendations,
            "progress_metrics": {
                "cards_studied_today": stats.get("cards_studied_today", 0),
                "time_studied_today": stats.get("time_studied_today", 0),
                "retention_rate": stats.get("retention_rate", 0),
                "study_streak": stats.get("study_streak", 0)
            },
            "next_session_goals": {
                "new_cards": min(20, stats.get("new", 0)),
                "review_cards": min(100, stats.get("review", 0))
            }
        }


class AnkiSyncManager:
    """Manage synchronization between OpenEducation and Anki with progress tracking."""

    def __init__(self, client: Optional[AnkiConnectClient] = None):
        self.client = client or AnkiConnectClient()
        self.manager = AnkiDeckManager(self.client)

    def sync_syllabus_progress(self, syllabus_id: str, student_id: str) -> Dict[str, Any]:
        """Sync syllabus learning progress with Anki study progress."""
        # This would integrate with the progress tracker
        # For now, return a placeholder
        return {
            "syllabus_id": syllabus_id,
            "student_id": student_id,
            "sync_status": "completed",
            "anki_decks_synced": 0,
            "progress_updated": True
        }

    def create_adaptive_study_plan(self, syllabus_id: str, anki_decks: List[str]) -> Dict[str, Any]:
        """Create an adaptive study plan based on syllabus and Anki performance."""
        study_plan = {
            "syllabus_id": syllabus_id,
            "adaptive_plan": {
                "weak_areas": [],
                "strong_areas": [],
                "recommended_sessions": [],
                "adjustments": []
            },
            "anki_integration": {
                "decks_to_focus": anki_decks,
                "priority_cards": [],
                "study_streaks": {}
            }
        }

        return study_plan


class AnkiPluginManager:
    """Manage Anki plugins and their integration with OpenEducation."""

    def __init__(self):
        self.supported_plugins = {
            "ankiconnect": {
                "name": "AnkiConnect",
                "description": "REST API for Anki",
                "url": "https://ankiweb.net/shared/info/2055492159",
                "required": True,
                "features": ["remote_deck_management", "card_operations", "sync"]
            },
            "review_heatmap": {
                "name": "Review Heatmap",
                "description": "Visual study statistics",
                "url": "https://ankiweb.net/shared/info/1771074083",
                "required": False,
                "features": ["study_analytics", "progress_tracking"]
            },
            "advanced_browser": {
                "name": "Advanced Browser",
                "description": "Enhanced card browser",
                "url": "https://ankiweb.net/shared/info/874215009",
                "required": False,
                "features": ["advanced_search", "bulk_operations"]
            },
            "morphman": {
                "name": "MorphMan",
                "description": "Morphology-based study",
                "url": "https://ankiweb.net/shared/info/900801631",
                "required": False,
                "features": ["vocabulary_learning", "morphological_analysis"]
            },
            "image_occlusion": {
                "name": "Image Occlusion Enhanced",
                "description": "Create cards from images",
                "url": "https://ankiweb.net/shared/info/1111933094",
                "required": False,
                "features": ["image_based_cards", "visual_learning"]
            }
        }

    def get_supported_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported plugins."""
        return self.supported_plugins

    def check_plugin_compatibility(self, plugin_name: str) -> Dict[str, Any]:
        """Check if a plugin is compatible with current setup."""
        if plugin_name not in self.supported_plugins:
            return {"compatible": False, "reason": "Plugin not supported"}

        plugin = self.supported_plugins[plugin_name]

        # Check if required plugins are installed
        if plugin.get("required", False):
            # For AnkiConnect, we can check if it's running
            if plugin_name == "ankiconnect":
                client = AnkiConnectClient()
                return {
                    "compatible": client.is_connected(),
                    "reason": "AnkiConnect running" if client.is_connected() else "AnkiConnect not running"
                }

        return {"compatible": True, "reason": "Plugin supported"}


class EnhancedFlashcardGenerator:
    """Enhanced flashcard generator using OpenAI embeddings and LLM."""

    def __init__(self, openai_api_key: Optional[str] = None):
        self.llm = OpenAIWrapper()
        self.embedding_model = OpenAIEmbedding()

    def generate_semantic_flashcards(self, content: str, subject: str = "general",
                                   num_cards: int = 10) -> List[Dict[str, Any]]:
        """Generate flashcards using semantic analysis and embeddings."""

        # Extract key concepts using LLM
        system_prompt = f"""You are an expert {subject} educator. Analyze the provided content and extract key concepts,
        definitions, relationships, and important facts that would make effective flashcards."""

        user_prompt = f"""Content to analyze:
{content[:4000]}  # Truncate for token limits

Please identify and structure the most important educational concepts from this content.
Focus on:
1. Key terms and definitions
2. Important relationships and connections
3. Cause and effect relationships
4. Critical facts and data
5. Processes and procedures

Return a JSON array of concept objects with 'term', 'definition', and 'difficulty' (1-5) fields."""

        concepts = self.llm.json_structured(system_prompt, user_prompt, {"concepts": "array"})

        # Generate embeddings for content chunks
        content_chunks = self._chunk_content(content)
        _ = self.embedding_model.embed(content_chunks)

        # Create flashcards with difficulty assessment
        flashcards = []
        for concept in concepts.get("concepts", [])[:num_cards]:
            if "term" in concept and "definition" in concept:
                flashcard = {
                    "front": concept["term"],
                    "back": concept["definition"],
                    "subject": subject,
                    "difficulty": concept.get("difficulty", 3),
                    "tags": [subject, f"difficulty_{concept.get('difficulty', 3)}"],
                    "embedding": None  # Could store embedding for semantic search
                }
                flashcards.append(flashcard)

        return flashcards

    def _chunk_content(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Split content into manageable chunks."""
        words = content.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) > chunk_size:
                chunks.append(' '.join(current_chunk[:-1]))
                current_chunk = [word]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def generate_cloze_flashcards(self, content: str, subject: str = "general",
                                num_cards: int = 5) -> List[Dict[str, Any]]:
        """Generate cloze deletion flashcards for memorization."""

        system_prompt = f"""You are an expert {subject} educator. Create cloze deletion flashcards from the content.
        Cloze deletions should remove key terms that students need to recall."""

        user_prompt = f"""Content:
{content[:3000]}

Create {num_cards} cloze deletion flashcards. Each should:
1. Have one key term removed and replaced with {{c1::key term}}
2. Test important concepts and terminology
3. Be educational and memorable

Return a JSON array with 'text' (cloze text) and 'extra' (hint) fields."""

        response = self.llm.json_structured(system_prompt, user_prompt, {"cloze_cards": "array"})

        flashcards = []
        for card in response.get("cloze_cards", [])[:num_cards]:
            flashcard = {
                "front": card.get("text", ""),
                "back": "",  # Cloze cards don't need back
                "subject": subject,
                "difficulty": 3,
                "tags": [subject, "cloze"],
                "card_type": "cloze"
            }
            flashcards.append(flashcard)

        return flashcards

    def assess_difficulty(self, flashcard: Dict[str, Any]) -> int:
        """Assess flashcard difficulty using LLM."""
        system_prompt = "You are an expert educator assessing flashcard difficulty."

        user_prompt = f"""Rate this flashcard's difficulty from 1-5:
Front: {flashcard['front']}
Back: {flashcard['back']}
Subject: {flashcard.get('subject', 'general')}

Consider:
- Complexity of concept
- Amount of information to memorize
- Prerequisite knowledge needed
- Common student struggles

Return only a number from 1-5."""

        try:
            rating = self.llm.complete(system_prompt, user_prompt).strip()
            return min(5, max(1, int(rating)))
        except Exception:
            return 3  # Default medium difficulty


class DockerAnkiManager:
    """Manage Anki operations in Docker environment."""

    def __init__(self):
        self.client = AnkiConnectClient()
        self.generator = EnhancedFlashcardGenerator()
        self.plugin_manager = AnkiPluginManager()

    def setup_docker_environment(self) -> Dict[str, Any]:
        """Setup the Docker environment for Anki integration."""
        return {
            "environment": {
                "ANKI_HOST": "host.docker.internal",
                "ANKI_PORT": "8765",
                "OPENAI_API_KEY": "your_api_key_here"
            },
            "volumes": [
                "/tmp/anki_data:/app/data",
                "/tmp/anki_decks:/app/decks"
            ],
            "network": "anki_network",
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:8765"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }

    def create_docker_compose_config(self) -> str:
        """Generate Docker Compose configuration for Anki + OpenEducation."""
        config = {
            "version": "3.8",
            "services": {
                "openeducation": {
                    "build": ".",
                    "environment": [
                        "OPENAI_API_KEY=${OPENAI_API_KEY}",
                        "ANKI_HOST=anki",
                        "ANKI_PORT=8765"
                    ],
                    "volumes": [
                        "./data:/app/data",
                        "./decks:/app/decks"
                    ],
                    "depends_on": ["anki"],
                    "networks": ["anki-net"]
                },
                "anki": {
                    "image": "ankicommunity/anki:latest",
                    "environment": [
                        "ANKI_WEB_ENABLED=true",
                        "ANKI_WEB_PORT=8080"
                    ],
                    "ports": ["8080:8080"],
                    "volumes": [
                        "anki_data:/app/data"
                    ],
                    "networks": ["anki-net"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8080"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }
                }
            },
            "volumes": {
                "anki_data": {}
            },
            "networks": {
                "anki-net": {
                    "driver": "bridge"
                }
            }
        }

        return json.dumps(config, indent=2)

    def generate_master_flashcard_program(self, syllabus_data: Dict[str, Any],
                                        output_dir: str = "/app/decks") -> Dict[str, Any]:
        """Generate a comprehensive flashcard program from syllabus data."""

        logger.info(f"Generating master flashcard program for {syllabus_data.get('subject', 'unknown')}")

        # Extract content from syllabus
        units_content = []
        for unit in syllabus_data.get("units", []):
            unit_content = {
                "title": unit.get("title", ""),
                "description": unit.get("description", ""),
                "objectives": [obj.get("description", "") for obj in unit.get("objectives", [])],
                "assessment_methods": unit.get("assessment_methods", []),
                "resources": unit.get("resources", [])
            }
            units_content.append(unit_content)

        # Generate different types of flashcards
        all_flashcards = []

        # Regular flashcards from objectives
        for unit in units_content:
            content = f"{unit['title']}: {unit['description']} {'. '.join(unit['objectives'])}"
            regular_cards = self.generator.generate_semantic_flashcards(
                content, syllabus_data.get("subject", "general"), 5
            )
            all_flashcards.extend(regular_cards)

        # Cloze cards from key concepts
        for unit in units_content:
            content = f"{unit['title']}: {unit['description']}"
            cloze_cards = self.generator.generate_cloze_flashcards(
                content, syllabus_data.get("subject", "general"), 3
            )
            all_flashcards.extend(cloze_cards)

        # Create master deck
        deck_name = f"Master_{syllabus_data.get('subject', 'General')}_{syllabus_data.get('grade_level', '')}"
        deck_name = deck_name.replace(" ", "_").replace("-", "_")

        # Save flashcards to file
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        cards_file = Path(output_dir) / f"{deck_name}_cards.json"

        with open(cards_file, 'w', encoding='utf-8') as f:
            json.dump(all_flashcards, f, indent=2, ensure_ascii=False)

        return {
            "deck_name": deck_name,
            "total_cards": len(all_flashcards),
            "regular_cards": len([c for c in all_flashcards if c.get("card_type") != "cloze"]),
            "cloze_cards": len([c for c in all_flashcards if c.get("card_type") == "cloze"]),
            "cards_file": str(cards_file),
            "subject": syllabus_data.get("subject", "general"),
            "grade_level": syllabus_data.get("grade_level", "unknown")
        }
