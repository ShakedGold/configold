import logging
import logging.config
from typing import Any

import yaml

def setup_logger(console=True):
    with open("logger.yml", "r") as f:
        config: dict[str, Any] = yaml.safe_load(f.read())

        if console:
            config['root']['handlers'].append('console')
            config['loggers']['app']['handlers'].append('console')

        logging.config.dictConfig(config)
