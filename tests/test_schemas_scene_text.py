"""Unit tests for scene_text schema models."""

import pytest
from pydantic import ValidationError

from space_hulk_game.schemas.scene_text import (
    SceneDialogue,
    SceneText,
    SceneTexts,
)


class TestSceneDialogue:
    """Tests for SceneDialogue model."""

    def test_valid_dialogue(self):
        """Test creating valid dialogue."""
        dialogue = SceneDialogue(
            speaker="Brother-Captain Tyberius",
            text="Status report!",
        )
        assert dialogue.speaker == "Brother-Captain Tyberius"
        assert dialogue.emotion is None
        assert dialogue.context is None

    def test_dialogue_with_emotion_and_context(self):
        """Test dialogue with optional fields."""
        dialogue = SceneDialogue(
            speaker="Test Speaker",
            text="Test dialogue text",
            emotion="Angry",
            context="During battle",
        )
        assert dialogue.emotion == "Angry"
        assert dialogue.context == "During battle"


class TestSceneText:
    """Tests for SceneText model."""

    def test_valid_scene_text(self):
        """Test creating valid scene text."""
        scene = SceneText(
            name="Test Scene",
            description="A" * 50,
            atmosphere="Dark, ominous",
            initial_text="You enter the scene",
            examination_texts={"object1": "Description of object 1"},
            dialogue=[SceneDialogue(speaker="Speaker", text="Text")],
        )
        assert scene.name == "Test Scene"
        assert len(scene.examination_texts) == 1
        assert len(scene.dialogue) == 1

    def test_examination_text_minimum_length(self):
        """Test examination texts must be at least 10 characters."""
        with pytest.raises(ValidationError, match="at least 10"):
            SceneText(
                name="Test",
                description="A" * 50,
                atmosphere="Atmosphere",
                initial_text="Initial text",
                examination_texts={"object": "short"},  # Too short
            )

    def test_description_quality_validation(self):
        """Test description must be at least 100 characters when in SceneTexts."""
        # Individual SceneText allows 50+ chars
        scene = SceneText(
            name="Test",
            description="A" * 60,  # 60 chars is valid for individual SceneText
            atmosphere="Atmosphere",
            initial_text="Initial text",
        )
        assert len(scene.description) == 60


class TestSceneTexts:
    """Tests for SceneTexts model."""

    def test_valid_scene_texts(self):
        """Test creating valid scene texts collection."""
        st = SceneTexts(
            scenes={
                "scene_1": SceneText(
                    name="Scene 1",
                    description="A" * 100,  # 100+ for immersion
                    atmosphere="Dark",
                    initial_text="Welcome to scene 1",
                ),
                "scene_2": SceneText(
                    name="Scene 2",
                    description="B" * 100,
                    atmosphere="Bright",
                    initial_text="Welcome to scene 2",
                ),
            }
        )
        assert len(st.scenes) == 2

    def test_scene_description_quality_in_collection(self):
        """Test scenes in collection must have 100+ char descriptions."""
        with pytest.raises(ValidationError, match="at least 100"):
            SceneTexts(
                scenes={
                    "scene_1": SceneText(
                        name="Scene 1",
                        description="A" * 60,  # Too short for immersion
                        atmosphere="Dark",
                        initial_text="Welcome",
                    )
                }
            )

    def test_scene_id_format_validation(self):
        """Test scene IDs must be alphanumeric with underscores/hyphens."""
        with pytest.raises(ValidationError):
            SceneTexts(
                scenes={
                    "scene@invalid": SceneText(  # Invalid ID
                        name="Scene",
                        description="A" * 100,
                        atmosphere="Dark",
                        initial_text="Welcome",
                    )
                }
            )
