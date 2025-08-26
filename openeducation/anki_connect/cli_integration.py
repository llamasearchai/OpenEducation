from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from .advanced import AnkiConnectClient, AnkiDeckManager, AnkiSyncManager

app = typer.Typer(help="Advanced Anki integration and management")


@app.command()
def check_connection(
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Check connection to Anki via AnkiConnect."""
    try:
        client = AnkiConnectClient(host, port)

        if client.is_connected():
            version = client.get_version()
            deck_names = client.get_deck_names()
            model_names = client.get_model_names()

            print("✅ Successfully connected to Anki!")
            print(f"   Version: {version}")
            print(f"   Decks: {len(deck_names)}")
            print(f"   Models: {len(model_names)}")

            if deck_names:
                print("\n📚 Available Decks:")
                for deck in deck_names[:5]:  # Show first 5
                    print(f"   • {deck}")
                if len(deck_names) > 5:
                    print(f"   ... and {len(deck_names) - 5} more")
        else:
            print("❌ Cannot connect to Anki")
            print("   Make sure Anki is running with AnkiConnect plugin installed")
            print("   Download from: https://ankiweb.net/shared/info/2055492159")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise typer.Exit(1)


@app.command()
def create_educational_deck(
    deck_name: str = typer.Option(..., help="Name for the new deck"),
    cards_file: str = typer.Option(..., help="Path to JSON file with card data"),
    subject: str = typer.Option("", help="Subject area for the cards"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Create an educational deck with custom model optimized for learning."""
    try:
        # Load card data
        if not Path(cards_file).exists():
            raise FileNotFoundError(f"Cards file not found: {cards_file}")

        with open(cards_file, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)

        if not cards_data:
            raise ValueError("No card data found in file")

        # Create manager
        client = AnkiConnectClient(host, port)
        manager = AnkiDeckManager(client)

        # Add subject to each card
        for card in cards_data:
            if subject and "subject" not in card:
                card["subject"] = subject

        # Create the deck
        result = manager.create_educational_deck(deck_name, cards_data)

        print(f"✅ Educational deck '{deck_name}' created successfully!")
        print(f"   Cards Added: {result['notes_created']}")
        print(f"   Note IDs: {len(result['note_ids'])}")
        print(f"   Model: OpenEducation Basic")

        # Show sample cards
        print("\n📝 Sample Cards:")
        for i, card in enumerate(cards_data[:3]):
            print(f"   {i+1}. {card.get('front', '')[:50]}...")

        if len(cards_data) > 3:
            print(f"   ... and {len(cards_data) - 3} more cards")

    except Exception as e:
        print(f"❌ Error creating deck: {e}")
        raise typer.Exit(1)


@app.command()
def get_study_recommendations(
    deck_name: str = typer.Option(..., help="Name of the deck to analyze"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Get personalized study recommendations for a deck."""
    try:
        client = AnkiConnectClient(host, port)
        manager = AnkiDeckManager(client)

        recommendations = manager.get_study_recommendations(deck_name)

        print(f"📚 Study Recommendations for '{deck_name}'")
        print("=" * 60)

        print("⏰ Daily Study Time:")
        print(f"   Recommended: {recommendations['daily_study_time']}")
        print(f"   Break Reminders: {recommendations['break_reminders']}")

        print("\n📅 Session Structure:")
        for activity, duration in recommendations['session_structure'].items():
            print(f"   • {activity}: {duration}")

        print("\n🎯 Difficulty Focus:")
        for rec in recommendations['difficulty_focus']:
            print(f"   • {rec}")

        print("\n🔥 Motivation:")
        print(f"   Goal: {recommendations['study_streak_goal']}")

        # Get deck stats
        stats = client.get_deck_stats(deck_name)
        if stats:
            print("\n📊 Current Deck Stats:")
            print(f"   Total Cards: {stats.get('total', 0)}")
            print(f"   New Cards: {stats.get('new', 0)}")
            print(f"   Review Cards: {stats.get('review', 0)}")
            print(f"   Cards Studied Today: {stats.get('cards_studied_today', 0)}")

    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        raise typer.Exit(1)


@app.command()
def create_study_plan(
    deck_name: str = typer.Option(..., help="Name of the deck"),
    days: int = typer.Option(30, help="Number of days for the study plan"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Create a personalized study plan based on deck analysis."""
    try:
        client = AnkiConnectClient(host, port)
        manager = AnkiDeckManager(client)

        study_plan = manager.create_study_plan(deck_name, days)

        print(f"📅 {days}-Day Study Plan for '{deck_name}'")
        print("=" * 60)

        daily = study_plan["daily_goals"]
        print("\n🎯 Daily Goals:")
        print(f"   New Cards: {daily['new_cards']}")
        print(f"   Review Cards: {daily['review_cards']}")
        print(f"   Study Time: {daily['study_time_minutes']} minutes")

        print("\n📚 Session Structure:")
        for activity, duration in study_plan["session_structure"].items():
            print(f"   • {activity}: {duration}")

        print("\n🏆 Milestones:")
        for milestone in study_plan["milestones"]:
            print(f"   Day {milestone['day']}: {milestone['goal']}")

        if study_plan["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in study_plan["recommendations"]:
                print(f"   • {rec}")

    except Exception as e:
        print(f"❌ Error creating study plan: {e}")
        raise typer.Exit(1)


@app.command()
def get_progress_analytics(
    deck_name: str = typer.Option(..., help="Name of the deck to analyze"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Get detailed progress analytics for a deck."""
    try:
        client = AnkiConnectClient(host, port)
        manager = AnkiDeckManager(client)

        analytics = manager.get_progress_analytics(deck_name)

        print(f"📊 Progress Analytics for '{deck_name}'")
        print("=" * 60)

        progress = analytics["progress_metrics"]
        print("\n📈 Today's Progress:")
        print(f"   Cards Studied: {progress['cards_studied_today']}")
        print(f"   Time Studied: {progress['time_studied_today']} minutes")
        print(f"   Retention Rate: {progress['retention_rate']:.1f}%")
        print(f"   Study Streak: {progress['study_streak']} days")

        goals = analytics["next_session_goals"]
        print("\n🎯 Next Session Goals:")
        print(f"   New Cards: {goals['new_cards']}")
        print(f"   Review Cards: {goals['review_cards']}")

        study_rec = analytics["study_recommendations"]
        print("\n💡 Study Recommendations:")
        print(f"   Daily Time: {study_rec['daily_study_time']}")
        for rec in study_rec['difficulty_focus']:
            print(f"   • {rec}")

    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
        raise typer.Exit(1)


@app.command()
def export_educational_deck(
    deck_name: str = typer.Option(..., help="Name of the deck to export"),
    output_path: str = typer.Option(..., help="Output path for the package"),
    include_progress: bool = typer.Option(True, help="Include scheduling progress"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Export a deck with educational metadata."""
    try:
        client = AnkiConnectClient(host, port)
        manager = AnkiDeckManager(client)

        export_path = manager.export_educational_deck(deck_name, output_path, include_progress)

        print(f"✅ Educational deck exported successfully!")
        print(f"   Deck: {deck_name}")
        print(f"   Package: {export_path}")
        print(f"   Progress Included: {include_progress}")

        # Show file size
        file_size = Path(export_path).stat().st_size / 1024  # KB
        print(f"   File Size: {file_size:.1f} KB")
        # Show metadata if it exists
        metadata_path = export_path.replace('.apkg', '_metadata.json')
        if Path(metadata_path).exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print("\n📋 Educational Metadata:")
            print(f"   Purpose: {metadata.get('educational_purpose', 'N/A')}")
            print(f"   Recommended Time: {metadata.get('recommended_study_time', 'N/A')}")

    except Exception as e:
        print(f"❌ Error exporting deck: {e}")
        raise typer.Exit(1)


@app.command()
def sync_syllabus_progress(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    student_id: str = typer.Option(..., help="Student identifier"),
    anki_decks: str = typer.Option(..., help="Comma-separated list of Anki deck names"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Sync syllabus learning progress with Anki study progress."""
    try:
        client = AnkiConnectClient(host, port)
        sync_manager = AnkiSyncManager(client)

        deck_list = [deck.strip() for deck in anki_decks.split(",")]

        result = sync_manager.sync_syllabus_progress(syllabus_id, student_id)

        print(f"✅ Progress synchronization completed!")
        print(f"   Syllabus: {syllabus_id}")
        print(f"   Student: {student_id}")
        print(f"   Anki Decks: {len(deck_list)}")
        print(f"   Status: {result.get('sync_status', 'unknown')}")

        for deck in deck_list:
            if deck in client.get_deck_names():
                stats = client.get_deck_stats(deck)
                print(f"   📚 {deck}: {stats.get('total', 0)} cards")

    except Exception as e:
        print(f"❌ Error syncing progress: {e}")
        raise typer.Exit(1)


@app.command()
def create_adaptive_plan(
    syllabus_id: str = typer.Option(..., help="ID of the syllabus"),
    anki_decks: str = typer.Option(..., help="Comma-separated list of Anki deck names"),
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """Create an adaptive study plan based on syllabus and Anki performance."""
    try:
        client = AnkiConnectClient(host, port)
        sync_manager = AnkiSyncManager(client)

        deck_list = [deck.strip() for deck in anki_decks.split(",")]

        adaptive_plan = sync_manager.create_adaptive_study_plan(syllabus_id, deck_list)

        print(f"🎯 Adaptive Study Plan for '{syllabus_id}'")
        print("=" * 60)

        adjustments = adaptive_plan["adaptive_plan"]["adjustments"]
        if adjustments:
            print("\n🔧 Recommended Adjustments:")
            for adj in adjustments:
                print(f"   • {adj}")

        strong = adaptive_plan["adaptive_plan"]["strong_areas"]
        if strong:
            print("\n💪 Strong Areas:")
            for area in strong:
                print(f"   ✓ {area}")

        weak = adaptive_plan["adaptive_plan"]["weak_areas"]
        if weak:
            print("\n📈 Areas for Improvement:")
            for area in weak:
                print(f"   • {area}")

        print("\n📚 Anki Integration:")
        for deck in adaptive_plan["anki_integration"]["decks_to_focus"]:
            print(f"   • Focus on: {deck}")

        print("\n💡 Next Steps:")
        print("   1. Review weak areas with additional study")
        print("   2. Continue practicing in Anki")
        print("   3. Track progress and adjust as needed")

    except Exception as e:
        print(f"❌ Error creating adaptive plan: {e}")
        raise typer.Exit(1)


@app.command()
def list_decks(
    host: str = typer.Option("localhost", help="AnkiConnect host"),
    port: int = typer.Option(8765, help="AnkiConnect port")
) -> None:
    """List all available decks in Anki."""
    try:
        client = AnkiConnectClient(host, port)

        if not client.is_connected():
            print("❌ Cannot connect to Anki")
            raise typer.Exit(1)

        deck_names = client.get_deck_names()

        print(f"📚 Available Decks in Anki ({len(deck_names)} total)")
        print("=" * 50)

        for deck in deck_names:
            try:
                stats = client.get_deck_stats(deck)
                total_cards = stats.get('total', 0)
                new_cards = stats.get('new', 0)
                review_cards = stats.get('review', 0)
                print("20")
            except Exception:
                print("20")

    except Exception as e:
        print(f"❌ Error listing decks: {e}")
        raise typer.Exit(1)


@app.command()
def generate_master_deck(
    syllabus_file: str = typer.Argument(..., help="Path to syllabus JSON file"),
    output_dir: str = typer.Option("/app/decks", help="Output directory for flashcard decks"),
    num_cards_per_unit: int = typer.Option(5, help="Number of cards to generate per unit"),
    include_cloze: bool = typer.Option(True, help="Include cloze deletion cards"),
) -> None:
    """Generate a comprehensive master flashcard deck from syllabus content."""
    try:
        from .advanced import DockerAnkiManager

        # Load syllabus
        with open(syllabus_file, 'r', encoding='utf-8') as f:
            syllabus_data = json.load(f)

        print(f"🎯 Generating Master Flashcard Program")
        print(f"   Subject: {syllabus_data.get('subject', 'Unknown')}")
        print(f"   Grade Level: {syllabus_data.get('grade_level', 'Unknown')}")
        print(f"   Units: {len(syllabus_data.get('units', []))}")
        print("=" * 60)

        # Create Docker manager
        manager = DockerAnkiManager()

        # Generate master flashcard program
        result = manager.generate_master_flashcard_program(syllabus_data, output_dir)

        print("\n✅ Master Flashcard Program Generated Successfully!")
        print(f"   Deck Name: {result['deck_name']}")
        print(f"   Total Cards: {result['total_cards']}")
        print(f"   Regular Cards: {result['regular_cards']}")
        print(f"   Cloze Cards: {result['cloze_cards']}")
        print(f"   Cards File: {result['cards_file']}")

        # Show sample cards
        if Path(result['cards_file']).exists():
            with open(result['cards_file'], 'r', encoding='utf-8') as f:
                cards = json.load(f)

            print("\n📝 Sample Cards:")
            for i, card in enumerate(cards[:3]):
                print(f"   {i+1}. {card.get('front', '')[:60]}...")
                if card.get('card_type') == 'cloze':
                    print("      (Cloze card)")
                else:
                    print(f"      → {card.get('back', '')[:60]}...")

            if len(cards) > 3:
                print(f"   ... and {len(cards) - 3} more cards")

        print("\n💡 Next Steps:")
        print("   1. Review and edit cards in the generated JSON file")
        print("   2. Use 'create-educational-deck' to import into Anki")
        print("   3. Run study sessions and track progress")

    except Exception as e:
        print(f"❌ Error generating master deck: {e}")
        raise typer.Exit(1)


@app.command()
def setup_docker_environment(
    output_file: str = typer.Option("docker-compose.yml", help="Output Docker Compose file")
) -> None:
    """Setup Docker environment for OpenEducation + Anki integration."""
    try:
        from .advanced import DockerAnkiManager

        manager = DockerAnkiManager()

        # Generate Docker Compose config
        docker_config = manager.create_docker_compose_config()

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(docker_config)

        print("🐳 Docker Environment Setup Complete!")
        print(f"   Configuration saved to: {output_file}")
        print("\n📋 Setup Instructions:")
        print("   1. Ensure Docker and Docker Compose are installed")
        print("   2. Set your OPENAI_API_KEY environment variable")
        print("   3. Run: docker-compose up -d")
        print("   4. Access OpenEducation CLI: docker-compose exec openeducation bash")
        print("   5. Access Anki Web: http://localhost:8080")

        # Show environment setup
        env_setup = manager.setup_docker_environment()
        print("\n🔧 Environment Variables to Set:")
        for key, value in env_setup['environment'].items():
            print(f"   export {key}={value}")

        print("\n📊 Health Check:")
        print("   AnkiConnect will be available at http://localhost:8765")
        print("   Use 'check-connection' command to verify connectivity")

    except Exception as e:
        print(f"❌ Error setting up Docker environment: {e}")
        raise typer.Exit(1)


@app.command()
def list_supported_plugins() -> None:
    """List all supported Anki plugins and their features."""
    try:
        from .advanced import AnkiPluginManager

        manager = AnkiPluginManager()
        plugins = manager.get_supported_plugins()

        print("🔌 Supported Anki Plugins")
        print("=" * 50)

        for plugin_id, plugin_info in plugins.items():
            required = "Required" if plugin_info.get("required", False) else "Optional"
            print(f"\n📦 {plugin_info['name']} ({required})")
            print(f"   {plugin_info['description']}")
            print(f"   URL: {plugin_info['url']}")

            features = plugin_info.get('features', [])
            if features:
                print("   Features:")
                for feature in features:
                    print(f"     • {feature}")

            # Check compatibility
            compatibility = manager.check_plugin_compatibility(plugin_id)
            status = "✅ Compatible" if compatibility['compatible'] else "❌ Not Compatible"
            print(f"   Status: {status}")
            if not compatibility['compatible']:
                print(f"   Reason: {compatibility['reason']}")

    except Exception as e:
        print(f"❌ Error listing plugins: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
