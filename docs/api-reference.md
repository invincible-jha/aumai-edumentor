# API Reference — aumai-edumentor

> **Educational Disclaimer:** This tool is an educational aid. Always verify
> recommendations with qualified educators and follow local curriculum guidelines.

Package: `aumai_edumentor` | Version: 0.1.0 | Python: 3.11+

---

## Module: `aumai_edumentor.models`

All models use Pydantic v2. Validation is enforced at construction time.

---

### `LearnerProfile`

Profile of a learner for personalised path generation.

```python
class LearnerProfile(BaseModel):
    learner_id: str
    name: str
    age: int
    grade: int
    language: str = "en"
    strengths: list[str] = []
    weaknesses: list[str] = []
    learning_style: str = "visual"
```

**Fields:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `learner_id` | `str` | Yes | — | Unique learner identifier |
| `name` | `str` | Yes | — | Learner's full name |
| `age` | `int` | Yes | 4 <= age <= 25 | Age in years |
| `grade` | `int` | Yes | 1 <= grade <= 12 | Current grade (India: Class 1–12) |
| `language` | `str` | No | default `"en"` | Preferred language code (IETF) |
| `strengths` | `list[str]` | No | default `[]` | Subjects the learner excels in |
| `weaknesses` | `list[str]` | No | default `[]` | Subjects needing improvement |
| `learning_style` | `str` | No | see below | Preferred learning modality |

Valid `learning_style` values: `"visual"`, `"auditory"`, `"kinesthetic"`, `"read-write"`.

**Raises:** `pydantic.ValidationError` if any constraint is violated.

**Example:**

```python
from aumai_edumentor.models import LearnerProfile

learner = LearnerProfile(
    learner_id="L001",
    name="Arjun",
    age=10,
    grade=5,
    weaknesses=["math"],
    learning_style="kinesthetic",
)
```

---

### `LearningContent`

A single unit of learning content aligned with NCF 2023.

```python
class LearningContent(BaseModel):
    content_id: str
    subject: str
    topic: str
    difficulty: str
    content_type: str
    content: str
    ncf_alignment: list[str] = []
    grade_level: int = 5
```

**Fields:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `content_id` | `str` | Yes | — | Unique identifier for this content unit |
| `subject` | `str` | Yes | — | Subject name (e.g. `"math"`, `"science"`) |
| `topic` | `str` | Yes | — | Specific topic within the subject |
| `difficulty` | `str` | Yes | see below | Difficulty level |
| `content_type` | `str` | Yes | see below | Content format |
| `content` | `str` | Yes | — | Full content text, quiz JSON string, or activity description |
| `ncf_alignment` | `list[str]` | No | default `[]` | NCF 2023 competency codes |
| `grade_level` | `int` | No | 1 <= grade_level <= 12, default `5` | Target grade level |

Valid `difficulty` values: `"beginner"`, `"intermediate"`, `"advanced"`.

Valid `content_type` values: `"text"`, `"quiz"`, `"activity"`.

**Raises:** `pydantic.ValidationError` if pattern constraints are violated.

---

### `LearningPath`

A personalised sequence of learning content for a learner.

```python
class LearningPath(BaseModel):
    learner: LearnerProfile
    content_sequence: list[LearningContent]
    progress_pct: float = 0.0
```

**Fields:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `learner` | `LearnerProfile` | Yes | — | The learner this path belongs to |
| `content_sequence` | `list[LearningContent]` | Yes | — | Ordered content units |
| `progress_pct` | `float` | No | 0.0 <= value <= 100.0, default `0.0` | Completion percentage |

`LearningPath` objects are returned by `PathGenerator.generate`. They are not typically
constructed directly.

---

### `AssessmentResult`

Result of a learning assessment for a learner.

```python
class AssessmentResult(BaseModel):
    learner_id: str
    subject: str
    score: float
    areas_to_improve: list[str]
```

**Fields:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `learner_id` | `str` | Yes | — | Learner identifier |
| `subject` | `str` | Yes | — | Subject assessed |
| `score` | `float` | Yes | 0.0 <= score <= 100.0 | Score as a percentage |
| `areas_to_improve` | `list[str]` | Yes | — | Topics or skills needing improvement |

Special messages in `areas_to_improve`:
- If no answers provided: `["No answers provided — please attempt the assessment."]`
- If score < 40%: includes `"Fundamental concepts in {subject}"`
- If all answers correct: `["Continue to advanced topics — excellent performance!"]`

---

## Module: `aumai_edumentor.core`

---

### `ContentLibrary`

Stores and queries learning content aligned with NCF 2023.

```python
class ContentLibrary:
    def __init__(self) -> None: ...
```

Initialises with 25 built-in content units across five subjects and ten grade levels.

**Methods:**

#### `add`

```python
def add(self, content: LearningContent) -> None
```

Add a new learning content item to the library.

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `LearningContent` | Content unit to add |

Returns: `None`. Does not check for duplicate `content_id`.

---

#### `search`

```python
def search(
    self,
    subject: str,
    difficulty: str | None = None,
    grade: int | None = None,
) -> list[LearningContent]
```

Search content by subject with optional difficulty and grade filters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `subject` | `str` | Subject name — case-insensitive match |
| `difficulty` | `str | None` | If provided, filters to this difficulty level |
| `grade` | `int | None` | If provided, filters to this exact grade level |

Returns: `list[LearningContent]` sorted by `(grade_level, difficulty)` ascending.

Returns an empty list if no content matches.

---

#### `all_subjects`

```python
def all_subjects(self) -> list[str]
```

Return unique subject names in the library, sorted alphabetically.

Returns: `list[str]`

---

#### `all_content`

```python
def all_content(self) -> list[LearningContent]
```

Return all content in the library (built-in plus any added via `add`).

Returns: `list[LearningContent]` (copy — not the internal list).

---

### `PathGenerator`

Generates personalised learning paths based on a learner profile.

```python
class PathGenerator:
    def __init__(self, library: ContentLibrary | None = None) -> None: ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `library` | `ContentLibrary | None` | Content library to use. If `None`, creates a default `ContentLibrary`. |

**Methods:**

#### `generate`

```python
def generate(self, learner: LearnerProfile, subject: str) -> LearningPath
```

Generate a personalised learning path for a learner and subject.

| Parameter | Type | Description |
|-----------|------|-------------|
| `learner` | `LearnerProfile` | The learner to generate a path for |
| `subject` | `str` | Subject name — matched case-insensitively against `LearningContent.subject` |

Returns: `LearningPath` with `progress_pct=0.0`.

**Algorithm:**
1. Retrieve all content for the subject.
2. Filter to grade range `[learner.grade - 1, learner.grade + 1]` (clamped to 1–12). Falls back to all subject content if range is empty.
3. Determine starting difficulty: `"beginner"` if subject is in `learner.weaknesses`, else `"intermediate"`.
4. Sort by `(abs(difficulty_value - target_difficulty_value), grade_level)`.
5. Partition: preferred content type first (visual/kinesthetic → `"activity"`; auditory/read-write → `"text"`), then others. Deduplication by `content_id`.

**Raises:** Does not raise. Returns a `LearningPath` with an empty `content_sequence` if the subject has no content.

---

### `AssessmentEngine`

Evaluates learner answers and generates assessment results.

```python
class AssessmentEngine:
```

No constructor parameters.

**Methods:**

#### `evaluate`

```python
def evaluate(
    self,
    learner_id: str,
    subject: str,
    answers: list[dict[str, object]],
) -> AssessmentResult
```

Evaluate a list of answer objects and return an `AssessmentResult`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `learner_id` | `str` | Learner identifier (stored in result) |
| `subject` | `str` | Subject being assessed |
| `answers` | `list[dict[str, object]]` | List of answer dictionaries |

Each `dict` in `answers` should contain:

| Key | Type | Description |
|-----|------|-------------|
| `question_id` | `str` | Arbitrary identifier |
| `correct` | `bool` or `str` | Whether the answer was correct |
| `topic` | `str` | Topic the question tests |

Returns: `AssessmentResult`

**Correctness handling:** The `correct` field is evaluated by an internal `_is_correct`
helper. Values treated as falsy: `False`, `0`, `"false"`, `"0"`, `"no"`, `""`.
All other values (including `True`, non-empty strings, non-zero numbers) are treated as
truthy. This prevents `bool("false") == True` bugs from JSON deserialisation.

**Edge case — empty answers:**

```python
result = engine.evaluate("L001", "math", [])
# result.score == 0.0
# result.areas_to_improve == ["No answers provided — please attempt the assessment."]
```

---

## Module: `aumai_edumentor.cli`

CLI entry point. Access via the `aumai-edumentor` shell command.

```python
@click.group()
def main() -> None: ...
```

### Commands

| Command | Description |
|---------|-------------|
| `subjects` | List all subjects and unit counts |
| `path` | Generate a personalised learning path |
| `assess` | Evaluate learner answers |
| `serve` | Start the API server |

All commands support `--help` for option documentation.

#### `EDUCATIONAL_DISCLAIMER`

```python
EDUCATIONAL_DISCLAIMER: str
```

Module-level constant printed by the `serve` command on startup.

Value: `"This tool provides AI-assisted educational recommendations only. Learning plans
should be reviewed by qualified educators. This tool does not replace professional
pedagogical assessment."`

---

## Built-in Content Library — Subject Coverage

| Subject | Content IDs | Grade range | Topics |
|---------|-------------|-------------|--------|
| `math` | `math-001` to `math-010` | 1–10 | Counting, Addition/Subtraction, Multiplication, Fractions (×2 inc. quiz), Algebra Intro, Geometry: Triangles, Linear Equations, Quadratic Equations, Statistics |
| `science` | `sci-001` to `sci-006` | 5–10 | Photosynthesis, Human Body Systems, Circuits, Atoms/Molecules, Ecosystems, Heredity/Evolution |
| `hindi` | `hindi-001` to `hindi-003` | 1–8 | Varnamala, Reading Comprehension, Essay Writing |
| `english` | `eng-001` to `eng-003` | 1–8 | Phonics, Grammar/Tenses, Letter Writing |
| `social_studies` | `evs-001` to `evs-003` | 3–10 | Neighbourhood, Ancient Civilisations, Constitution/Democracy |

---

## NCF Alignment Code Format

```
NCF-<SUBJECT>-G<GRADE>-<DOMAIN>-<INDEX>
```

| Token | Example | Description |
|-------|---------|-------------|
| `SUBJECT` | `MATH`, `SCI`, `HINDI`, `ENG`, `EVS`, `SS` | Subject abbreviation |
| `GRADE` | `G5` | Target grade level |
| `DOMAIN` | `FRA`, `OPS`, `BIO`, `READ`, `HIST` | Learning domain |
| `INDEX` | `1`, `2`, `3` | Sequential index within domain |

Examples: `NCF-MATH-G5-FRA-1`, `NCF-SCI-G7-PHY-1`, `NCF-HINDI-G8-WRITE-1`.

---

## Type Aliases and Constants

```python
# Difficulty ordering used by PathGenerator
_DIFFICULTY_ORDER: dict[str, int] = {
    "beginner": 0,
    "intermediate": 1,
    "advanced": 2,
}

# Learning style to preferred content type mapping
_STYLE_PREF: dict[str, str] = {
    "visual": "activity",
    "auditory": "text",
    "kinesthetic": "activity",
    "read-write": "text",
}
```

---

## Exceptions

aumai-edumentor does not define custom exception classes. Errors surface as:

| Situation | Exception |
|-----------|-----------|
| Invalid `LearnerProfile` fields | `pydantic.ValidationError` |
| Invalid `LearningContent` fields | `pydantic.ValidationError` |
| File not found (CLI) | Click exits with error message |
| Invalid JSON (CLI) | `json.JSONDecodeError` |
| Missing `uvicorn` for `serve` | `SystemExit(1)` with error message |

---

## Public API Surface (`__all__`)

### `aumai_edumentor.models`

```python
__all__ = [
    "LearnerProfile",
    "LearningContent",
    "LearningPath",
    "AssessmentResult",
]
```

### `aumai_edumentor.core`

```python
__all__ = ["ContentLibrary", "PathGenerator", "AssessmentEngine"]
```
