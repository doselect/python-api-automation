"""
Ports utils/logger.py from https://github.com/doselect/do-api-automation.git: one logger per
module name, logging to both a rotating-by-day file under `logs/` and the console.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

# python-api-automation/src/core/do_api_logger.py -> repo root is 2 parents up from this file's dir.
LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def setup_logger(name: str) -> logging.Logger:
    """Mirrors utils.logger.setup_logger(name)."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    log_file = LOGS_DIR / f"api_test_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
