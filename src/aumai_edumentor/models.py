"""Pydantic v2 models for aumai-edumentor personalised learning AI."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "LearnerProfile",
    "LearningContent",
    "LearningPath",
    "AssessmentResult",
]


class LearnerProfile(BaseModel):
    """Profile of a learner for personalised path generation."""

    learner_id: str = Field(..., description="Unique learner identifier")
    name: str = Field(..., description="Learner's name")
    age: int = Field(..., ge=4, le=25, description="Learner's age in years")
    grade: int = Field(..., ge=1, le=12, description="Current grade (1-12)")
    language: str = Field(default="en", description="Preferred language code")
    strengths: list[str] = Field(default_factory=list, description="Subject or topic strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Subject or topic weaknesses")
    learning_style: str = Field(
        default="visual",
        description="Learning style: visual, auditory, kinesthetic, or read-write",
        pattern="^(visual|auditory|kinesthetic|read-write)$",
    )


class LearningContent(BaseModel):
    """A single unit of learning content aligned with NCF 2023."""

    content_id: str = Field(..., description="Unique content identifier")
    subject: str = Field(..., description="Subject name (e.g. math, science, hindi)")
    topic: str = Field(..., description="Specific topic within the subject")
    difficulty: str = Field(
        ...,
        description="Difficulty level: beginner, intermediate, or advanced",
        pattern="^(beginner|intermediate|advanced)$",
    )
    content_type: str = Field(
        ...,
        description="Content format: text, quiz, or activity",
        pattern="^(text|quiz|activity)$",
    )
    content: str = Field(..., description="The actual content text, quiz JSON, or activity description")
    ncf_alignment: list[str] = Field(
        default_factory=list,
        description="NCF 2023 competency codes or learning outcome references",
    )
    grade_level: int = Field(default=5, ge=1, le=12, description="Target grade level")


class LearningPath(BaseModel):
    """A personalised sequence of learning content for a learner."""

    learner: LearnerProfile
    content_sequence: list[LearningContent] = Field(
        ..., description="Ordered list of learning content units"
    )
    progress_pct: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion percentage"
    )


class AssessmentResult(BaseModel):
    """Result of a learning assessment for a learner."""

    learner_id: str = Field(..., description="Learner identifier")
    subject: str = Field(..., description="Subject assessed")
    score: float = Field(..., ge=0.0, le=100.0, description="Score as a percentage")
    areas_to_improve: list[str] = Field(
        ..., description="Topics or skills that need improvement"
    )
