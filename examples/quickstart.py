"""Quickstart examples for aumai-edumentor.

This script demonstrates the three core workflows:
  1. Browsing the built-in content library
  2. Generating a personalised learning path
  3. Running and interpreting an assessment

Run directly to verify your installation:

    python examples/quickstart.py

Educational Disclaimer: This tool is an educational aid. Always verify
recommendations with qualified educators and follow local curriculum guidelines.
"""

from __future__ import annotations

from aumai_edumentor.core import AssessmentEngine, ContentLibrary, PathGenerator
from aumai_edumentor.models import LearnerProfile, LearningContent


def demo_content_library() -> None:
    """Demonstrate ContentLibrary search and inspection.

    The built-in library ships with 25 content units across five subjects.
    You can search by subject, filter by difficulty or grade level, and
    add your own custom content without modifying built-in data.
    """
    print("\n" + "=" * 60)
    print("DEMO 1: Content Library")
    print("=" * 60)

    library = ContentLibrary()

    # List all available subjects
    subjects = library.all_subjects()
    print(f"\nAvailable subjects: {', '.join(subjects)}")

    # Count total content units
    all_units = library.all_content()
    print(f"Total built-in content units: {len(all_units)}")

    # Search math content at grade 5
    grade5_math = library.search("math", grade=5)
    print(f"\nMath content at grade 5: {len(grade5_math)} unit(s)")
    for unit in grade5_math:
        print(f"  [{unit.difficulty:12s}] {unit.topic} ({unit.content_type})")
        print(f"    NCF: {', '.join(unit.ncf_alignment)}")

    # Add a custom content unit
    custom = LearningContent(
        content_id="math-custom-001",
        subject="math",
        topic="Profit and Loss",
        difficulty="intermediate",
        content_type="activity",
        content=(
            "Calculate profit/loss for a small shop. "
            "Given cost price Rs 150, selling price Rs 180: find profit %."
        ),
        ncf_alignment=["NCF-MATH-G6-ARI-1"],
        grade_level=6,
    )
    library.add(custom)

    # Confirm the custom unit appears in searches
    updated = library.search("math", grade=6)
    custom_found = any(u.content_id == "math-custom-001" for u in updated)
    print(f"\nCustom unit added — visible in grade 6 search: {custom_found}")


def demo_path_generation() -> None:
    """Demonstrate PathGenerator for two different learner profiles.

    Two learners in the same grade receive different paths because:
    - Priya is weak in math and visual → gets activity content first, starts at beginner
    - Rahul has no math weakness and is auditory → gets text content first, intermediate start
    """
    print("\n" + "=" * 60)
    print("DEMO 2: Personalised Path Generation")
    print("=" * 60)

    generator = PathGenerator()

    # Learner 1: visual, math is a weakness
    priya = LearnerProfile(
        learner_id="student-001",
        name="Priya",
        age=12,
        grade=7,
        language="en",
        strengths=["science"],
        weaknesses=["math"],
        learning_style="visual",
    )

    # Learner 2: auditory, no math weakness
    rahul = LearnerProfile(
        learner_id="student-002",
        name="Rahul",
        age=13,
        grade=7,
        language="en",
        strengths=["math", "english"],
        weaknesses=["hindi"],
        learning_style="auditory",
    )

    priya_path = generator.generate(priya, "math")
    rahul_path = generator.generate(rahul, "math")

    print(f"\nPriya's path — {len(priya_path.content_sequence)} unit(s):")
    for unit in priya_path.content_sequence:
        print(f"  [{unit.difficulty:12s}] {unit.topic} ({unit.content_type})")

    print(f"\nRahul's path — {len(rahul_path.content_sequence)} unit(s):")
    for unit in rahul_path.content_sequence:
        print(f"  [{unit.difficulty:12s}] {unit.topic} ({unit.content_type})")

    # Show that paths differ due to personalisation
    priya_first = priya_path.content_sequence[0].topic if priya_path.content_sequence else "none"
    rahul_first = rahul_path.content_sequence[0].topic if rahul_path.content_sequence else "none"
    print(f"\nPriya starts with: {priya_first}")
    print(f"Rahul starts with:  {rahul_first}")
    print("(Different starting points reflect weakness and learning style differences)")


def demo_assessment_engine() -> None:
    """Demonstrate AssessmentEngine with three different answer scenarios.

    The engine handles:
    - Typical mixed performance (some right, some wrong)
    - Excellent performance (all correct)
    - Edge case: empty answer list
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Assessment Engine")
    print("=" * 60)

    engine = AssessmentEngine()

    # Scenario 1: Typical mixed performance
    mixed_answers = [
        {"question_id": "q1", "correct": True,  "topic": "Geometry: Triangles"},
        {"question_id": "q2", "correct": True,  "topic": "Geometry: Triangles"},
        {"question_id": "q3", "correct": False, "topic": "Algebra Introduction"},
        {"question_id": "q4", "correct": False, "topic": "Linear Equations"},
    ]
    result = engine.evaluate("student-001", "math", mixed_answers)
    print(f"\nScenario 1 — Mixed performance:")
    print(f"  Score: {result.score}%")
    print(f"  Areas to improve: {result.areas_to_improve}")

    # Scenario 2: Excellent — all correct
    excellent_answers = [
        {"question_id": f"q{i}", "correct": True, "topic": "Fractions"}
        for i in range(1, 6)
    ]
    result2 = engine.evaluate("student-002", "math", excellent_answers)
    print(f"\nScenario 2 — Excellent performance:")
    print(f"  Score: {result2.score}%")
    print(f"  Areas to improve: {result2.areas_to_improve}")

    # Scenario 3: Edge case — no answers provided
    result3 = engine.evaluate("student-003", "science", [])
    print(f"\nScenario 3 — Empty answers:")
    print(f"  Score: {result3.score}%")
    print(f"  Areas to improve: {result3.areas_to_improve}")


def demo_json_roundtrip() -> None:
    """Demonstrate LearnerProfile JSON validation for API / file use.

    In production, learner profiles arrive as JSON from a form, API request,
    or file. Pydantic validates all fields including age bounds, grade bounds,
    and the learning_style pattern.
    """
    print("\n" + "=" * 60)
    print("DEMO 4: JSON Roundtrip and Validation")
    print("=" * 60)

    import json

    raw = {
        "learner_id": "api-learner-42",
        "name": "Ananya",
        "age": 9,
        "grade": 4,
        "language": "hi",
        "strengths": ["hindi", "social_studies"],
        "weaknesses": ["english"],
        "learning_style": "kinesthetic",
    }

    learner = LearnerProfile.model_validate(raw)
    print(f"\nValidated learner: {learner.name}, Grade {learner.grade}, Style: {learner.learning_style}")

    # Serialise back to JSON
    serialised = learner.model_dump()
    roundtrip_json = json.dumps(serialised, ensure_ascii=False, indent=2)
    print(f"Serialised to JSON ({len(roundtrip_json)} chars)")

    # Demonstrate validation error for bad learning_style
    try:
        LearnerProfile.model_validate({**raw, "learning_style": "reading"})
    except Exception as exc:
        print(f"\nValidation error for bad learning_style: {type(exc).__name__}")

    # Generate a path from the validated learner
    generator = PathGenerator()
    path = generator.generate(learner, "english")
    print(f"Generated English path for {learner.name}: {len(path.content_sequence)} unit(s)")


def main() -> None:
    """Run all quickstart demonstrations."""
    print("aumai-edumentor Quickstart")
    print("Educational Disclaimer: Verify recommendations with qualified educators.")

    demo_content_library()
    demo_path_generation()
    demo_assessment_engine()
    demo_json_roundtrip()

    print("\n" + "=" * 60)
    print("All demos complete.")
    print("See docs/api-reference.md for full API documentation.")
    print("=" * 60)


if __name__ == "__main__":
    main()
