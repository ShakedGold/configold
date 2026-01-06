import logging
import sys
from typing import Generic, TypeVar, override

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from utils import find_executable

T = TypeVar("T")


class BinaryRequirement(Generic[T]):
    """
    Used for enforcing requirements that rely on specific binaries to be in the PATH, intended to be used as a string
    """

    def __init__(self, value: T, binaries: list[str], must_have: bool = True) -> None:
        self.value: T = value
        self.binaries: list[str] = binaries
        self.must_have: bool = must_have
        self.logger: logging.Logger = logging.getLogger(
            f"{__name__}.{type(self).__name__}"
        )

    def get_missing_binaries(self) -> list[str]:
        missing_binaries: list[str] = []
        for binary in self.binaries:
            path: str | None = find_executable(binary)

            if path is None:
                missing_binaries.append(binary)

        return missing_binaries

    def validate(self) -> None:
        missing_binaries = self.get_missing_binaries()
        if len(missing_binaries) == 0:
            return

        missing_message: str = (
            f"Missing binaries for: {self.value}, the missing binaries are: {", ".join(missing_binaries)}"
        )
        if self.must_have:
            self.logger.fatal(missing_message)
            sys.exit(1)

        self.logger.warning(missing_message)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    @override
    def __str__(self) -> str:
        self.validate()
        return str(self.value)
