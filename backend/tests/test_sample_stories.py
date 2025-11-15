"""Tests for sample story seeding and protection."""

import json
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.models.story import Story


def test_sample_stories_exist(db_session):
    """Test that sample stories are seeded in database."""
    samples = db_session.query(Story).filter(Story.is_sample == True).all()  # noqa: E712

    assert len(samples) >= 3, "Should have at least 3 sample stories"
    assert all(s.is_sample for s in samples), "All samples should have is_sample=True"


def test_sample_stories_have_correct_metadata(db_session):
    """Test that sample stories have expected metadata."""
    samples = db_session.query(Story).filter(Story.is_sample == True).all()  # noqa: E712

    for sample in samples:
        assert sample.title, "Sample should have a title"
        assert sample.description, "Sample should have a description"
        assert sample.game_file_path, "Sample should have a game_file_path"
        assert sample.tags, "Sample should have tags"
        assert sample.scene_count is not None, "Sample should have scene_count"
        assert sample.item_count is not None, "Sample should have item_count"
        assert sample.npc_count is not None, "Sample should have npc_count"


def test_sample_game_files_exist():
    """Test that sample game.json files exist and are valid JSON."""
    # Get the root directory (parent of backend)
    root_dir = Path(__file__).parent.parent.parent
    samples_dir = root_dir / "data" / "samples"

    required_samples = [
        "sample-001-derelict-station",
        "sample-002-hive-assault",
        "sample-003-cyberpunk-heist",
        "sample-004-mystery-cult",
        "sample-005-rescue-mission",
    ]

    for sample in required_samples:
        game_file = samples_dir / sample / "game.json"
        assert game_file.exists(), f"Missing game file: {game_file}"

        # Validate JSON structure
        with game_file.open() as f:
            data = json.load(f)

        # Verify required fields
        assert "title" in data, f"{sample}: Missing title"
        assert "scenes" in data, f"{sample}: Missing scenes"
        assert "items" in data, f"{sample}: Missing items"
        assert "npcs" in data, f"{sample}: Missing npcs"
        assert "player" in data, f"{sample}: Missing player"
        assert "metadata" in data, f"{sample}: Missing metadata"

        # Verify scenes are not empty
        assert len(data["scenes"]) > 0, f"{sample}: Should have at least one scene"


def test_sample_stories_theme_distribution():
    """Test that sample stories cover different themes."""
    # Get the root directory (parent of backend)
    root_dir = Path(__file__).parent.parent.parent
    samples_dir = root_dir / "data" / "samples"

    themes = set()
    for sample_dir in samples_dir.iterdir():
        if sample_dir.is_dir():
            game_file = sample_dir / "game.json"
            if game_file.exists():
                with game_file.open() as f:
                    data = json.load(f)
                themes.add(data.get("theme"))

    # Should have at least Warhammer 40K and Cyberpunk themes
    assert "warhammer40k" in themes, "Should have Warhammer 40K samples"
    assert "cyberpunk" in themes, "Should have Cyberpunk samples"


def test_sample_stories_content_structure():
    """Test that sample stories have complete game structures."""
    # Get the root directory (parent of backend)
    root_dir = Path(__file__).parent.parent.parent
    samples_dir = root_dir / "data" / "samples"

    for sample_dir in samples_dir.iterdir():
        if sample_dir.is_dir():
            game_file = sample_dir / "game.json"
            if game_file.exists():
                with game_file.open() as f:
                    data = json.load(f)

                # Verify scenes have required fields
                for scene in data.get("scenes", []):
                    assert "id" in scene, f"{sample_dir.name}: Scene missing id"
                    assert "name" in scene, f"{sample_dir.name}: Scene missing name"
                    assert "description" in scene, f"{sample_dir.name}: Scene missing description"
                    assert "connections" in scene, f"{sample_dir.name}: Scene missing connections"

                # Verify items have required fields
                for item in data.get("items", []):
                    assert "id" in item, f"{sample_dir.name}: Item missing id"
                    assert "name" in item, f"{sample_dir.name}: Item missing name"
                    assert "type" in item, f"{sample_dir.name}: Item missing type"

                # Verify NPCs have required fields
                for npc in data.get("npcs", []):
                    assert "id" in npc, f"{sample_dir.name}: NPC missing id"
                    assert "name" in npc, f"{sample_dir.name}: NPC missing name"
                    assert "type" in npc, f"{sample_dir.name}: NPC missing type"


@pytest.mark.asyncio
async def test_sample_stories_cannot_be_deleted(db_session):
    """Test that sample stories are protected from deletion."""
    # Get a sample story
    sample = db_session.query(Story).filter(Story.is_sample == True).first()  # noqa: E712

    if sample:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/api/v1/stories/{sample.id}")

            assert response.status_code == 403, "Should return 403 Forbidden"
            assert "cannot be deleted" in response.json()["detail"].lower(), (
                "Error message should mention deletion protection"
            )

            # Verify the story still exists
            db_session.expire_all()
            still_exists = db_session.query(Story).filter(Story.id == sample.id).first()
            assert still_exists is not None, "Sample story should still exist after delete attempt"


@pytest.mark.asyncio
async def test_list_stories_filter_by_is_sample(db_session):  # noqa: ARG001
    """Test filtering stories by is_sample parameter."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test filtering for sample stories only
        response = await client.get("/api/v1/stories?is_sample=true")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 3, "Should have at least 3 sample stories"

        # Verify all returned items are samples
        for item in data["items"]:
            assert item["is_sample"] is True, "All items should be samples"


@pytest.mark.asyncio
async def test_list_stories_filter_non_samples(db_session):  # noqa: ARG001
    """Test filtering for non-sample stories."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test filtering for non-sample stories
        response = await client.get("/api/v1/stories?is_sample=false")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

        # Verify all returned items are not samples
        for item in data["items"]:
            assert item["is_sample"] is False, "All items should not be samples"


@pytest.mark.asyncio
async def test_get_sample_story_content(db_session):
    """Test retrieving game.json content for a sample story."""
    # Get a sample story
    sample = db_session.query(Story).filter(Story.is_sample == True).first()  # noqa: E712

    if sample:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/stories/{sample.id}/content")

            assert response.status_code == 200
            content = response.json()

            # Verify content structure
            assert "title" in content
            assert "scenes" in content
            assert "items" in content
            assert "npcs" in content
            assert len(content["scenes"]) > 0, "Should have at least one scene"


@pytest.mark.asyncio
async def test_sample_story_response_includes_is_sample(db_session):
    """Test that story response includes is_sample field."""
    # Get a sample story
    sample = db_session.query(Story).filter(Story.is_sample == True).first()  # noqa: E712

    if sample:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/stories/{sample.id}")

            assert response.status_code == 200
            data = response.json()

            assert "is_sample" in data, "Response should include is_sample field"
            assert data["is_sample"] is True, "Sample story should have is_sample=True"


def test_sample_stories_count(db_session):
    """Test that exactly 5 sample stories are seeded."""
    samples = db_session.query(Story).filter(Story.is_sample == True).all()  # noqa: E712

    assert len(samples) == 5, "Should have exactly 5 sample stories"


def test_sample_stories_unique_paths(db_session):
    """Test that sample stories have unique game file paths."""
    samples = db_session.query(Story).filter(Story.is_sample == True).all()  # noqa: E712

    paths = [s.game_file_path for s in samples]
    assert len(paths) == len(set(paths)), "All sample stories should have unique paths"
