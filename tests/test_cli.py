"""Tests for aumai-edumentor CLI."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from aumai_edumentor.cli import main


def test_cli_version() -> None:
    """Version flag must report 0.1.0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help() -> None:
    """Help flag should return exit code 0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "NCF" in result.output or "learning" in result.output.lower()


def test_cli_subjects_command() -> None:
    """Subjects command should list available subjects."""
    runner = CliRunner()
    result = runner.invoke(main, ["subjects"])
    assert result.exit_code == 0
    assert "math" in result.output.lower()
    assert "AVAILABLE SUBJECTS" in result.output.upper()


def test_cli_subjects_shows_count() -> None:
    """Subjects command should show content unit count per subject."""
    runner = CliRunner()
    result = runner.invoke(main, ["subjects"])
    assert result.exit_code == 0
    # Each subject line contains "(N content units)"
    assert "content units" in result.output.lower()


def test_cli_path_command_basic() -> None:
    """Path command should generate a learning path from a JSON learner file."""
    runner = CliRunner()
    learner_data = {
        "learner_id": "cli-test-001",
        "name": "CLI Test Learner",
        "age": 10,
        "grade": 5,
        "learning_style": "visual",
    }
    with runner.isolated_filesystem():
        learner_file = "learner.json"
        with open(learner_file, "w") as fh:
            json.dump(learner_data, fh)
        result = runner.invoke(main, ["path", "--learner", learner_file, "--subject", "math"])

    assert result.exit_code == 0
    assert "CLI Test Learner" in result.output
    assert "math" in result.output.lower()


def test_cli_path_command_shows_grade_and_style() -> None:
    """Path command output should show grade and learning style."""
    runner = CliRunner()
    learner_data = {
        "learner_id": "cli-test-002",
        "name": "Style Learner",
        "age": 12,
        "grade": 7,
        "learning_style": "kinesthetic",
    }
    with runner.isolated_filesystem():
        learner_file = "learner.json"
        with open(learner_file, "w") as fh:
            json.dump(learner_data, fh)
        result = runner.invoke(main, ["path", "--learner", learner_file, "--subject", "science"])

    assert result.exit_code == 0
    assert "7" in result.output  # Grade 7
    assert "kinesthetic" in result.output.lower()


def test_cli_path_command_missing_learner_file_fails() -> None:
    """Path command with non-existent learner file should fail."""
    runner = CliRunner()
    result = runner.invoke(
        main, ["path", "--learner", "/nonexistent/file.json", "--subject", "math"]
    )
    assert result.exit_code != 0


def test_cli_path_command_missing_subject_fails() -> None:
    """Path command without --subject should fail."""
    runner = CliRunner()
    learner_data = {
        "learner_id": "cli-test-003",
        "name": "Learner",
        "age": 10,
        "grade": 5,
    }
    with runner.isolated_filesystem():
        learner_file = "learner.json"
        with open(learner_file, "w") as fh:
            json.dump(learner_data, fh)
        result = runner.invoke(main, ["path", "--learner", learner_file])

    assert result.exit_code != 0


def test_cli_assess_command_basic() -> None:
    """Assess command should evaluate answers from a JSON file."""
    runner = CliRunner()
    answers_data = [
        {"question_id": "q1", "correct": True, "topic": "Fractions"},
        {"question_id": "q2", "correct": False, "topic": "Algebra"},
    ]
    with runner.isolated_filesystem():
        answers_file = "answers.json"
        with open(answers_file, "w") as fh:
            json.dump(answers_data, fh)
        result = runner.invoke(
            main,
            ["assess", "--learner-id", "cli-learner-01", "--subject", "math", "--answers", answers_file],
        )

    assert result.exit_code == 0
    assert "cli-learner-01" in result.output
    assert "math" in result.output.lower()


def test_cli_assess_command_shows_score() -> None:
    """Assess command output should show a score percentage."""
    runner = CliRunner()
    answers_data = [
        {"question_id": "q1", "correct": True, "topic": "Fractions"},
        {"question_id": "q2", "correct": True, "topic": "Algebra"},
    ]
    with runner.isolated_filesystem():
        answers_file = "answers.json"
        with open(answers_file, "w") as fh:
            json.dump(answers_data, fh)
        result = runner.invoke(
            main,
            ["assess", "--learner-id", "learner-score-test", "--subject", "science", "--answers", answers_file],
        )

    assert result.exit_code == 0
    assert "100.0%" in result.output or "Score" in result.output


def test_cli_assess_command_shows_areas_to_improve() -> None:
    """Assess command output should show AREAS TO IMPROVE section."""
    runner = CliRunner()
    answers_data = [
        {"question_id": "q1", "correct": False, "topic": "Algebra"},
    ]
    with runner.isolated_filesystem():
        answers_file = "answers.json"
        with open(answers_file, "w") as fh:
            json.dump(answers_data, fh)
        result = runner.invoke(
            main,
            ["assess", "--learner-id", "L001", "--subject", "math", "--answers", answers_file],
        )

    assert result.exit_code == 0
    assert "AREAS TO IMPROVE" in result.output.upper()


def test_cli_assess_command_missing_answers_file_fails() -> None:
    """Assess command with non-existent answers file should fail."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["assess", "--learner-id", "L001", "--subject", "math", "--answers", "/nonexistent/answers.json"],
    )
    assert result.exit_code != 0


def test_cli_assess_command_all_correct_shows_excellent() -> None:
    """Assess with all correct answers should show Excellent performance."""
    runner = CliRunner()
    answers_data = [
        {"question_id": f"q{i}", "correct": True, "topic": "Test"}
        for i in range(5)
    ]
    with runner.isolated_filesystem():
        answers_file = "answers.json"
        with open(answers_file, "w") as fh:
            json.dump(answers_data, fh)
        result = runner.invoke(
            main,
            ["assess", "--learner-id", "excellent-learner", "--subject", "math", "--answers", answers_file],
        )

    assert result.exit_code == 0
    assert "Excellent" in result.output


def test_cli_path_command_shows_total_units() -> None:
    """Path command should show total number of content units."""
    runner = CliRunner()
    learner_data = {
        "learner_id": "units-test-001",
        "name": "Units Test Learner",
        "age": 10,
        "grade": 5,
        "learning_style": "read-write",
    }
    with runner.isolated_filesystem():
        learner_file = "learner.json"
        with open(learner_file, "w") as fh:
            json.dump(learner_data, fh)
        result = runner.invoke(
            main, ["path", "--learner", learner_file, "--subject", "math"]
        )

    assert result.exit_code == 0
    assert "units" in result.output.lower() or "Total" in result.output


def test_cli_serve_help() -> None:
    """Serve command help should show port and host options."""
    runner = CliRunner()
    result = runner.invoke(main, ["serve", "--help"])
    assert result.exit_code == 0
    assert "port" in result.output.lower() or "host" in result.output.lower()
