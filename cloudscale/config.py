"""Discovery and parsing of the ``cloudscale.ini`` config file."""

import configparser
import os
from pathlib import Path

from .error import CloudscaleException
from .log import logger

CLOUDSCALE_CONFIG = "cloudscale.ini"


def _xdg_config_home() -> Path:
    """Returns ``$XDG_CONFIG_HOME`` with the freedesktop.org default applied."""
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def config_file_paths() -> tuple[str, ...]:
    """Returns the config file locations, in ascending order of precedence."""
    config_file = os.getenv("CLOUDSCALE_CONFIG", CLOUDSCALE_CONFIG)
    return (
        str(_xdg_config_home() / "cloudscale" / config_file),
        str(Path.home() / f".{config_file}"),
        str(Path.cwd() / config_file),
    )


def read_config(profile: str = "") -> dict[str, str]:
    """Reads a profile from the config files.

    Args:
        profile (str, optional): Section to read. Defaults to the section named
            by ``$CLOUDSCALE_PROFILE``, or ``default``.

    Raises:
        CloudscaleException: An explicitly requested profile was not found.

    Returns:
        dict: The key/value pairs of the profile, empty if it does not exist.
    """
    paths = config_file_paths()

    conf = configparser.ConfigParser()
    conf.read(paths)

    if profile:
        if not conf.has_section(profile):
            raise CloudscaleException(
                f"Profile '{profile}' not found in config files: ({', '.join(paths)})"
            )
    else:
        profile = os.getenv("CLOUDSCALE_PROFILE", "default")

    logger.info("Using profile %s", profile)

    if not conf.has_section(profile):
        return {}

    return dict(conf[profile])
