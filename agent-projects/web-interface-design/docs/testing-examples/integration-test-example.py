"""
Integration Test Example
Demonstrates best practices for testing API endpoints with real database and services.

This example shows:
- API integration testing with test database
- Complete workflow testing (multiple API calls)
- Database transaction testing
- WebSocket integration testing
- Async operation testing
- Error handling across components
"""

import asyncio
import json
from datetime import datetime

import pytest
from app.dependencies import get_db
from app.main import app
from app.models.base import Base
from app.models.story import Story
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# === TEST DATABASE SETUP ===


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine (PostgreSQL)."""
    # Use separate test database
    DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine):
    """Provide database session for tests, rollback after each test."""
    async_session = sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Provide HTTP client with test database."""
    # Override database dependency
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# === TEST DATA FIXTURES ===


@pytest.fixture
async def sample_story(db_session: AsyncSession) -> Story:
    """Create and return a sample complete story."""
    story = Story(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Sample Horror Story",
        description="A test horror story",
        theme_id="warhammer40k",
        game_file_path="/stories/550e8400/game.json",
        prompt="Create a horror adventure",
        is_sample=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_version=1,
        total_iterations=0,
        play_count=0,
        scene_count=8,
        item_count=12,
        npc_count=3,
        puzzle_count=2,
        tags=["horror", "atmospheric"],
    )

    db_session.add(story)
    await db_session.commit()
    await db_session.refresh(story)
    return story


@pytest.fixture
async def sample_game_content(tmp_path):
    """Create sample game.json file."""
    game_content = {
        "plot": {"title": "Test Plot", "acts": []},
        "narrative_map": {
            "scenes": {
                "scene_001": {
                    "title": "Starting Room",
                    "description": "You are in a dark room.",
                    "items": ["flashlight"],
                    "exits": {"north": "scene_002"},
                }
            }
        },
        "puzzles": [],
        "scenes": {},
    }

    game_file = tmp_path / "game.json"
    game_file.write_text(json.dumps(game_content))
    return str(game_file)


# === STORY API INTEGRATION TESTS ===


@pytest.mark.integration
class TestStoryAPIIntegration:
    """Integration tests for Story API endpoints."""

    async def test_list_stories_empty_database(self, client: AsyncClient):
        """
        Test listing stories when database is empty.

        Steps:
        1. Call GET /api/v1/stories
        2. Verify 200 OK
        3. Verify empty list returned
        """
        response = await client.get("/api/v1/stories")

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    async def test_list_stories_with_data(self, client: AsyncClient, sample_story: Story):
        """
        Test listing stories with data in database.

        Steps:
        1. Create story via fixture
        2. Call GET /api/v1/stories
        3. Verify story in list
        """
        response = await client.get("/api/v1/stories")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == sample_story.id
        assert data["data"][0]["title"] == "Sample Horror Story"

    async def test_search_stories_case_insensitive(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """
        Test search is case-insensitive.

        Steps:
        1. Create stories with mixed case titles
        2. Search with lowercase query
        3. Verify results match case-insensitively
        """
        # Create test stories
        stories = [
            Story(
                id=f"story-{i}", title=f"Horror Story {i}", theme_id="warhammer40k", prompt="test"
            )
            for i in range(3)
        ]
        for story in stories:
            db_session.add(story)
        await db_session.commit()

        # Search with lowercase
        response = await client.get("/api/v1/stories?search=horror")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3

    async def test_filter_stories_by_theme(self, client: AsyncClient, db_session: AsyncSession):
        """
        Test filtering stories by theme.

        Steps:
        1. Create stories with different themes
        2. Filter by specific theme
        3. Verify only matching stories returned
        """
        # Create stories with different themes
        wh40k_story = Story(
            id="story-wh40k", title="WH40K Story", theme_id="warhammer40k", prompt="test"
        )
        cyberpunk_story = Story(
            id="story-cyber", title="Cyberpunk Story", theme_id="cyberpunk", prompt="test"
        )

        db_session.add(wh40k_story)
        db_session.add(cyberpunk_story)
        await db_session.commit()

        # Filter by warhammer40k
        response = await client.get("/api/v1/stories?theme=warhammer40k")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["theme_id"] == "warhammer40k"

    async def test_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """
        Test pagination works correctly.

        Steps:
        1. Create 25 stories
        2. Request page 1 with per_page=10
        3. Verify 10 stories returned
        4. Request page 2
        5. Verify next 10 stories returned
        """
        # Create 25 stories
        for i in range(25):
            story = Story(
                id=f"story-{i}", title=f"Story {i}", theme_id="warhammer40k", prompt="test"
            )
            db_session.add(story)
        await db_session.commit()

        # Page 1
        response = await client.get("/api/v1/stories?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["pages"] == 3

        # Page 2
        response = await client.get("/api/v1/stories?page=2&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["page"] == 2

    async def test_get_story_by_id(self, client: AsyncClient, sample_story: Story):
        """
        Test retrieving single story by ID.

        Steps:
        1. Call GET /api/v1/stories/{id}
        2. Verify 200 OK
        3. Verify story details returned
        """
        response = await client.get(f"/api/v1/stories/{sample_story.id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == sample_story.id
        assert data["title"] == "Sample Horror Story"
        assert data["scene_count"] == 8

    async def test_get_story_not_found(self, client: AsyncClient):
        """
        Test retrieving non-existent story returns 404.

        Steps:
        1. Call GET /api/v1/stories/{invalid_id}
        2. Verify 404 Not Found
        """
        response = await client.get("/api/v1/stories/invalid-id")

        assert response.status_code == 404
        error = response.json()["error"]
        assert "not found" in error["message"].lower()

    async def test_delete_story(self, client: AsyncClient, db_session: AsyncSession):
        """
        Test deleting a story.

        Steps:
        1. Create non-sample story
        2. Call DELETE /api/v1/stories/{id}
        3. Verify 204 No Content
        4. Verify story removed from database
        """
        # Create non-sample story
        story = Story(
            id="delete-me",
            title="Delete Me",
            theme_id="warhammer40k",
            is_sample=False,
            prompt="test",
        )
        db_session.add(story)
        await db_session.commit()

        # Delete
        response = await client.delete("/api/v1/stories/delete-me")
        assert response.status_code == 204

        # Verify deleted
        result = await db_session.get(Story, "delete-me")
        assert result is None

    async def test_delete_sample_story_forbidden(self, client: AsyncClient, sample_story: Story):
        """
        Test deleting sample story returns 403.

        Steps:
        1. Attempt to delete sample story
        2. Verify 403 Forbidden
        3. Verify story still exists
        """
        response = await client.delete(f"/api/v1/stories/{sample_story.id}")

        assert response.status_code == 403
        error = response.json()["error"]
        assert "sample" in error["message"].lower()


# === GENERATION WORKFLOW INTEGRATION TEST ===


@pytest.mark.integration
class TestGenerationWorkflow:
    """Integration tests for complete story generation workflow."""

    @pytest.mark.asyncio
    async def test_complete_generation_workflow(
        self, client: AsyncClient, _db_session: AsyncSession
    ):
        """
        Test complete story generation from start to finish.

        This is a long-running test that verifies the entire workflow:
        1. Submit story creation request
        2. Poll generation status
        3. Wait for completion
        4. Verify story created
        5. Verify game content exists

        Steps:
        1. POST /api/v1/stories with prompt
        2. Verify 202 Accepted with generation_job_id
        3. Poll GET /api/v1/generation/{job_id} until complete
        4. Verify story_id returned
        5. GET /api/v1/stories/{story_id}
        6. Verify story exists with correct data
        """
        # Step 1: Create story
        create_payload = {
            "prompt": "Create a horror-themed Space Hulk adventure with heavy atmosphere and minimal combat",
            "template_id": "horror_infestation",
            "theme_id": "warhammer40k",
        }

        create_response = await client.post("/api/v1/stories", json=create_payload)

        assert create_response.status_code == 202
        create_data = create_response.json()["data"]
        generation_job_id = create_data["generation_job_id"]
        story_id = create_data["story_id"]
        assert generation_job_id is not None
        assert story_id is not None

        # Step 2: Poll generation status
        max_wait = 600  # 10 minutes
        poll_interval = 5  # seconds
        waited = 0

        while waited < max_wait:
            status_response = await client.get(f"/api/v1/generation/{generation_job_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()["data"]
            status = status_data["status"]

            if status == "completed":
                assert status_data["progress_percent"] == 100
                assert status_data["story_id"] == story_id
                break
            elif status == "failed":
                pytest.fail(f"Generation failed: {status_data.get('error')}")

            await asyncio.sleep(poll_interval)
            waited += poll_interval

        if waited >= max_wait:
            pytest.fail("Generation timed out after 10 minutes")

        # Step 3: Verify story exists
        story_response = await client.get(f"/api/v1/stories/{story_id}")
        assert story_response.status_code == 200

        story_data = story_response.json()["data"]
        assert story_data["id"] == story_id
        assert story_data["title"] is not None
        assert story_data["scene_count"] > 0

        # Step 4: Verify game content
        content_response = await client.get(f"/api/v1/stories/{story_id}/content")
        assert content_response.status_code == 200

        content = content_response.json()["data"]
        assert "plot" in content
        assert "narrative_map" in content
        assert "scenes" in content

    @pytest.mark.asyncio
    async def test_concurrent_generation_prevented(
        self, client: AsyncClient, _db_session: AsyncSession
    ):
        """
        Test that only one generation can run at a time.

        Steps:
        1. Start first generation
        2. Attempt to start second generation
        3. Verify 429 Too Many Requests
        """
        # Start first generation
        payload = {"prompt": "First generation prompt", "theme_id": "warhammer40k"}

        first_response = await client.post("/api/v1/stories", json=payload)
        assert first_response.status_code == 202

        # Attempt second generation immediately
        second_response = await client.post("/api/v1/stories", json=payload)
        assert second_response.status_code == 429

        error = second_response.json()["error"]
        assert "already in progress" in error["message"].lower()


# === ITERATION WORKFLOW INTEGRATION TEST ===


@pytest.mark.integration
class TestIterationWorkflow:
    """Integration tests for story iteration workflow."""

    @pytest.mark.asyncio
    async def test_complete_iteration_workflow(
        self, client: AsyncClient, _db_session: AsyncSession, sample_story: Story
    ):
        """
        Test complete iteration workflow with feedback.

        Steps:
        1. POST /api/v1/stories/{id}/iterate with feedback
        2. Verify 202 Accepted with new job_id
        3. Poll generation status
        4. Wait for completion
        5. GET /api/v1/stories/{id}/iterations
        6. Verify iteration added
        7. Verify version incremented
        """
        story_id = sample_story.id

        # Step 1: Submit iteration feedback
        feedback_payload = {
            "feedback": "The puzzle in scene 2 needs better hints. Make the tone darker and more atmospheric.",
            "changes": {
                "plot_rating": 5,
                "puzzle_rating": 3,
                "writing_rating": 4,
                "tone_adjustment": "darker",
                "difficulty_adjustment": "easier",
                "focus_areas": ["puzzles", "atmosphere"],
            },
        }

        iterate_response = await client.post(
            f"/api/v1/stories/{story_id}/iterate", json=feedback_payload
        )

        assert iterate_response.status_code == 202
        iterate_data = iterate_response.json()["data"]
        job_id = iterate_data["generation_job_id"]
        iteration_number = iterate_data["iteration_number"]
        assert iteration_number == 2  # First iteration

        # Step 2: Wait for completion (similar to generation test)
        max_wait = 600
        poll_interval = 5
        waited = 0

        while waited < max_wait:
            status_response = await client.get(f"/api/v1/generation/{job_id}")
            status = status_response.json()["data"]["status"]

            if status == "completed":
                break
            elif status == "failed":
                pytest.fail("Iteration failed")

            await asyncio.sleep(poll_interval)
            waited += poll_interval

        # Step 3: Verify iterations list
        iterations_response = await client.get(f"/api/v1/stories/{story_id}/iterations")
        assert iterations_response.status_code == 200

        iterations = iterations_response.json()["data"]
        assert len(iterations) == 2  # Original + iteration
        assert iterations[1]["version"] == 2
        assert "puzzle" in iterations[1]["feedback"].lower()

    @pytest.mark.asyncio
    async def test_iteration_limit_enforced(
        self, client: AsyncClient, db_session: AsyncSession, sample_story: Story
    ):
        """
        Test that iteration limit (5) is enforced.

        Steps:
        1. Create story with 5 iterations already
        2. Attempt 6th iteration
        3. Verify 409 Conflict
        """
        # Update story to have 5 iterations
        sample_story.total_iterations = 5
        await db_session.commit()

        # Attempt 6th iteration
        feedback_payload = {"feedback": "This is the 6th iteration attempt", "changes": {}}

        response = await client.post(
            f"/api/v1/stories/{sample_story.id}/iterate", json=feedback_payload
        )

        assert response.status_code == 409
        error = response.json()["error"]
        assert "limit" in error["message"].lower()


# === GAME SESSION INTEGRATION TEST ===


@pytest.mark.integration
class TestGameSessionWorkflow:
    """Integration tests for gameplay session workflow."""

    @pytest.mark.asyncio
    async def test_complete_game_session_workflow(self, client: AsyncClient, sample_story: Story):
        """
        Test complete game session from start to save/load.

        Steps:
        1. POST /api/v1/game/{story_id}/start
        2. Verify initial scene returned
        3. POST /api/v1/game/{session_id}/command (multiple commands)
        4. Verify state updates
        5. POST /api/v1/game/{session_id}/save
        6. POST /api/v1/game/load/{save_id}
        7. Verify state restored
        """
        story_id = sample_story.id

        # Step 1: Start game
        start_response = await client.post(f"/api/v1/game/{story_id}/start")
        assert start_response.status_code == 200

        start_data = start_response.json()["data"]
        session_id = start_data["game_session_id"]
        assert start_data["initial_scene"] is not None
        assert start_data["state"]["current_scene"] is not None

        # Step 2: Send commands
        commands = ["look around", "examine door", "take flashlight", "use flashlight"]

        for command in commands:
            cmd_response = await client.post(
                f"/api/v1/game/{session_id}/command", json={"command": command}
            )

            assert cmd_response.status_code == 200
            cmd_data = cmd_response.json()["data"]
            assert cmd_data["output"] is not None
            assert cmd_data["state"] is not None

        # Step 3: Save game
        save_response = await client.post(
            f"/api/v1/game/{session_id}/save", json={"save_name": "Integration test save"}
        )

        assert save_response.status_code == 200
        save_data = save_response.json()["data"]
        save_id = save_data["save_id"]
        assert save_id is not None

        # Step 4: Load game
        load_response = await client.post(f"/api/v1/game/load/{save_id}")
        assert load_response.status_code == 200

        load_data = load_response.json()["data"]
        new_session_id = load_data["game_session_id"]
        assert new_session_id != session_id  # New session created
        assert load_data["state"] is not None

        # Verify inventory preserved
        assert "flashlight" in load_data["state"].get("inventory", [])


# === DATABASE TRANSACTION TESTS ===


@pytest.mark.integration
class TestDatabaseTransactions:
    """Integration tests for database transaction handling."""

    @pytest.mark.asyncio
    async def test_rollback_on_error(self, client: AsyncClient, db_session: AsyncSession):
        """
        Test that database rolls back on error.

        Steps:
        1. Start transaction
        2. Create story
        3. Simulate error
        4. Verify rollback occurred
        """
        initial_count = await db_session.execute("SELECT COUNT(*) FROM stories")
        initial_count = initial_count.scalar()

        # Attempt to create story with invalid data (will fail validation)
        invalid_payload = {
            "prompt": "Too short",  # Below minimum length
            "theme_id": "warhammer40k",
        }

        response = await client.post("/api/v1/stories", json=invalid_payload)
        assert response.status_code == 400

        # Verify no story created
        final_count = await db_session.execute("SELECT COUNT(*) FROM stories")
        final_count = final_count.scalar()
        assert final_count == initial_count

    @pytest.mark.asyncio
    async def test_foreign_key_constraint(self, client: AsyncClient, _db_session: AsyncSession):
        """
        Test that foreign key constraints are enforced.

        Steps:
        1. Attempt to create iteration for non-existent story
        2. Verify error
        """
        response = await client.post(
            "/api/v1/stories/non-existent-story/iterate", json={"feedback": "test"}
        )

        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
