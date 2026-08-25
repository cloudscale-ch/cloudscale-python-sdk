import logging
import os

logging.basicConfig(
    level=os.environ.get("CLOUDSCALE_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s:%(levelname)s:%(message)s",
)

logger = logging.getLogger(__name__)
logger.debug("Init")
