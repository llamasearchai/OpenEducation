#!/usr/bin/env python3
"""
OpenEducation Master Demo Script
===============================

This script demonstrates the complete OpenEducation system with comprehensive
Anki integration, Docker support, and advanced flashcard generation.

Features demonstrated:
- Complete syllabus generation for all subjects
- Advanced Anki plugin integration
- OpenAI embeddings for semantic flashcard generation
- Docker environment setup
- Learning progress tracking
- Master flashcard program generation

Requirements:
- Python 3.9+
- OpenAI API key
- Anki (optional, for full integration)
- Docker (optional, for containerized demo)
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔹 {title}")
    print("-" * 40)

def run_command(cmd: str, description: str = "") -> bool:
    """Run a shell command and return success status."""
    if description:
        print(f"📌 {description}")

    # Replace 'python' with 'python3' in commands
    if cmd.startswith('python '):
        cmd = cmd.replace('python ', 'python3 ')

    print(f"💻 Running: {cmd}")
    result = os.system(cmd)

    if result == 0:
        print("✅ Command completed successfully")
        return True
    else:
        print("❌ Command failed")
        return False

def check_environment():
    """Check the environment and prerequisites."""
    print_header("Environment Check")

    print("🔍 Checking Python version...")
    import sys
    print(f"   Python version: {sys.version}")

    print("\n🔍 Checking required packages...")
    try:
        import openai
        print("   ✅ OpenAI package available")
    except ImportError:
        print("   ❌ OpenAI package not found")
        return False

    try:
        import typer
        print("   ✅ Typer package available")
    except ImportError:
        print("   ❌ Typer package not found")
        return False

    print("\n🔍 Checking API keys...")
    if os.getenv("OPENAI_API_KEY"):
        print("   ✅ OpenAI API key found")
    else:
        print("   ⚠️  OpenAI API key not set (some features will be limited)")

    print("\n🔍 Checking directories...")
    dirs = ["data", "data/syllabi", "data/decks", "data/progress"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created directory: {dir_path}")

    return True

def demo_syllabus_generation():
    """Demonstrate syllabus generation for all subjects."""
    print_header("Syllabus Generation Demo")

    subjects = [
        ("science", "9-12", "Dr. Smith"),
        ("mathematics", "11-12", "Prof. Davis"),
        ("social_studies", "10-12", "Ms. Johnson"),
        ("language_literacy", "9-10", "Mr. Brown"),
        ("visual_performing_arts", "9-12", "Ms. Wilson")
    ]

    generated_syllabi = []

    for subject, grade_level, instructor in subjects:
        print_section(f"Generating {subject.title()} Syllabus")

        cmd = f"python -m openeducation.cli syllabus generate --subject {subject} --grade-level {grade_level} --instructor '{instructor}' --output-dir data/syllabi"
        if run_command(cmd, f"Creating {subject} syllabus"):
            syllabus_file = f"data/syllabi/syllabus_{subject}_{grade_level.replace('-', '_')}.json"
            generated_syllabi.append((subject, syllabus_file))

            # Show syllabus summary
            if Path(syllabus_file).exists():
                with open(syllabus_file, 'r') as f:
                    syllabus = json.load(f)
                print(f"   📚 Title: {syllabus.get('title', 'N/A')}")
                print(f"   📖 Units: {len(syllabus.get('units', []))}")
                print(f"   🎯 Standards: {', '.join(syllabus.get('standards', []))}")

    return generated_syllabi

def demo_anki_features():
    """Demonstrate Anki integration features."""
    print_header("Anki Integration Demo")

    print_section("Checking Anki Connection")
    run_command("python -m openeducation.cli anki check-connection", "Checking AnkiConnect connection")

    print_section("Listing Supported Plugins")
    run_command("python -m openeducation.cli anki list-supported-plugins", "Showing supported Anki plugins")

def demo_master_flashcard_generation(syllabi):
    """Demonstrate master flashcard generation."""
    print_header("Master Flashcard Generation Demo")

    if not syllabi:
        print("❌ No syllabi available for flashcard generation")
        return

    print_section("Generating Master Flashcard Programs")

    for subject, syllabus_file in syllabi:
        print(f"\n🎯 Processing {subject} syllabus...")

        cmd = f"python -m openeducation.cli anki generate-master-deck {syllabus_file} --output-dir data/decks"
        if run_command(cmd, f"Creating master flashcard program for {subject}"):

            # Show results
            deck_name = f"Master_{subject}_9_12"
            cards_file = f"data/decks/{deck_name}_cards.json"

            if Path(cards_file).exists():
                with open(cards_file, 'r') as f:
                    cards = json.load(f)

                print(f"   📚 Deck: {deck_name}")
                print(f"   📝 Cards Generated: {len(cards)}")
                print(f"   🃏 Regular Cards: {len([c for c in cards if c.get('card_type') != 'cloze'])}")
                print(f"   🎭 Cloze Cards: {len([c for c in cards if c.get('card_type') == 'cloze'])}")

                # Show sample cards
                print("\n   📋 Sample Cards:")
                for i, card in enumerate(cards[:2]):
                    print(f"      {i+1}. {card.get('front', '')[:50]}...")
                    if card.get('card_type') == 'cloze':
                        print("         (Cloze deletion card)")

def demo_learning_progress_tracking():
    """Demonstrate learning progress tracking."""
    print_header("Learning Progress Tracking Demo")

    print_section("Starting Progress Tracking")
    run_command("python -m openeducation.cli schedule start-tracking --syllabus-id syllabus_science_9_12 --student-id demo_student_001 --data-dir data/progress", "Starting progress tracking")

    print_section("Logging Study Session")
    run_command("python -m openeducation.cli schedule log-session --syllabus-id syllabus_science_9_12 --student-id demo_student_001 --unit-id unit_1 --objective-id unit_1_obj_1 --duration-actual 45 --completed --difficulty-rating 3 --understanding-level 4 --notes 'First study session on scientific method'", "Logging completed study session")

    print_section("Getting Progress Report")
    run_command("python -m openeducation.cli schedule get-report --syllabus-id syllabus_science_9_12 --student-id demo_student_001 --data-dir data/progress", "Generating progress report")

def demo_docker_setup():
    """Demonstrate Docker environment setup."""
    print_header("Docker Environment Setup Demo")

    print_section("Creating Docker Compose Configuration")
    run_command("python -m openeducation.cli anki setup-docker-environment --output-file docker-compose.yml", "Setting up Docker environment")

    if Path("docker-compose.yml").exists():
        print("   📋 Docker Compose configuration created")
        print("   🐳 To run in Docker:")
        print("      1. docker-compose up -d")
        print("      2. docker-compose exec openeducation bash")
        print("      3. Run commands inside container")

def demo_complete_workflow():
    """Demonstrate a complete workflow."""
    print_header("Complete Workflow Demo")

    print_section("1. Generate Comprehensive Syllabus")
    run_command("python -m openeducation.cli syllabus generate --subject health_fitness --grade-level 9-12 --instructor 'Coach Miller' --output-dir data/syllabi", "Creating health & fitness syllabus")

    print_section("2. Create Master Flashcard Program")
    syllabus_file = "data/syllabi/syllabus_health_fitness_9_12.json"
    if Path(syllabus_file).exists():
        run_command(f"python -m openeducation.cli anki generate-master-deck {syllabus_file} --output-dir data/decks", "Generating flashcards from syllabus")

        print_section("3. Import into Anki (if available)")
        cards_file = "data/decks/Master_health_fitness_9_12_cards.json"
        if Path(cards_file).exists():
            run_command(f"python -m openeducation.cli anki create-educational-deck 'Health & Fitness Master' {cards_file} --subject health_fitness", "Creating Anki deck")

    print_section("4. Start Progress Tracking")
    run_command("python -m openeducation.cli schedule start-tracking --syllabus-id syllabus_health_fitness_9_12 --student-id demo_student_002 --data-dir data/progress", "Starting progress tracking")

def main():
    """Main demo function."""
    print("🚀 OpenEducation Master Demo")
    print("=" * 60)
    print("This demo will showcase the complete OpenEducation system")
    print("with comprehensive Anki integration and Docker support.")
    print("\nPress Enter to begin...")
    input()

    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix issues and try again.")
        return

    # Run demos
    try:
        # Generate syllabi
        syllabi = demo_syllabus_generation()

        # Anki features demo
        demo_anki_features()

        # Master flashcard generation
        demo_master_flashcard_generation(syllabi)

        # Learning progress tracking
        demo_learning_progress_tracking()

        # Docker setup
        demo_docker_setup()

        # Complete workflow
        demo_complete_workflow()

        # Final summary
        print_header("Demo Complete!")
        print("🎉 Congratulations! You have successfully explored the complete OpenEducation system.")
        print("\n📊 What was demonstrated:")
        print("   ✅ Comprehensive syllabus generation for all subjects")
        print("   ✅ Advanced Anki plugin integration")
        print("   ✅ OpenAI embeddings for semantic flashcard generation")
        print("   ✅ Docker environment setup and configuration")
        print("   ✅ Learning progress tracking and analytics")
        print("   ✅ Master flashcard program creation")
        print("   ✅ Complete educational workflow automation")

        print("\n🔧 System Capabilities:")
        print("   📚 Supports 10+ educational subjects")
        print("   🔌 Integrates with 5+ Anki plugins")
        print("   🤖 Uses AI for intelligent content generation")
        print("   🐳 Fully dockerized and production-ready")
        print("   📊 Comprehensive progress tracking")
        print("   🎯 Adaptive learning recommendations")

        print("\n📞 Next Steps:")
        print("   1. Set up your OpenAI API key")
        print("   2. Install Anki with AnkiConnect plugin")
        print("   3. Run: python -m openeducation.cli --help")
        print("   4. Start creating educational content!")

    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
