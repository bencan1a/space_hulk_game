"""Add is_sample field and seed sample stories

Revision ID: 002
Revises: 001
Create Date: 2025-11-15 07:40:00.000000

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add is_sample field and seed sample stories."""
    # Add is_sample column to stories table
    op.add_column(
        "stories",
        sa.Column("is_sample", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index("ix_stories_is_sample", "stories", ["is_sample"])

    # Sample story metadata
    samples = [
        {
            "title": "Derelict Station Omega-7",
            "description": "Explore an abandoned space station in the Ghoul Stars sector. Uncover what happened to the crew while battling corrupted servitors and avoiding environmental hazards.",
            "theme_id": "warhammer40k",
            "tags": '["horror", "atmospheric", "combat", "exploration"]',
            "game_file_path": "data/samples/sample-001-derelict-station/game.json",
            "prompt": "Create a horror-themed Space Hulk mission exploring a derelict station with corrupted servitors and environmental hazards.",
            "template_id": "exploration_horror",
            "is_sample": True,
            "scene_count": 4,
            "item_count": 4,
            "npc_count": 2,
            "puzzle_count": 2,
        },
        {
            "title": "Hive Assault: Purge of Sector 7-G",
            "description": "Lead a squad through a hive city's underbelly to eliminate a genestealer cult. Fast-paced combat and tactical decisions.",
            "theme_id": "warhammer40k",
            "tags": '["action", "combat", "squad-based"]',
            "game_file_path": "data/samples/sample-002-hive-assault/game.json",
            "prompt": "Create an action-packed combat mission in a hive city with a genestealer cult as the enemy.",
            "template_id": "combat_tactical",
            "is_sample": True,
            "scene_count": 3,
            "item_count": 2,
            "npc_count": 4,
            "puzzle_count": 0,
        },
        {
            "title": "Neon Heist: The Arasaka Job",
            "description": "Infiltrate a megacorp tower to steal valuable data. Stealth, hacking, and quick thinking required.",
            "theme_id": "cyberpunk",
            "tags": '["cyberpunk", "stealth", "hacking"]',
            "game_file_path": "data/samples/sample-003-cyberpunk-heist/game.json",
            "prompt": "Create a cyberpunk stealth mission involving infiltration and hacking of a corporate tower.",
            "template_id": "stealth_heist",
            "is_sample": True,
            "scene_count": 3,
            "item_count": 2,
            "npc_count": 2,
            "puzzle_count": 2,
        },
        {
            "title": "The Ritual of Crimson Stars",
            "description": "Investigate a mysterious cult in the underhive. Uncover ancient secrets and prevent a dark ritual.",
            "theme_id": "warhammer40k",
            "tags": '["mystery", "investigation", "horror"]',
            "game_file_path": "data/samples/sample-004-mystery-cult/game.json",
            "prompt": "Create a mystery investigation mission involving a dark cult and ancient secrets.",
            "template_id": "mystery_investigation",
            "is_sample": True,
            "scene_count": 5,
            "item_count": 6,
            "npc_count": 3,
            "puzzle_count": 3,
        },
        {
            "title": "Rescue at Firebase Zeta",
            "description": "Extract Imperial Guard survivors from an overrun firebase. Time is running out.",
            "theme_id": "warhammer40k",
            "tags": '["rescue", "action", "time-pressure"]',
            "game_file_path": "data/samples/sample-005-rescue-mission/game.json",
            "prompt": "Create a time-sensitive rescue mission to extract survivors from an overrun military base.",
            "template_id": "rescue_operation",
            "is_sample": True,
            "scene_count": 4,
            "item_count": 3,
            "npc_count": 5,
            "puzzle_count": 1,
        },
    ]

    # Insert sample stories
    conn = op.get_bind()
    now = datetime.now(timezone.utc)

    for sample in samples:
        conn.execute(
            sa.text(
                """
                INSERT INTO stories (
                    title, description, theme_id, tags, game_file_path,
                    prompt, template_id, is_sample, scene_count, item_count,
                    npc_count, puzzle_count, created_at, updated_at,
                    play_count, iteration_count
                )
                VALUES (
                    :title, :description, :theme_id, :tags, :game_file_path,
                    :prompt, :template_id, :is_sample, :scene_count, :item_count,
                    :npc_count, :puzzle_count, :created_at, :updated_at,
                    0, 1
                )
            """
            ),
            {
                **sample,
                "created_at": now,
                "updated_at": now,
            },
        )


def downgrade() -> None:
    """Remove sample stories and is_sample field."""
    # Remove sample stories
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM stories WHERE is_sample = true"))

    # Drop is_sample column
    op.drop_index("ix_stories_is_sample", table_name="stories")
    op.drop_column("stories", "is_sample")
