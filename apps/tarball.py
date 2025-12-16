import os
from pathlib import PosixPath
import shutil
import subprocess
import sys
from typing import override
from apps import consts
from apps.installable_app import InstallableApp
from configuration import Configuration


class TarballApp(InstallableApp):
    """
    An installer for any tarball application
    """

    BINARIES: dict[str, str | None] = {"tar": None}
    UNARCHIVE_DIRECTORY_PREFIX: str = "-dir"

    def __init__(
        self,
        configuration: Configuration,
        link_path: PosixPath,
        detail: str = "",
        strip_components: bool = False,
    ) -> None:
        super().__init__(
            label=type(self).BINARY_NAME,
            detail=detail,
            configuration=configuration,
        )

        self.strip_components: bool = strip_components
        self.link_path: PosixPath = link_path

    @property
    def archive_name(self):
        return f"{self.full_source_path}.tar.gz"

    @property
    def full_link_path(self):
        return PosixPath(
            self.full_target_directory_path,
            f"{type(self).BINARY_NAME}{type(self).UNARCHIVE_DIRECTORY_PREFIX}",
            self.link_path,
        )

    @override
    async def _install(self) -> bool:
        tar_path: str = self.get_binary_path("tar")
        self.logger.debug(f"Binary path of tar ({tar_path})")

        self.logger.debug(
            f"Making sure that the source unarchive directory exists ({self.full_target_directory_path})"
        )
        self.full_source_path.mkdir(parents=True, exist_ok=True)

        tar_unarchive_args = [
            tar_path,
            "-xzf",
            self.archive_name,
            "-C",
            self.full_source_path.as_posix(),
        ]

        if self.strip_components:
            tar_unarchive_args += ["--strip-components=1"]

        self.logger.debug(
            f"Creating tar subprocess to un-archive the gzip ({' '.join(tar_unarchive_args)})"
        )

        unarchive_process = subprocess.Popen(
            tar_unarchive_args,
            cwd=self.full_source_directory,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        return_code = unarchive_process.wait()
        if return_code != consts.RETURN_CODE_SUCCESS:
            return False

        self.logger.debug("Un-archived the gzip archive successfully")

        target_unarchive_path = (
            f"{self.full_target_path.as_posix()}{type(self).UNARCHIVE_DIRECTORY_PREFIX}"
        )

        try:
            _ = shutil.move(self.full_source_path.as_posix(), target_unarchive_path)
            self.logger.debug(
                f"Moved the executable to the target path ({target_unarchive_path})"
            )
        except shutil.Error:
            self.logger.warning(
                f"Failed to move the target directory, file already exists in: {target_unarchive_path}"
            )
            return False

        try:
            os.symlink(self.full_link_path.as_posix(), self.full_target_path.as_posix())
            self.logger.debug(
                f"Linked the binary to the bin folder ({self.full_link_path})"
            )
        except FileExistsError:
            self.logger.warning(
                f"Failed to move the target directory, file already exists in: {target_unarchive_path}"
            )
            return False

        return True
