from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

AnalysisText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# Task 2: Reusable constrained string type for Entry fields
EntryText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=256,
        strict=True,
    ),
]


class AnalysisResponse(BaseModel):
    """Response model for journal entry analysis."""

    model_config = ConfigDict(hide_input_in_errors=True)

    entry_id: str = Field(description="ID of the analyzed entry")
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="Sentiment: positive, negative, or neutral"
    )
    summary: AnalysisText = Field(
        description="Nonempty summary of the entry; aim for two sentences"
    )
    topics: list[AnalysisText] = Field(
        min_length=2, max_length=4, description="2-4 nonempty key topics mentioned in the entry"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the analysis was created",
    )


class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input)."""

    work: EntryText = Field(
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"},
    )
    struggle: EntryText = Field(
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"},
    )
    intention: EntryText = Field(
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"},
    )


class EntryUpdate(BaseModel):
    """Model for updating an existing journal entry (user input)."""

    work: EntryText | None = None
    struggle: EntryText | None = None
    intention: EntryText | None = None

    @field_validator("work", "struggle", "intention", mode="before")
    @classmethod
    def reject_explicit_none(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Explicit null is invalid")
        return value


class Entry(BaseModel):
    """A persisted entry. The service, not response validation, creates metadata."""

    id: str = Field(description="Unique identifier for the entry (UUID).")
    work: str = Field(description="What did you work on today?")
    struggle: str = Field(description="What's one thing you struggled with today?")
    intention: str = Field(description="What will you study/work on tomorrow?")
    created_at: datetime = Field(
        description="Timestamp when the entry was created.",
    )
    updated_at: datetime = Field(
        description="Timestamp when the entry was last updated.",
    )


class EntryCreatedResponse(BaseModel):
    detail: str
    entry: Entry


class EntryListResponse(BaseModel):
    entries: list[Entry]
    count: int


class DetailResponse(BaseModel):
    detail: str
