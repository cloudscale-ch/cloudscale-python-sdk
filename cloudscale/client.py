"""The :class:`Cloudscale` client, entry point of the SDK."""

import logging
import os
from types import TracebackType

from .config import read_config
from .error import CloudscaleException
from .http import RestAPIClient
from .lib.custom_image import CustomImage
from .lib.flavor import Flavor
from .lib.floating_ip import FloatingIp
from .lib.image import Image
from .lib.network import Network
from .lib.objects_user import ObjectsUser
from .lib.region import Region
from .lib.server import Server
from .lib.server_group import ServerGroup
from .lib.subnet import Subnet
from .lib.volume import Volume
from .log import logger
from .version import __version__

CLOUDSCALE_API_URL = os.getenv("CLOUDSCALE_API_URL", "https://api.cloudscale.ch/v1")

DEFAULT_TIMEOUT = 60


class Cloudscale:
    """Client for the cloudscale.ch API.

    Each API resource is available as an attribute, e.g. ``cloudscale.server``.
    """

    api_url = CLOUDSCALE_API_URL
    version = __version__

    def __init__(self, api_token: str = "", profile: str = "", debug: bool = False):
        """Cloudscale

        Args:
            api_token (str, optional): API token. Defaults to None.
            profile (str, optional): Section to use in cloudscale.ini. Defaults to None.
            debug (bool, optional): Enable debug logging. Defaults to False.

        Raises:
            CloudscaleException: Exception related to API token handling.
        """
        if debug:
            logger.setLevel(logging.DEBUG)

        logger.info("Started, version: %s", self.version)

        if api_token and profile:
            raise CloudscaleException("API token and profile are mutually exclusive")

        # Read ini configs
        self.config = read_config(profile=profile)

        self.api_token: str = api_token or self.config.get("api_token", "")
        if not self.api_token:
            raise CloudscaleException("Missing API key")

        logger.info("API Token used: %s...", self.api_token[:4])

        # Configure requests timeout
        self.timeout: int = int(self.config.get("timeout", DEFAULT_TIMEOUT))
        logger.debug("Timeout is: %s", self.timeout)

        self._client = RestAPIClient(
            api_token=self.api_token,
            api_url=self.api_url,
            user_agent=f"cloudscale-sdk {self.version}",
            timeout=self.timeout,
        )

        # Resource attributes
        self.custom_image = CustomImage(self)
        self.flavor = Flavor(self)
        self.floating_ip = FloatingIp(self)
        self.image = Image(self)
        self.network = Network(self)
        self.objects_user = ObjectsUser(self)
        self.region = Region(self)
        self.server = Server(self)
        self.server_group = ServerGroup(self)
        self.subnet = Subnet(self)
        self.volume = Volume(self)

    def _read_from_configfile(self, profile: str = "") -> dict:
        """Deprecated, use :func:`cloudscale.config.read_config` instead."""
        return read_config(profile=profile)

    def close(self) -> None:
        """Closes the underlying HTTP session."""
        self._client.close()

    def __enter__(self) -> "Cloudscale":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
