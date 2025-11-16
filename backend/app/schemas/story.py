"""Pydantic schemas for story API."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class StoryBase(BaseModel):
    """Base story schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    theme_id: str = Field(default="warhammer40k", max_length=50)
    tags: list[str] = Field(default_factory=list)


class StoryCreate(StoryBase):
    """Schema for creating a new story."""

    prompt: str = Field(..., min_length=50, max_length=5000)
    template_id: str | None = Field(None, max_length=50)
    game_file_path: str = Field(..., min_length=1, max_length=500)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags are lowercase and unique."""
        return list({tag.lower().strip() for tag in v if tag.strip()})


class StoryUpdate(BaseModel):
    """Schema for updating a story."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    tags: list[str] | None = Field(default=None)
    scene_count: int | None = Field(default=None)
    item_count: int | None = Field(default=None)
    npc_count: int | None = Field(default=None)
    puzzle_count: int | None = Field(default=None)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags are lowercase and unique, or None if not provided."""
        if v is None:
            return None
        return list({tag.lower().strip() for tag in v if tag.strip()})

    @field_validator("scene_count", "item_count", "npc_count", "puzzle_count")
    @classmethod
    def validate_counts(cls, v: int | None) -> int | None:
        """Validate counts are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Count must be non-negative")
        return v


class StoryResponse(StoryBase):
    """Schema for story response."""

    id: int
    game_file_path: str
    created_at: datetime
    updated_at: datetime
    play_count: int
    last_played: datetime | None
    prompt: str
    template_id: str | None
    iteration_count: int
    scene_count: int | None
    item_count: int | None
    npc_count: int | None
    puzzle_count: int | None
    is_sample: bool = False

    model_config = {"from_attributes": True}


class StoryListResponse(BaseModel):
    """Paginated list of stories."""

    items: list[StoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
