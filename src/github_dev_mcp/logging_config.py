import logging
import structlog

from github_dev_mcp.config import settings


def configure_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level)
    )