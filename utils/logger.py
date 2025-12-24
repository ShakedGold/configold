import logging
import logging.config
from typing import Any

import yaml


def setup_logger():
    with open("logger.yml", "r") as f:
        config: dict[str, Any] = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
