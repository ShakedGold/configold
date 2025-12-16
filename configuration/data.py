import logging
from typing import Any, override
from pydantic import BaseModel


class ConfigurationData(BaseModel):
    """
    Holds the data of the configuration
    """

    logger: Any = logging.Logger("")

    @override
    def model_post_init(self, context: Any, /) -> None:
        super().model_post_init(context)

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

    def config(self) -> bool:
        raise NotImplementedError
