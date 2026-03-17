import sys
import os
import logging

# Set up basic logging for Vercel diagnostic
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from main import app
    logger.info("Successfully imported app from main")
except Exception as e:
    logger.error(f"Failed to import app from main: {e}")
    # Fallback or re-raise if fatal
    raise
