"""Pydantic schemas for generation API."""

from datetime import datetime

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Schema for starting a new generation."""

    prompt: str = Field(..., min_length=50, max_length=5000, description="Generation prompt")
    template_id: str | None = Field(None, max_length=50, description="Optional template ID")


class GenerationResponse(BaseModel):
    """Schema for generation start response."""

    session_id: str = Field(..., description="Unique session ID for tracking progress")
    status: str = Field(default="pending", description="Initial status")
    message: str = Field(default="Generation task started", description="Status message")


class GenerationStatusResponse(BaseModel):
    """Schema for generation status response."""

    session_id: str = Field(
        ..., alias="id", serialization_alias="session_id", description="Session ID"
    )
    status: str = Field(..., description="Current status (pending, running, completed, failed)")
    current_step: str | None = Field(None, description="Current processing step")
    progress_percent: int = Field(..., ge=0, le=100, description="Progress percentage")
    created_at: datetime = Field(..., description="Session creation timestamp")
    completed_at: datetime | None = Field(None, description="Session completion timestamp")
    error_message: str | None = Field(None, description="Error message if failed")
    story_id: int | None = Field(None, description="Story ID if completed successfully")

    model_config = {"from_attributes": True, "populate_by_name": True}
