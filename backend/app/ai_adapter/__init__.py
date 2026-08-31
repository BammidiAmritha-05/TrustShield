import os
import sys
import logging
from app.config import settings

logger = logging.getLogger("trustshield-backend.ai_adapter")


def bootstrap_ai_root() -> bool:
    """
    Centrally configures sys.path so the backend can import the existing TrustShield AI package.
    Uses settings.TRUSTSHIELD_AI_ROOT without hardcoding machine-specific absolute paths.
    """
    ai_root = settings.TRUSTSHIELD_AI_ROOT or os.getenv("TRUSTSHIELD_AI_ROOT", "")
    if not ai_root:
        logger.warning("TRUSTSHIELD_AI_ROOT is not configured.")
        return False

    ai_root_path = os.path.abspath(ai_root)
    if not os.path.exists(ai_root_path):
        logger.warning(f"TRUSTSHIELD_AI_ROOT directory does not exist: {ai_root_path}")
        return False

    # The AI package is inside D:\TrustShield\ai (or parent D:\TrustShield for `import ai`)
    parent_dir = os.path.dirname(ai_root_path)

    for path in [parent_dir, ai_root_path]:
        if path and os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            logger.info(f"Added {path} to sys.path for AI module imports.")

    return True
