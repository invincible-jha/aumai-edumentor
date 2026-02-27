"""Core logic for aumai-edumentor: content library, path generation, assessments."""

from __future__ import annotations

from .models import AssessmentResult, LearnerProfile, LearningContent, LearningPath

__all__ = ["ContentLibrary", "PathGenerator", "AssessmentEngine"]

# ---------------------------------------------------------------------------
# Built-in content library aligned with NCF 2023
# ---------------------------------------------------------------------------

_BUILTIN_CONTENT: list[dict[str, object]] = [
    # Mathematics
    {"content_id": "math-001", "subject": "math", "topic": "Counting and Numbers", "difficulty": "beginner", "content_type": "text", "content": "Numbers from 1 to 100. Learn to count forwards and backwards. Practice skip counting by 2s, 5s, and 10s.", "ncf_alignment": ["NCF-MATH-G1-NUM-1"], "grade_level": 1},
    {"content_id": "math-002", "subject": "math", "topic": "Addition and Subtraction", "difficulty": "beginner", "content_type": "activity", "content": "Use counting beads or stones to practise addition and subtraction within 20. Story problems using local contexts.", "ncf_alignment": ["NCF-MATH-G2-OPS-1"], "grade_level": 2},
    {"content_id": "math-003", "subject": "math", "topic": "Multiplication Tables", "difficulty": "beginner", "content_type": "text", "content": "Multiplication tables from 1 to 10. Visual array models. Repeated addition concept. Practice with rhymes and patterns.", "ncf_alignment": ["NCF-MATH-G3-MUL-1"], "grade_level": 3},
    {"content_id": "math-004", "subject": "math", "topic": "Fractions", "difficulty": "intermediate", "content_type": "text", "content": "Understanding fractions as parts of a whole. Equivalent fractions. Comparing fractions with same and different denominators. Real-life examples: sharing rotis, dividing land.", "ncf_alignment": ["NCF-MATH-G5-FRA-1"], "grade_level": 5},
    {"content_id": "math-005", "subject": "math", "topic": "Fractions Quiz", "difficulty": "intermediate", "content_type": "quiz", "content": '[{"q":"What is 1/2 + 1/4?","options":["1/2","3/4","2/6","1/6"],"answer":"3/4"},{"q":"Which is bigger: 2/3 or 3/4?","options":["2/3","3/4","Equal","Cannot tell"],"answer":"3/4"}]', "ncf_alignment": ["NCF-MATH-G5-FRA-2"], "grade_level": 5},
    {"content_id": "math-006", "subject": "math", "topic": "Algebra Introduction", "difficulty": "intermediate", "content_type": "text", "content": "Introduction to variables and simple equations. Solving x + 5 = 12. Writing word problems as equations.", "ncf_alignment": ["NCF-MATH-G7-ALG-1"], "grade_level": 7},
    {"content_id": "math-007", "subject": "math", "topic": "Geometry: Triangles", "difficulty": "intermediate", "content_type": "activity", "content": "Properties of triangles. Sum of angles = 180°. Types: equilateral, isosceles, scalene. Measure angles with protractor activity.", "ncf_alignment": ["NCF-MATH-G7-GEO-1"], "grade_level": 7},
    {"content_id": "math-008", "subject": "math", "topic": "Linear Equations", "difficulty": "advanced", "content_type": "text", "content": "Solving simultaneous linear equations by substitution and elimination. Real-world applications: mixtures, speed-distance-time.", "ncf_alignment": ["NCF-MATH-G9-ALG-2"], "grade_level": 9},
    {"content_id": "math-009", "subject": "math", "topic": "Quadratic Equations", "difficulty": "advanced", "content_type": "text", "content": "Solving ax²+bx+c=0 by factorisation and quadratic formula. Discriminant. Nature of roots.", "ncf_alignment": ["NCF-MATH-G10-ALG-3"], "grade_level": 10},
    {"content_id": "math-010", "subject": "math", "topic": "Statistics: Mean Median Mode", "difficulty": "intermediate", "content_type": "activity", "content": "Calculate mean, median, and mode from real data sets (e.g. rainfall, crop yields). Understand when to use each measure.", "ncf_alignment": ["NCF-MATH-G8-STAT-1"], "grade_level": 8},
    # Science
    {"content_id": "sci-001", "subject": "science", "topic": "Plants and Photosynthesis", "difficulty": "beginner", "content_type": "text", "content": "How plants make food using sunlight, water, and carbon dioxide. Chlorophyll. Leaf structure. Importance of plants in food chain.", "ncf_alignment": ["NCF-SCI-G5-BIO-1"], "grade_level": 5},
    {"content_id": "sci-002", "subject": "science", "topic": "Human Body Systems", "difficulty": "intermediate", "content_type": "text", "content": "Digestive, circulatory, and respiratory systems. Functions of major organs. Nutrition and health. Hygiene practices.", "ncf_alignment": ["NCF-SCI-G7-BIO-2"], "grade_level": 7},
    {"content_id": "sci-003", "subject": "science", "topic": "Electricity and Circuits", "difficulty": "intermediate", "content_type": "activity", "content": "Build a simple circuit with battery, wire, and bulb. Conductors and insulators. Series vs parallel circuits. Safety with electricity.", "ncf_alignment": ["NCF-SCI-G7-PHY-1"], "grade_level": 7},
    {"content_id": "sci-004", "subject": "science", "topic": "Atoms and Molecules", "difficulty": "advanced", "content_type": "text", "content": "Structure of atom: protons, neutrons, electrons. Valency. Chemical formulae. Balancing equations. Periodic table introduction.", "ncf_alignment": ["NCF-SCI-G9-CHE-1"], "grade_level": 9},
    {"content_id": "sci-005", "subject": "science", "topic": "Ecosystems", "difficulty": "intermediate", "content_type": "text", "content": "Food chains and food webs. Producers, consumers, decomposers. Biodiversity. Indian ecosystems: forests, wetlands, grasslands.", "ncf_alignment": ["NCF-SCI-G8-ENV-1"], "grade_level": 8},
    {"content_id": "sci-006", "subject": "science", "topic": "Heredity and Evolution", "difficulty": "advanced", "content_type": "text", "content": "Mendel's laws of inheritance. Dominant and recessive traits. DNA basics. Theory of evolution and natural selection.", "ncf_alignment": ["NCF-SCI-G10-BIO-3"], "grade_level": 10},
    # Hindi
    {"content_id": "hindi-001", "subject": "hindi", "topic": "Varnamala (Alphabet)", "difficulty": "beginner", "content_type": "text", "content": "Hindi alphabet: 11 swaras (vowels) and 35 vyanjanas (consonants). Devanagari script. Matras. Basic words.", "ncf_alignment": ["NCF-HINDI-G1-READ-1"], "grade_level": 1},
    {"content_id": "hindi-002", "subject": "hindi", "topic": "Reading Comprehension", "difficulty": "intermediate", "content_type": "text", "content": "Short stories and poems from Rimjhim textbook. Understanding main idea, characters, and moral. Answer in complete sentences.", "ncf_alignment": ["NCF-HINDI-G5-READ-2"], "grade_level": 5},
    {"content_id": "hindi-003", "subject": "hindi", "topic": "Essay Writing", "difficulty": "advanced", "content_type": "activity", "content": "Structure of a Hindi essay: Prastavan, Mukhya Bhag, Upasanhar. Practice topics: Mera Gaon, Paryavaran Pradushan, Swastha Jeevan.", "ncf_alignment": ["NCF-HINDI-G8-WRITE-1"], "grade_level": 8},
    # Social Studies / EVS
    {"content_id": "evs-001", "subject": "social_studies", "topic": "Our Neighbourhood", "difficulty": "beginner", "content_type": "activity", "content": "Map your school and home. Identify helpers in the community: farmers, teachers, doctors, postmen. Discuss their roles.", "ncf_alignment": ["NCF-EVS-G3-SOC-1"], "grade_level": 3},
    {"content_id": "evs-002", "subject": "social_studies", "topic": "Indian History: Ancient Civilisations", "difficulty": "intermediate", "content_type": "text", "content": "Indus Valley Civilisation: Harappa and Mohenjo-daro. Vedic period. Maurya Empire. Gupta Golden Age. Key contributions to science, mathematics, and art.", "ncf_alignment": ["NCF-SS-G6-HIST-1"], "grade_level": 6},
    {"content_id": "evs-003", "subject": "social_studies", "topic": "Indian Constitution and Democracy", "difficulty": "advanced", "content_type": "text", "content": "Fundamental Rights and Duties. Directive Principles. Structure of government: Legislature, Executive, Judiciary. Preamble and its significance.", "ncf_alignment": ["NCF-SS-G10-CIV-1"], "grade_level": 10},
    # English
    {"content_id": "eng-001", "subject": "english", "topic": "Basic Reading: Phonics", "difficulty": "beginner", "content_type": "activity", "content": "Letter sounds and blends. CVC words (cat, bat, mat). Short stories with illustrations. Oral reading practice.", "ncf_alignment": ["NCF-ENG-G1-READ-1"], "grade_level": 1},
    {"content_id": "eng-002", "subject": "english", "topic": "Grammar: Tenses", "difficulty": "intermediate", "content_type": "text", "content": "Simple present, past, and future tenses. Present and past continuous. Perfect tenses introduction. Common errors in Indian English.", "ncf_alignment": ["NCF-ENG-G6-GRAM-1"], "grade_level": 6},
    {"content_id": "eng-003", "subject": "english", "topic": "Letter Writing", "difficulty": "intermediate", "content_type": "activity", "content": "Formal and informal letter formats. Application for leave. Complaint letter. Invitation letter. Practice exercises with real contexts.", "ncf_alignment": ["NCF-ENG-G8-WRITE-1"], "grade_level": 8},
]


class ContentLibrary:
    """Stores and queries learning content aligned with NCF 2023."""

    def __init__(self) -> None:
        self._contents: list[LearningContent] = [
            LearningContent(**c) for c in _BUILTIN_CONTENT  # type: ignore[arg-type]
        ]

    def add(self, content: LearningContent) -> None:
        """Add a new learning content item to the library."""
        self._contents.append(content)

    def search(
        self,
        subject: str,
        difficulty: str | None = None,
        grade: int | None = None,
    ) -> list[LearningContent]:
        """Search content by subject with optional difficulty and grade filters."""
        results = [
            c for c in self._contents
            if c.subject.lower() == subject.lower()
        ]
        if difficulty:
            results = [c for c in results if c.difficulty == difficulty]
        if grade is not None:
            results = [c for c in results if c.grade_level == grade]
        return sorted(results, key=lambda c: (c.grade_level, c.difficulty))

    def all_subjects(self) -> list[str]:
        """Return unique subject names in the library."""
        return sorted({c.subject for c in self._contents})

    def all_content(self) -> list[LearningContent]:
        """Return all content in the library."""
        return list(self._contents)


# Difficulty ordering for path generation
_DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


class PathGenerator:
    """Generates personalised learning paths based on learner profile."""

    def __init__(self, library: ContentLibrary | None = None) -> None:
        self._library = library or ContentLibrary()

    def generate(self, learner: LearnerProfile, subject: str) -> LearningPath:
        """Generate a personalised learning path for a learner and subject."""
        # Get all content for the subject at the learner's grade level (+/- 1)
        all_content = self._library.search(subject)

        # Filter by grade range
        grade_range = range(max(1, learner.grade - 1), min(12, learner.grade + 2))
        grade_filtered = [c for c in all_content if c.grade_level in grade_range]

        if not grade_filtered:
            # Fallback: return all content for the subject
            grade_filtered = all_content

        # Determine starting difficulty based on weaknesses
        subject_lower = subject.lower()
        is_weak = subject_lower in [w.lower() for w in learner.weaknesses]
        starting_difficulty = "beginner" if is_weak else "intermediate"

        # Sort: start from appropriate difficulty, then ascending
        def sort_key(content: LearningContent) -> tuple[int, int]:
            diff_val = _DIFFICULTY_ORDER.get(content.difficulty, 1)
            target = _DIFFICULTY_ORDER.get(starting_difficulty, 1)
            return (abs(diff_val - target), content.grade_level)

        grade_filtered.sort(key=sort_key)

        # Prefer content matching learner style
        style_pref: dict[str, str] = {
            "visual": "activity",
            "auditory": "text",
            "kinesthetic": "activity",
            "read-write": "text",
        }
        preferred_type = style_pref.get(learner.learning_style, "text")
        preferred = [c for c in grade_filtered if c.content_type == preferred_type]
        others = [c for c in grade_filtered if c.content_type != preferred_type]

        # Mix: preferred first, then others, deduplicated
        seen_ids: set[str] = set()
        sequence: list[LearningContent] = []
        for item in preferred + others:
            if item.content_id not in seen_ids:
                seen_ids.add(item.content_id)
                sequence.append(item)

        return LearningPath(
            learner=learner,
            content_sequence=sequence,
            progress_pct=0.0,
        )


class AssessmentEngine:
    """Evaluates learner answers and generates assessment results."""

    def evaluate(
        self, learner_id: str, subject: str, answers: list[dict[str, object]]
    ) -> AssessmentResult:
        """Evaluate a list of answer objects and return an AssessmentResult.

        Each answer dict should have: question_id, correct (bool), topic (str).
        """
        if not answers:
            return AssessmentResult(
                learner_id=learner_id,
                subject=subject,
                score=0.0,
                areas_to_improve=["No answers provided — please attempt the assessment."],
            )

        def _is_correct(value: object) -> bool:
            """Evaluate a correct flag that may be a bool or a string representation.

            Handles the case where JSON deserialisation yields the string "false"
            instead of the boolean False — bool("false") is True in Python, which
            would incorrectly count wrong answers as correct.
            """
            if isinstance(value, str):
                return value.strip().lower() not in ("false", "0", "no", "")
            return bool(value)

        correct_count = sum(1 for a in answers if _is_correct(a.get("correct", False)))
        score = round(correct_count / len(answers) * 100, 1)

        # Identify topics with wrong answers
        incorrect_topics: list[str] = []
        for answer in answers:
            if not _is_correct(answer.get("correct", False)):
                topic = str(answer.get("topic", subject))
                if topic not in incorrect_topics:
                    incorrect_topics.append(topic)

        areas_to_improve = incorrect_topics if incorrect_topics else []
        if score < 40:
            areas_to_improve.append(f"Fundamental concepts in {subject}")
        if not areas_to_improve:
            areas_to_improve = ["Continue to advanced topics — excellent performance!"]

        return AssessmentResult(
            learner_id=learner_id,
            subject=subject,
            score=score,
            areas_to_improve=areas_to_improve,
        )
