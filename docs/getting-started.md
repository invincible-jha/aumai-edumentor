# Getting Started with aumai-edumentor

> **Educational Disclaimer:** This tool is an educational aid. Always verify
> recommendations with qualified educators and follow local curriculum guidelines.
> This tool does not replace professional pedagogical assessment.

---

## Prerequisites

- Python 3.11 or higher (`python --version` to check)
- pip 23+ (`pip --version` to check)
- Basic familiarity with JSON files

No database, no API key, no internet connection required after installation.

---

## Installation

**From PyPI (recommended):**

```bash
pip install aumai-edumentor
```

**Development install (from source):**

```bash
git clone https://github.com/aumai/aumai-edumentor
cd aumai-edumentor
pip install -e ".[dev]"
```

**Verify the installation:**

```bash
aumai-edumentor --version
aumai-edumentor subjects
```

You should see a list of subjects with unit counts.

---

## Step-by-Step Tutorial

This tutorial walks through the three core workflows: browsing content, generating a
learning path, and running an assessment.

### Step 1: Understand what content is available

```bash
aumai-edumentor subjects
```

This lists the built-in subjects. Each subject has a number of content units covering
different grade levels and difficulty levels.

To explore content for a specific subject programmatically:

```python
from aumai_edumentor.core import ContentLibrary

library = ContentLibrary()

# See all math content
math_content = library.search("math")
for unit in math_content:
    print(f"Grade {unit.grade_level} | {unit.difficulty:12s} | {unit.topic}")
```

Output:

```
Grade 1 | beginner     | Counting and Numbers
Grade 2 | beginner     | Addition and Subtraction
Grade 3 | beginner     | Multiplication Tables
Grade 5 | intermediate | Fractions
Grade 5 | intermediate | Fractions Quiz
...
```

### Step 2: Create a learner profile

A `LearnerProfile` captures everything the path generator needs to personalise content.

**As a JSON file** (for CLI use):

Create `learner.json`:

```json
{
  "learner_id": "student-001",
  "name": "Priya",
  "age": 12,
  "grade": 7,
  "language": "en",
  "strengths": ["science"],
  "weaknesses": ["math"],
  "learning_style": "visual"
}
```

Valid `learning_style` values: `visual`, `auditory`, `kinesthetic`, `read-write`.

**As a Python object:**

```python
from aumai_edumentor.models import LearnerProfile

learner = LearnerProfile(
    learner_id="student-001",
    name="Priya",
    age=12,
    grade=7,
    language="en",
    strengths=["science"],
    weaknesses=["math"],
    learning_style="visual",
)
```

### Step 3: Generate a learning path

**CLI:**

```bash
aumai-edumentor path --learner learner.json --subject math
```

The output shows the ordered content sequence. Because Priya is in grade 7 with math
as a weakness and visual as her learning style, the generator will:

- Filter to grade 6–8 content
- Start at beginner difficulty (because math is a weakness)
- Place activity-type content (preferred for visual learners) before text content

**Python:**

```python
from aumai_edumentor.models import LearnerProfile
from aumai_edumentor.core import PathGenerator

learner = LearnerProfile(
    learner_id="student-001",
    name="Priya",
    age=12,
    grade=7,
    strengths=["science"],
    weaknesses=["math"],
    learning_style="visual",
)

generator = PathGenerator()
path = generator.generate(learner, subject="math")

print(f"Units in path: {len(path.content_sequence)}")
print(f"Progress: {path.progress_pct}%")

for i, unit in enumerate(path.content_sequence, 1):
    print(f"\n{i}. {unit.topic}")
    print(f"   Difficulty: {unit.difficulty}")
    print(f"   Type: {unit.content_type}")
    print(f"   NCF codes: {', '.join(unit.ncf_alignment)}")
```

### Step 4: Run an assessment

After a learner completes some content, evaluate their understanding.

**Create the answers file `answers.json`:**

```json
[
  {"question_id": "q1", "correct": true,  "topic": "Geometry: Triangles"},
  {"question_id": "q2", "correct": true,  "topic": "Geometry: Triangles"},
  {"question_id": "q3", "correct": false, "topic": "Algebra Introduction"},
  {"question_id": "q4", "correct": false, "topic": "Linear Equations"}
]
```

**CLI:**

```bash
aumai-edumentor assess \
  --learner-id student-001 \
  --subject math \
  --answers answers.json
```

Output:

```
ASSESSMENT RESULT
Learner ID: student-001 | Subject: math
Score: 50.0%
Performance: Needs Improvement

AREAS TO IMPROVE:
  - Algebra Introduction
  - Linear Equations
```

**Python:**

```python
from aumai_edumentor.core import AssessmentEngine

engine = AssessmentEngine()
answers = [
    {"question_id": "q1", "correct": True,  "topic": "Geometry: Triangles"},
    {"question_id": "q2", "correct": True,  "topic": "Geometry: Triangles"},
    {"question_id": "q3", "correct": False, "topic": "Algebra Introduction"},
    {"question_id": "q4", "correct": False, "topic": "Linear Equations"},
]
result = engine.evaluate("student-001", "math", answers)
print(f"Score: {result.score}%")
print(f"Improve: {result.areas_to_improve}")
```

### Step 5: Iterate — regenerate the path with updated weaknesses

After reviewing the assessment, update the learner profile to include the newly identified
weaknesses, then regenerate the path:

```python
learner.weaknesses = ["math", "Algebra Introduction", "Linear Equations"]
path = generator.generate(learner, subject="math")
# path now prioritises beginner content for algebra and linear equations
```

---

## 5 Common Patterns

### Pattern 1: Batch path generation for a classroom

```python
from aumai_edumentor.models import LearnerProfile
from aumai_edumentor.core import PathGenerator

generator = PathGenerator()

students = [
    LearnerProfile(learner_id=f"s{i}", name=f"Student {i}", age=10+i,
                   grade=5, learning_style="visual")
    for i in range(30)
]

paths = {s.learner_id: generator.generate(s, "math") for s in students}
# Each student gets a personalised path from the same library
```

### Pattern 2: Load learner profiles from a directory of JSON files

```python
import json
from pathlib import Path
from aumai_edumentor.models import LearnerProfile
from aumai_edumentor.core import PathGenerator

generator = PathGenerator()
profile_dir = Path("./learner_profiles/")

for json_file in profile_dir.glob("*.json"):
    with json_file.open() as f:
        learner = LearnerProfile.model_validate(json.load(f))
    path = generator.generate(learner, subject="science")
    print(f"{learner.name}: {len(path.content_sequence)} science units")
```

### Pattern 3: Extend the library with subject-specific content

```python
from aumai_edumentor.core import ContentLibrary, PathGenerator
from aumai_edumentor.models import LearnerContent

library = ContentLibrary()

library.add(LearningContent(
    content_id="evs-custom-001",
    subject="social_studies",
    topic="Water Conservation",
    difficulty="beginner",
    content_type="activity",
    content="Measure daily water usage at home. Compare with national average.",
    ncf_alignment=["NCF-EVS-G4-ENV-1"],
    grade_level=4,
))

generator = PathGenerator(library=library)
```

### Pattern 4: Filter content library results for a report

```python
from aumai_edumentor.core import ContentLibrary

library = ContentLibrary()

# Report: all advanced content across all subjects
advanced_units = [c for c in library.all_content() if c.difficulty == "advanced"]
for unit in advanced_units:
    print(f"{unit.subject:15s} | Grade {unit.grade_level} | {unit.topic}")
```

### Pattern 5: Deserialise a LearnerProfile from an API request body

```python
import json
from aumai_edumentor.models import LearnerProfile

raw_json = '{"learner_id":"x1","name":"Arun","age":9,"grade":4,"learning_style":"kinesthetic"}'
learner = LearnerProfile.model_validate(json.loads(raw_json))
# Pydantic validates age (4-25), grade (1-12), and learning_style pattern
```

---

## Troubleshooting FAQ

**Q: `aumai-edumentor: command not found` after pip install.**

A: The pip scripts directory may not be on your `PATH`. Try:

```bash
python -m aumai_edumentor.cli --help
```

Or add pip's script directory to `PATH`: on Linux/Mac, typically `~/.local/bin`.

---

**Q: `ValidationError: 1 validation error for LearnerProfile — learning_style`**

A: The `learning_style` field only accepts these exact strings: `visual`, `auditory`,
`kinesthetic`, `read-write`. Check for typos in your JSON.

---

**Q: `ValidationError: age` — Input should be greater than or equal to 4**

A: `age` must be between 4 and 25. `grade` must be between 1 and 12. These are enforced
by Pydantic at model creation time.

---

**Q: The generated learning path is empty.**

A: This happens when the content library has no content for the requested subject. Run
`aumai-edumentor subjects` to see valid subject names. Subject names are case-insensitive
in the API but must match exactly (e.g. `social_studies` not `social studies`).

---

**Q: The assessment score is 0.0 even though I passed correct answers.**

A: Check that the `correct` field in your answers JSON is a boolean (`true`/`false`) not a
string (`"true"`/`"false"`). The engine handles string falsy values (`"false"`, `"0"`,
`"no"`) but passes all non-empty strings as truthy. Prefer native JSON booleans.

---

**Q: How do I use this with a different language?**

A: Set `language` in `LearnerProfile` to the appropriate IETF language tag (e.g. `"hi"`
for Hindi, `"ta"` for Tamil). The `language` field is stored and returned but currently
does not filter content — content selection is grade- and difficulty-based. Add translated
content via `ContentLibrary.add()`.

---

**Q: Can I use the Python API without the CLI?**

A: Yes. The CLI is a thin wrapper around the Python API. All three classes —
`ContentLibrary`, `PathGenerator`, and `AssessmentEngine` — are fully usable as Python
imports. The CLI is optional.

---

## Next Steps

- [API Reference](api-reference.md) — full documentation of every class, method, and field
- [Examples](../examples/quickstart.py) — working demo script
- [Contributing](../CONTRIBUTING.md) — how to contribute content or code
