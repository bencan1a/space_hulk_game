"""Initial schema

Revision ID: 001
Create Date: 2025-11-12
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables."""
    # Stories table
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("theme_id", sa.String(length=50), nullable=False),
        sa.Column("game_file_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("play_count", sa.Integer(), nullable=False),
        sa.Column("last_played", sa.DateTime(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("template_id", sa.String(length=50), nullable=True),
        sa.Column("iteration_count", sa.Integer(), nullable=False),
        sa.Column("scene_count", sa.Integer(), nullable=True),
        sa.Column("item_count", sa.Integer(), nullable=True),
        sa.Column("npc_count", sa.Integer(), nullable=True),
        sa.Column("puzzle_count", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_file_path"),
    )
    op.create_index("idx_stories_created", "stories", ["created_at"])
    op.create_index("idx_stories_theme", "stories", ["theme_id"])

    # Iterations table
    op.create_table(
        "iterations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("story_id", sa.Integer(), nullable=False),
        sa.Column("iteration_number", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("changes_requested", sa.JSON(), nullable=True),
        sa.Column("game_file_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["story_id"],
            ["stories.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_iterations_story", "iterations", ["story_id", "iteration_number"]
    )

    # Sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("story_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("current_step", sa.String(length=50), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["story_id"],
            ["stories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("sessions")
    op.drop_table("iterations")
    op.drop_table("stories")
