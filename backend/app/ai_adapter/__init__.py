from pathlib import Path
import os
import sys
import logging

from app.config import settings

logger = logging.getLogger("trustshield-backend.ai_adapter")


def bootstrap_ai_root() -> bool:
    """
    Configure sys.path for the TrustShield AI package.

    Behavior:
    - If TRUSTSHIELD_AI_ROOT is explicitly configured, use it.
    - If it is unset (None), automatically discover the repository's ai/ folder.
    - If it is explicitly empty or points to a missing directory, report unavailable.
    """
    configured_root = settings.TRUSTSHIELD_AI_ROOT

    # Explicitly configured path.
    if configured_root is not None:
        if not configured_root.strip():
            logger.warning("TRUSTSHIELD_AI_ROOT is explicitly empty.")
            return False

        ai_root_path = Path(configured_root).expanduser().resolve()

        if not ai_root_path.is_dir():
            logger.warning(
                "TRUSTSHIELD_AI_ROOT directory does not exist: %s",
                ai_root_path,
            )
            return False

    # No configured path: discover the repository-level ai/ directory.
    else:
        # __file__:
        # <repo>/backend/app/ai_adapter/__init__.py
        repo_root = Path(__file__).resolve().parents[3]
        ai_root_path = repo_root / "ai"

        if not ai_root_path.is_dir():
            logger.warning(
                "Auto-discovered AI directory does not exist: %s",
                ai_root_path,
            )
            return False

        logger.info("Auto-discovered TrustShield AI root: %s", ai_root_path)

    parent_dir = ai_root_path.parent

    for path in (parent_dir, ai_root_path):
        path_str = os.fspath(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
            logger.info("Added %s to sys.path for AI module imports.", path)

    return True