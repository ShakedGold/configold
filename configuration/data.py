from dataclasses import make_dataclass
import logging
import os
from pathlib import PosixPath
from pprint import pformat
import shutil
from typing import Any, ClassVar, Self, override
from pydantic import BaseModel, ConfigDict, Field, SkipValidation

import warnings

from pydantic.json_schema import PydanticJsonSchemaWarning

warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)


class ConfigurationData(BaseModel):
    """
    Holds the data of the configuration
    """

    CONFIG_NAME: ClassVar[str] = ""
    CONFIG_FILE_NAME: ClassVar[str] = ""

    model_config = ConfigDict(use_attribute_docstrings=True)
    backup_directory_path: PosixPath = Field(
        default_factory=lambda: PosixPath(os.getenv("HOME", "~"), ".local", "backups")
    )
    logger: Any = logging.Logger("")

    descriptions: SkipValidation[Self] = {}  # pyright: ignore[reportAssignmentType]

    @property
    def resources_path(self) -> PosixPath:
        return PosixPath(
            os.getcwd(), "apps", type(self).CONFIG_NAME, "resources"
        ).resolve()

    @property
    def home_path(self):
        home_path = os.getenv("HOME")
        if home_path is None:
            home_path = "~"
        return home_path

    @property
    def config_path(self) -> PosixPath:
        return PosixPath(self.home_path, type(self).CONFIG_FILE_NAME)

    @override
    def model_post_init(self, context: Any, /) -> None:
        super().model_post_init(context)

        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

        """
        This ugly thing is because we want to have access to the descriptions of the properties of the model, and have type hinting on that, so we create a dynamic dataclass type and instantiate it.
        We basically convert all of the model to json and extract only the description to set it in the description dict which is marked as Self to allow type hinting with the names
        of the properties
        NOTE: The types of the properties themselves in the descriptions property should be ignored, they are all strings

        I should create a better way for this, but for now this is it.
        The type hinting system does not like this...
        """
        schema_defs: dict[str, dict[str, Any]] = self.model_json_schema().get("$defs")  # pyright: ignore[reportAssignmentType,reportExplicitAny]
        data_key: str = list(schema_defs.keys())[0]
        properties: dict[str, dict[str, str]] = schema_defs.get(data_key, {}).get(
            "properties"
        )  # pyright: ignore[reportAssignmentType]

        descriptions_class: type = make_dataclass(
            "descriptions",
            ((property_name, str) for property_name in properties),
        )
        self.descriptions = descriptions_class(
            **{
                property_name: property_value.get("description")
                for property_name, property_value in properties.items()
            }
        )

    def _config(self) -> bool:
        raise NotImplementedError

    def _backup_config(self) -> None:
        self.backup_directory_path.mkdir(parents=True, exist_ok=True)

        target_backup_directory_path = PosixPath(
            self.backup_directory_path, type(self).CONFIG_NAME
        )

        self.logger.debug(
            "backup path: %s, config_path: %s",
            target_backup_directory_path,
            self.config_path,
        )

        target_backup_directory_path.mkdir(parents=True, exist_ok=True)

        _ = shutil.copy(
            self.config_path,
            target_backup_directory_path,
        )
        self.logger.debug(
            f"Backed up the config ([{self.config_path}] to [{self.backup_directory_path}])"
        )

    def config(self) -> bool:
        self.logger.debug("Configuration: %s", pformat(dict(self)))

        if self.config_path.exists():
            self.logger.debug(f"Configuration file exists ({self.config_path})")
            self._backup_config()

            self.config_path.unlink()
            self.logger.debug(f"Removed config file ({self.config_path})")

        return self._config()
