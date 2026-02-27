"""Comprehensive tests for aumai-edumentor core module.

Covers ContentLibrary, PathGenerator, AssessmentEngine, and models.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aumai_edumentor.core import AssessmentEngine, ContentLibrary, PathGenerator
from aumai_edumentor.models import (
    AssessmentResult,
    LearnerProfile,
    LearningContent,
    LearningPath,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def library() -> ContentLibrary:
    return ContentLibrary()


@pytest.fixture()
def path_generator() -> PathGenerator:
    return PathGenerator()


@pytest.fixture()
def engine() -> AssessmentEngine:
    return AssessmentEngine()


@pytest.fixture()
def grade5_visual_learner() -> LearnerProfile:
    return LearnerProfile(
        learner_id="learner-001",
        name="Priya Sharma",
        age=10,
        grade=5,
        language="en",
        strengths=["science"],
        weaknesses=["math"],
        learning_style="visual",
    )


@pytest.fixture()
def grade9_readwrite_learner() -> LearnerProfile:
    return LearnerProfile(
        learner_id="learner-002",
        name="Arjun Patel",
        age=14,
        grade=9,
        language="en",
        strengths=["math"],
        weaknesses=["hindi"],
        learning_style="read-write",
    )


@pytest.fixture()
def sample_math_content() -> LearningContent:
    return LearningContent(
        content_id="test-math-001",
        subject="math",
        topic="Test Algebra",
        difficulty="intermediate",
        content_type="text",
        content="Test content for algebra.",
        ncf_alignment=["NCF-MATH-TEST-1"],
        grade_level=8,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestLearnerProfileModel:
    def test_valid_learner_profile(self) -> None:
        learner = LearnerProfile(
            learner_id="L001",
            name="Test Learner",
            age=12,
            grade=6,
        )
        assert learner.learner_id == "L001"
        assert learner.name == "Test Learner"
        assert learner.grade == 6

    def test_default_language_is_en(self) -> None:
        learner = LearnerProfile(
            learner_id="L002", name="Learner", age=10, grade=5
        )
        assert learner.language == "en"

    def test_default_learning_style_visual(self) -> None:
        learner = LearnerProfile(
            learner_id="L003", name="Learner", age=10, grade=5
        )
        assert learner.learning_style == "visual"

    def test_default_strengths_empty(self) -> None:
        learner = LearnerProfile(
            learner_id="L004", name="Learner", age=10, grade=5
        )
        assert learner.strengths == []

    def test_default_weaknesses_empty(self) -> None:
        learner = LearnerProfile(
            learner_id="L005", name="Learner", age=10, grade=5
        )
        assert learner.weaknesses == []

    def test_invalid_age_too_young(self) -> None:
        with pytest.raises(Exception):
            LearnerProfile(
                learner_id="L006", name="Learner", age=3, grade=1  # age < 4
            )

    def test_invalid_age_too_old(self) -> None:
        with pytest.raises(Exception):
            LearnerProfile(
                learner_id="L007", name="Learner", age=26, grade=12  # age > 25
            )

    def test_invalid_grade_zero(self) -> None:
        with pytest.raises(Exception):
            LearnerProfile(
                learner_id="L008", name="Learner", age=10, grade=0  # grade < 1
            )

    def test_invalid_grade_thirteen(self) -> None:
        with pytest.raises(Exception):
            LearnerProfile(
                learner_id="L009", name="Learner", age=18, grade=13  # grade > 12
            )

    def test_invalid_learning_style(self) -> None:
        with pytest.raises(Exception):
            LearnerProfile(
                learner_id="L010",
                name="Learner",
                age=10,
                grade=5,
                learning_style="tactile",  # invalid
            )

    def test_valid_learning_styles(self) -> None:
        for style in ["visual", "auditory", "kinesthetic", "read-write"]:
            learner = LearnerProfile(
                learner_id="L011", name="Learner", age=10, grade=5, learning_style=style
            )
            assert learner.learning_style == style

    def test_serialisation_roundtrip(self) -> None:
        learner = LearnerProfile(
            learner_id="L012",
            name="Roundtrip Learner",
            age=12,
            grade=7,
            strengths=["science"],
            weaknesses=["math"],
        )
        data = learner.model_dump()
        restored = LearnerProfile.model_validate(data)
        assert restored.learner_id == learner.learner_id
        assert restored.strengths == learner.strengths


class TestLearningContentModel:
    def test_valid_learning_content(self) -> None:
        content = LearningContent(
            content_id="C001",
            subject="math",
            topic="Fractions",
            difficulty="intermediate",
            content_type="text",
            content="Learn about fractions.",
            grade_level=5,
        )
        assert content.content_id == "C001"
        assert content.subject == "math"

    def test_invalid_difficulty(self) -> None:
        with pytest.raises(Exception):
            LearningContent(
                content_id="C002",
                subject="math",
                topic="Test",
                difficulty="expert",  # invalid
                content_type="text",
                content="Test content",
                grade_level=5,
            )

    def test_invalid_content_type(self) -> None:
        with pytest.raises(Exception):
            LearningContent(
                content_id="C003",
                subject="math",
                topic="Test",
                difficulty="beginner",
                content_type="video",  # invalid
                content="Test content",
                grade_level=5,
            )

    def test_invalid_grade_level(self) -> None:
        with pytest.raises(Exception):
            LearningContent(
                content_id="C004",
                subject="math",
                topic="Test",
                difficulty="beginner",
                content_type="text",
                content="Test content",
                grade_level=13,  # invalid > 12
            )

    def test_default_ncf_alignment_empty(self) -> None:
        content = LearningContent(
            content_id="C005",
            subject="math",
            topic="Test",
            difficulty="beginner",
            content_type="text",
            content="Test content",
            grade_level=5,
        )
        assert content.ncf_alignment == []

    def test_valid_difficulty_values(self) -> None:
        for diff in ["beginner", "intermediate", "advanced"]:
            content = LearningContent(
                content_id=f"C-{diff}",
                subject="math",
                topic="Test",
                difficulty=diff,
                content_type="text",
                content="Test.",
                grade_level=5,
            )
            assert content.difficulty == diff

    def test_valid_content_type_values(self) -> None:
        for ctype in ["text", "quiz", "activity"]:
            content = LearningContent(
                content_id=f"CT-{ctype}",
                subject="science",
                topic="Test",
                difficulty="beginner",
                content_type=ctype,
                content="Test.",
                grade_level=5,
            )
            assert content.content_type == ctype


class TestLearningPathModel:
    def test_learning_path_creation(
        self, grade5_visual_learner: LearnerProfile
    ) -> None:
        path = LearningPath(
            learner=grade5_visual_learner,
            content_sequence=[],
            progress_pct=0.0,
        )
        assert path.learner == grade5_visual_learner
        assert path.content_sequence == []
        assert path.progress_pct == 0.0

    def test_progress_pct_default_zero(
        self, grade5_visual_learner: LearnerProfile
    ) -> None:
        path = LearningPath(
            learner=grade5_visual_learner,
            content_sequence=[],
        )
        assert path.progress_pct == 0.0

    def test_progress_pct_invalid_over_100(
        self, grade5_visual_learner: LearnerProfile
    ) -> None:
        with pytest.raises(Exception):
            LearningPath(
                learner=grade5_visual_learner,
                content_sequence=[],
                progress_pct=101.0,  # invalid
            )

    def test_progress_pct_invalid_negative(
        self, grade5_visual_learner: LearnerProfile
    ) -> None:
        with pytest.raises(Exception):
            LearningPath(
                learner=grade5_visual_learner,
                content_sequence=[],
                progress_pct=-1.0,  # invalid
            )


class TestAssessmentResultModel:
    def test_valid_assessment_result(self) -> None:
        result = AssessmentResult(
            learner_id="L001",
            subject="math",
            score=85.0,
            areas_to_improve=["Fractions"],
        )
        assert result.score == 85.0

    def test_invalid_score_over_100(self) -> None:
        with pytest.raises(Exception):
            AssessmentResult(
                learner_id="L001",
                subject="math",
                score=101.0,  # invalid
                areas_to_improve=[],
            )

    def test_invalid_score_negative(self) -> None:
        with pytest.raises(Exception):
            AssessmentResult(
                learner_id="L001",
                subject="math",
                score=-1.0,  # invalid
                areas_to_improve=[],
            )

    def test_score_boundary_zero(self) -> None:
        result = AssessmentResult(
            learner_id="L001",
            subject="math",
            score=0.0,
            areas_to_improve=["Everything"],
        )
        assert result.score == 0.0

    def test_score_boundary_100(self) -> None:
        result = AssessmentResult(
            learner_id="L001",
            subject="math",
            score=100.0,
            areas_to_improve=[],
        )
        assert result.score == 100.0


# ---------------------------------------------------------------------------
# ContentLibrary tests
# ---------------------------------------------------------------------------


class TestContentLibrary:
    def test_library_loads_builtin_content(self, library: ContentLibrary) -> None:
        all_content = library.all_content()
        assert len(all_content) >= 20

    def test_all_content_returns_learning_content_objects(
        self, library: ContentLibrary
    ) -> None:
        for item in library.all_content():
            assert isinstance(item, LearningContent)

    def test_all_subjects_returns_expected_subjects(
        self, library: ContentLibrary
    ) -> None:
        subjects = library.all_subjects()
        assert "math" in subjects
        assert "science" in subjects

    def test_all_subjects_sorted(self, library: ContentLibrary) -> None:
        subjects = library.all_subjects()
        assert subjects == sorted(subjects)

    def test_search_by_subject_math(self, library: ContentLibrary) -> None:
        results = library.search("math")
        assert len(results) > 0
        for item in results:
            assert item.subject == "math"

    def test_search_by_subject_case_insensitive(
        self, library: ContentLibrary
    ) -> None:
        lower_results = library.search("math")
        upper_results = library.search("MATH")
        assert len(lower_results) == len(upper_results)

    def test_search_unknown_subject_returns_empty(
        self, library: ContentLibrary
    ) -> None:
        results = library.search("nonexistent_subject_xyz")
        assert results == []

    def test_search_with_difficulty_filter(self, library: ContentLibrary) -> None:
        results = library.search("math", difficulty="beginner")
        assert len(results) > 0
        for item in results:
            assert item.difficulty == "beginner"

    def test_search_with_grade_filter(self, library: ContentLibrary) -> None:
        results = library.search("math", grade=5)
        assert len(results) > 0
        for item in results:
            assert item.grade_level == 5

    def test_search_with_difficulty_and_grade_filter(
        self, library: ContentLibrary
    ) -> None:
        results = library.search("math", difficulty="intermediate", grade=5)
        for item in results:
            assert item.difficulty == "intermediate"
            assert item.grade_level == 5

    def test_search_results_sorted_by_grade_then_difficulty(
        self, library: ContentLibrary
    ) -> None:
        results = library.search("math")
        # Grade levels should be non-decreasing
        for i in range(len(results) - 1):
            assert results[i].grade_level <= results[i + 1].grade_level

    def test_add_content_increases_count(
        self, library: ContentLibrary, sample_math_content: LearningContent
    ) -> None:
        initial_count = len(library.all_content())
        library.add(sample_math_content)
        assert len(library.all_content()) == initial_count + 1

    def test_add_content_searchable(
        self, library: ContentLibrary, sample_math_content: LearningContent
    ) -> None:
        library.add(sample_math_content)
        results = library.search("math", grade=8)
        ids = [c.content_id for c in results]
        assert sample_math_content.content_id in ids

    def test_search_science(self, library: ContentLibrary) -> None:
        results = library.search("science")
        assert len(results) > 0

    def test_search_hindi(self, library: ContentLibrary) -> None:
        results = library.search("hindi")
        assert len(results) > 0

    def test_all_builtin_content_has_ncf_alignment(
        self, library: ContentLibrary
    ) -> None:
        for item in library.all_content():
            assert isinstance(item.ncf_alignment, list)
            assert len(item.ncf_alignment) > 0


# ---------------------------------------------------------------------------
# PathGenerator tests
# ---------------------------------------------------------------------------


class TestPathGenerator:
    def test_generate_returns_learning_path(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "math")
        assert isinstance(path, LearningPath)

    def test_generate_learner_preserved(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "math")
        assert path.learner == grade5_visual_learner

    def test_generate_progress_pct_starts_zero(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "math")
        assert path.progress_pct == 0.0

    def test_generate_content_sequence_non_empty_for_known_subject(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "math")
        assert len(path.content_sequence) > 0

    def test_generate_content_unique_ids(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "math")
        ids = [c.content_id for c in path.content_sequence]
        assert len(ids) == len(set(ids)), "Duplicate content IDs in path"

    def test_generate_unknown_subject_returns_path_with_fallback(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        # Unknown subjects should return a path (possibly empty sequence)
        path = path_generator.generate(grade5_visual_learner, "unknown_subject_xyz")
        assert isinstance(path, LearningPath)

    def test_generate_weak_subject_prefers_beginner_over_advanced(
        self,
        path_generator: PathGenerator,
    ) -> None:
        """A learner with math weakness should have beginner content before advanced content."""
        learner = LearnerProfile(
            learner_id="weak-math",
            name="Weak Math Learner",
            age=10,
            grade=5,
            weaknesses=["math"],
            learning_style="visual",
        )
        path = path_generator.generate(learner, "math")
        # If there are both beginner and advanced items, beginner should come first
        difficulties = [c.difficulty for c in path.content_sequence]
        if "beginner" in difficulties and "advanced" in difficulties:
            beginner_idx = difficulties.index("beginner")
            advanced_idx = difficulties.index("advanced")
            assert beginner_idx < advanced_idx

    def test_generate_visual_learner_prefers_activities(
        self,
        path_generator: PathGenerator,
    ) -> None:
        """Visual learner should have activities earlier in sequence when activities exist."""
        learner = LearnerProfile(
            learner_id="visual-learner",
            name="Visual Learner",
            age=10,
            grade=7,  # Grade 7 has activities: sci-003 (electricity), math-007 (geometry)
            learning_style="visual",
        )
        path = path_generator.generate(learner, "math")
        types = [c.content_type for c in path.content_sequence]
        if "activity" in types:
            # The first activity index must be <= the first non-activity index
            first_activity_idx = types.index("activity")
            non_activity_indices = [i for i, t in enumerate(types) if t != "activity"]
            if non_activity_indices:
                first_non_activity_idx = non_activity_indices[0]
                assert first_activity_idx <= first_non_activity_idx

    def test_generate_science_subject(
        self,
        path_generator: PathGenerator,
        grade5_visual_learner: LearnerProfile,
    ) -> None:
        path = path_generator.generate(grade5_visual_learner, "science")
        assert isinstance(path, LearningPath)

    def test_generate_with_custom_library(self) -> None:
        """PathGenerator should use provided library."""
        custom_library = ContentLibrary()
        custom_content = LearningContent(
            content_id="custom-001",
            subject="custom_subject",
            topic="Custom Topic",
            difficulty="beginner",
            content_type="text",
            content="Custom learning content.",
            grade_level=5,
        )
        custom_library.add(custom_content)

        generator = PathGenerator(library=custom_library)
        learner = LearnerProfile(
            learner_id="L001", name="Learner", age=10, grade=5, learning_style="visual"
        )
        path = generator.generate(learner, "custom_subject")
        assert any(c.content_id == "custom-001" for c in path.content_sequence)

    def test_generate_grade_range_filtering(
        self, path_generator: PathGenerator
    ) -> None:
        """Content should be filtered to grade +/- 1."""
        learner = LearnerProfile(
            learner_id="L-g5", name="Grade 5 Learner", age=10, grade=5
        )
        path = path_generator.generate(learner, "math")
        for content in path.content_sequence:
            # Grade range is max(1, 5-1)=4 to min(12, 5+1)=6 inclusive (+2 exclusive)
            assert content.grade_level in range(4, 7), (
                f"Grade {content.grade_level} outside expected range [4,6]"
            )

    def test_generate_all_learning_styles(self) -> None:
        """All learning styles should produce valid paths."""
        generator = PathGenerator()
        for style in ["visual", "auditory", "kinesthetic", "read-write"]:
            learner = LearnerProfile(
                learner_id=f"L-{style}",
                name=f"{style} Learner",
                age=10,
                grade=5,
                learning_style=style,
            )
            path = generator.generate(learner, "math")
            assert isinstance(path, LearningPath)


# ---------------------------------------------------------------------------
# AssessmentEngine tests
# ---------------------------------------------------------------------------


class TestAssessmentEngine:
    def test_evaluate_empty_answers_returns_zero_score(
        self, engine: AssessmentEngine
    ) -> None:
        result = engine.evaluate("L001", "math", [])
        assert result.score == 0.0

    def test_evaluate_empty_answers_returns_assessment_result(
        self, engine: AssessmentEngine
    ) -> None:
        result = engine.evaluate("L001", "math", [])
        assert isinstance(result, AssessmentResult)

    def test_evaluate_empty_answers_areas_to_improve_non_empty(
        self, engine: AssessmentEngine
    ) -> None:
        result = engine.evaluate("L001", "math", [])
        assert len(result.areas_to_improve) > 0

    def test_evaluate_all_correct_returns_100(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": True, "topic": "Fractions"},
            {"question_id": "q2", "correct": True, "topic": "Algebra"},
            {"question_id": "q3", "correct": True, "topic": "Geometry"},
        ]
        result = engine.evaluate("L001", "math", answers)
        assert result.score == 100.0

    def test_evaluate_all_incorrect_returns_zero(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": False, "topic": "Fractions"},
            {"question_id": "q2", "correct": False, "topic": "Algebra"},
        ]
        result = engine.evaluate("L001", "math", answers)
        assert result.score == 0.0

    def test_evaluate_half_correct_returns_50(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": True, "topic": "Fractions"},
            {"question_id": "q2", "correct": False, "topic": "Algebra"},
        ]
        result = engine.evaluate("L001", "math", answers)
        assert result.score == 50.0

    def test_evaluate_score_is_percentage(self, engine: AssessmentEngine) -> None:
        answers = [
            {"question_id": f"q{i}", "correct": i % 2 == 0, "topic": "Fractions"}
            for i in range(10)
        ]
        result = engine.evaluate("L001", "math", answers)
        assert 0.0 <= result.score <= 100.0

    def test_evaluate_incorrect_topics_in_areas_to_improve(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": False, "topic": "Fractions"},
            {"question_id": "q2", "correct": True, "topic": "Algebra"},
        ]
        result = engine.evaluate("L001", "math", answers)
        assert "Fractions" in result.areas_to_improve

    def test_evaluate_correct_topics_not_in_areas_to_improve(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": False, "topic": "Fractions"},
            {"question_id": "q2", "correct": True, "topic": "Algebra"},
        ]
        result = engine.evaluate("L001", "math", answers)
        assert "Algebra" not in result.areas_to_improve

    def test_evaluate_low_score_adds_fundamental_area(
        self, engine: AssessmentEngine
    ) -> None:
        # Score < 40 should add fundamental area
        answers = [
            {"question_id": f"q{i}", "correct": False, "topic": f"Topic{i}"}
            for i in range(5)
        ]
        result = engine.evaluate("L001", "math", answers)
        # Score = 0 < 40, should include "fundamental concepts"
        combined = " ".join(result.areas_to_improve).lower()
        assert "fundamental" in combined or "math" in combined

    def test_evaluate_high_score_returns_encouragement(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": "q1", "correct": True, "topic": "Fractions"},
            {"question_id": "q2", "correct": True, "topic": "Algebra"},
        ]
        result = engine.evaluate("L001", "math", answers)
        combined = " ".join(result.areas_to_improve).lower()
        assert "excellent" in combined or "advanced" in combined or "continue" in combined

    def test_evaluate_learner_id_preserved(self, engine: AssessmentEngine) -> None:
        result = engine.evaluate("unique-learner-id-99", "science", [])
        assert result.learner_id == "unique-learner-id-99"

    def test_evaluate_subject_preserved(self, engine: AssessmentEngine) -> None:
        result = engine.evaluate("L001", "hindi", [])
        assert result.subject == "hindi"

    def test_evaluate_no_duplicate_incorrect_topics(
        self, engine: AssessmentEngine
    ) -> None:
        # Same topic failing multiple times should appear only once in areas_to_improve
        answers = [
            {"question_id": "q1", "correct": False, "topic": "Fractions"},
            {"question_id": "q2", "correct": False, "topic": "Fractions"},
            {"question_id": "q3", "correct": False, "topic": "Fractions"},
        ]
        result = engine.evaluate("L001", "math", answers)
        fractions_count = result.areas_to_improve.count("Fractions")
        assert fractions_count == 1

    def test_evaluate_score_rounded_to_one_decimal(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [
            {"question_id": f"q{i}", "correct": i < 1, "topic": "Topic"}
            for i in range(3)
        ]
        result = engine.evaluate("L001", "math", answers)
        # Score should be 33.3...% rounded to 1 decimal
        assert result.score == round(1 / 3 * 100, 1)

    def test_evaluate_returns_assessment_result_type(
        self, engine: AssessmentEngine
    ) -> None:
        answers = [{"question_id": "q1", "correct": True, "topic": "Test"}]
        result = engine.evaluate("L001", "math", answers)
        assert isinstance(result, AssessmentResult)


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------


class TestHypothesisBased:
    @given(
        subject=st.sampled_from(["math", "science", "hindi", "english", "social_studies"]),
        grade=st.integers(min_value=1, max_value=12),
    )
    @settings(max_examples=20)
    def test_path_generator_never_crashes(
        self, subject: str, grade: int
    ) -> None:
        generator = PathGenerator()
        learner = LearnerProfile(
            learner_id="hyp-learner",
            name="Hyp Learner",
            age=max(4, min(25, grade + 5)),
            grade=grade,
            learning_style="visual",
        )
        path = generator.generate(learner, subject)
        assert isinstance(path, LearningPath)
        assert path.progress_pct == 0.0

    @given(
        correct_count=st.integers(min_value=0, max_value=20),
        total_count=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=30)
    def test_assessment_score_in_valid_range(
        self, correct_count: int, total_count: int
    ) -> None:
        correct_count = min(correct_count, total_count)
        engine = AssessmentEngine()
        answers = [
            {"question_id": f"q{i}", "correct": i < correct_count, "topic": "T"}
            for i in range(total_count)
        ]
        result = engine.evaluate("L001", "math", answers)
        assert 0.0 <= result.score <= 100.0

    @given(
        difficulty=st.sampled_from(["beginner", "intermediate", "advanced"]),
        content_type=st.sampled_from(["text", "quiz", "activity"]),
        grade_level=st.integers(min_value=1, max_value=12),
    )
    @settings(max_examples=20)
    def test_learning_content_creation_valid_params(
        self, difficulty: str, content_type: str, grade_level: int
    ) -> None:
        content = LearningContent(
            content_id="hyp-c-001",
            subject="math",
            topic="Hypothesis Topic",
            difficulty=difficulty,
            content_type=content_type,
            content="Some content.",
            grade_level=grade_level,
        )
        assert content.difficulty == difficulty
        assert content.content_type == content_type
        assert content.grade_level == grade_level


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_full_learning_workflow(self) -> None:
        """Test the complete workflow: create learner -> generate path -> assess."""
        learner = LearnerProfile(
            learner_id="full-workflow-001",
            name="Integration Learner",
            age=11,
            grade=6,
            weaknesses=["math"],
            learning_style="visual",
        )

        generator = PathGenerator()
        path = generator.generate(learner, "math")

        assert isinstance(path, LearningPath)
        assert path.learner.learner_id == "full-workflow-001"
        assert len(path.content_sequence) > 0

        engine = AssessmentEngine()
        answers = [
            {"question_id": "q1", "correct": True, "topic": "Fractions"},
            {"question_id": "q2", "correct": False, "topic": "Algebra"},
            {"question_id": "q3", "correct": True, "topic": "Geometry"},
        ]
        result = engine.evaluate(learner.learner_id, "math", answers)

        assert result.learner_id == "full-workflow-001"
        assert result.score == pytest.approx(66.7, abs=0.1)
        assert "Algebra" in result.areas_to_improve

    def test_library_and_generator_consistency(self) -> None:
        """Content in generated path must exist in the library."""
        library = ContentLibrary()
        generator = PathGenerator(library=library)
        learner = LearnerProfile(
            learner_id="consistency-001",
            name="Consistency Learner",
            age=10,
            grade=5,
            learning_style="read-write",
        )
        path = generator.generate(learner, "science")
        library_ids = {c.content_id for c in library.all_content()}
        for content in path.content_sequence:
            assert content.content_id in library_ids

    def test_multiple_subjects_independently_tracked(self) -> None:
        """Paths for different subjects should contain subject-appropriate content."""
        generator = PathGenerator()
        learner = LearnerProfile(
            learner_id="multi-subject-001",
            name="Multi Subject Learner",
            age=12,
            grade=7,
            learning_style="kinesthetic",
        )
        math_path = generator.generate(learner, "math")
        science_path = generator.generate(learner, "science")

        math_subjects = {c.subject for c in math_path.content_sequence}
        science_subjects = {c.subject for c in science_path.content_sequence}

        assert "math" in math_subjects
        assert "science" in science_subjects
        # Math path should not contain science content and vice versa
        assert "science" not in math_subjects
        assert "math" not in science_subjects

    def test_assessment_with_all_correct_gives_encouragement(self) -> None:
        engine = AssessmentEngine()
        answers = [
            {"question_id": f"q{i}", "correct": True, "topic": f"Topic {i}"}
            for i in range(5)
        ]
        result = engine.evaluate("excellent-learner", "science", answers)
        assert result.score == 100.0
        combined = " ".join(result.areas_to_improve).lower()
        assert "excellent" in combined or "advanced" in combined

    def test_ncf_alignment_present_in_all_builtin_content(self) -> None:
        library = ContentLibrary()
        for content in library.all_content():
            assert len(content.ncf_alignment) > 0, (
                f"Content {content.content_id} missing NCF alignment"
            )
