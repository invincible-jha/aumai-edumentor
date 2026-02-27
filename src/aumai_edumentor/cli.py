"""CLI entry point for aumai-edumentor."""

from __future__ import annotations

import json
import sys

import click

from .core import AssessmentEngine, ContentLibrary, PathGenerator
from .models import LearnerProfile


@click.group()
@click.version_option()
def main() -> None:
    """AumAI EduMentor — Personalised learning AI aligned with NCF 2023."""


@main.command("path")
@click.option("--learner", "learner_file", required=True, type=click.Path(exists=True), help="Path to JSON file with LearnerProfile")
@click.option("--subject", required=True, help="Subject name (e.g. math, science, hindi)")
def path(learner_file: str, subject: str) -> None:
    """Generate a personalised learning path for a learner."""
    with open(learner_file) as fh:
        learner = LearnerProfile.model_validate(json.load(fh))

    generator = PathGenerator()
    learning_path = generator.generate(learner, subject)

    click.echo(f"\nLEARNING PATH: {learner.name} | {subject.upper()}")
    click.echo(f"Grade: {learner.grade} | Learning Style: {learner.learning_style}")
    click.echo(f"Total units: {len(learning_path.content_sequence)}")
    click.echo("=" * 60)

    for i, content in enumerate(learning_path.content_sequence, 1):
        click.echo(f"\n{i}. [{content.difficulty.upper()}] {content.topic}")
        click.echo(f"   Type: {content.content_type} | Grade: {content.grade_level}")
        click.echo(f"   NCF: {', '.join(content.ncf_alignment)}")
        preview = content.content[:150] + "..." if len(content.content) > 150 else content.content
        click.echo(f"   Preview: {preview}")
    click.echo()


@main.command("assess")
@click.option("--learner-id", required=True, help="Learner identifier")
@click.option("--subject", required=True, help="Subject being assessed")
@click.option("--answers", "answers_file", required=True, type=click.Path(exists=True), help="Path to JSON file with list of answer objects")
def assess(learner_id: str, subject: str, answers_file: str) -> None:
    """Evaluate learner answers and generate an assessment result."""
    with open(answers_file) as fh:
        answers_data: list[dict[str, object]] = json.load(fh)

    engine = AssessmentEngine()
    result = engine.evaluate(learner_id, subject, answers_data)

    click.echo(f"\nASSESSMENT RESULT")
    click.echo(f"Learner ID: {result.learner_id} | Subject: {result.subject}")
    click.echo(f"Score: {result.score:.1f}%")

    grade_label = "Excellent" if result.score >= 80 else "Good" if result.score >= 60 else "Needs Improvement"
    click.echo(f"Performance: {grade_label}")

    click.echo("\nAREAS TO IMPROVE:")
    for area in result.areas_to_improve:
        click.echo(f"  - {area}")
    click.echo()


@main.command("subjects")
def subjects() -> None:
    """List available subjects in the content library."""
    library = ContentLibrary()
    click.echo("\nAVAILABLE SUBJECTS:")
    for subject in library.all_subjects():
        count = len(library.search(subject))
        click.echo(f"  - {subject} ({count} content units)")
    click.echo()


EDUCATIONAL_DISCLAIMER = (
    "This tool provides AI-assisted educational recommendations only."
    " Learning plans should be reviewed by qualified educators."
    " This tool does not replace professional pedagogical assessment."
)


@main.command("serve")
@click.option("--port", default=8000, help="Port to serve on")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def serve(port: int, host: str) -> None:
    """Start the EduMentor API server."""
    click.echo(f"\nDISCLAIMER: {EDUCATIONAL_DISCLAIMER}\n")
    try:
        import uvicorn
    except ImportError:
        click.echo("Error: uvicorn is required. Install with: pip install uvicorn", err=True)
        sys.exit(1)
    uvicorn.run("aumai_edumentor.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
