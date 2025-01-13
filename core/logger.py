import logging
import sys
from fastapi.logger import logger as fastapi_logger


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[1;31m",  # Bright/Bold Red
        "CRITICAL": "\033[0;35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }
    APP_COLOR = "\033[1;34m"  # Bright Blue

    def format(self, record):
        log_message = super().format(record)
        if record.name == "video_generation":
            return f"{self.APP_COLOR}{record.levelname}:{self.COLORS['RESET']}     {log_message}"
        else:
            return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{record.levelname}:{self.COLORS['RESET']}     {log_message}"


def setup_logger():
    # Configure logging
    LOGGER = logging.getLogger("video_generation")
    LOGGER.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler("video_generation.log")
    file_handler.setLevel(logging.DEBUG)

    # Create a stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)

    # Create logging formats
    file_formatter = logging.Formatter("%(levelname)s: %(message)s")
    stream_formatter = ColoredFormatter("%(message)s")

    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)

    # Add the handlers to the logger
    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stream_handler)

    # Suppress Numba logs
    logging.getLogger("numba").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    # Connect FastAPI logger
    fastapi_logger.handlers = LOGGER.handlers
    fastapi_logger.setLevel(LOGGER.level)

    return LOGGER


LOGGER = setup_logger()
