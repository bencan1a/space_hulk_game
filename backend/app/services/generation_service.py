"""Service layer for managing story generation sessions."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.session import Session as SessionModel

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for managing story generation sessions."""

    def __init__(self, db: Session):
        """
        Initialize generation service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def start_generation(self, prompt: str, template_id: str | None = None) -> str:
        """
        Start a new story generation session.

        This creates a new Session record in the database and enqueues a
        Celery task to run the generation in the background.

        Args:
            prompt: User's generation prompt
            template_id: Optional template identifier

        Returns:
            str: Unique session ID for tracking progress

        Raises:
            ValueError: If prompt is invalid
        """
        if not prompt or len(prompt.strip()) < 50:
            raise ValueError("Prompt must be at least 50 characters")

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        try:
            # Create session record
            session = SessionModel(
                id=session_id,
                status="pending",
                current_step=None,
                progress_percent=0,
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(session)
            self.db.commit()

            logger.info(f"Created generation session: {session_id}")

            # Import here to avoid circular dependency (task imports this service)
            from ..tasks.generation_tasks import run_generation_crew  # noqa: PLC0415

            # Enqueue Celery task
            run_generation_crew.apply_async(
                args=[session_id, prompt, template_id],
                task_id=session_id,  # Use session_id as task_id for easy correlation
            )

            logger.info(f"Enqueued generation task for session: {session_id}")

            return session_id

        except Exception:
            self.db.rollback()
            raise

    def get_session(self, session_id: str) -> SessionModel | None:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session model or None if not found
        """
        result: SessionModel | None = (
            self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        )
        return result

    def update_session(
        self,
        session_id: str,
        status: str | None = None,
        current_step: str | None = None,
        progress_percent: int | None = None,
        error_message: str | None = None,
        story_id: int | None = None,
    ) -> SessionModel | None:
        """
        Update session progress and status.

        Args:
            session_id: Session ID
            status: New status (pending, running, completed, failed)
            current_step: Current processing step
            progress_percent: Progress percentage (0-100)
            error_message: Error message if status is failed
            story_id: Story ID if generation completed successfully

        Returns:
            Updated session or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        try:
            if status is not None:
                session.status = status  # type: ignore[assignment]

            if current_step is not None:
                session.current_step = current_step  # type: ignore[assignment]

            if progress_percent is not None:
                session.progress_percent = min(100, max(0, progress_percent))  # type: ignore[assignment]

            if error_message is not None:
                session.error_message = error_message  # type: ignore[assignment]

            if story_id is not None:
                session.story_id = story_id  # type: ignore[assignment]

            # Set completion timestamp if status is completed or failed
            if status in ("completed", "failed") and not session.completed_at:
                session.completed_at = datetime.now(timezone.utc)  # type: ignore[assignment]

            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Updated session {session_id}: status={status}, progress={progress_percent}%")
            return session

        except Exception:
            self.db.rollback()
            raise
