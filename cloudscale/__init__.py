import os
import configparser
import logging
from xdg import XDG_CONFIG_HOME

from .http import RestAPIClient
from .lib.server import Server
from .lib.server_group import ServerGroup
from .lib.volume import Volume
from .lib.flavor import Flavor
from .lib.floating_ip import FloatingIp
from .lib.image import Image
from .lib.region import Region
from .lib.network import Network
from .lib.subnet import Subnet
from .lib.objects_user import ObjectsUser

from .log import logger
from .error import CloudscaleException, CloudscaleApiException # noqa F401

from .version import __version__

CLOUDSCALE_API_URL = os.getenv('CLOUDSCALE_API_URL', 'https://api.cloudscale.ch/v1')
CLOUDSCALE_CONFIG = 'cloudscale.ini'


class Cloudscale:

    def __init__(self, api_token: str = None, profile: str = None, debug: bool = False):
        """Cloudscale

        Args:
            api_token (str, optional): API token. Defaults to None.
            profile (str, optional): Section to use in cloudscale.ini. Defaults to None.
            debug (bool, optional): Enable debug logging. Defaults to False.

        Raises:
            CloudscaleException: Exception related to API token handling.
        """
        if debug:
            logger.setLevel(logging.INFO)

        logger.info(f"Started, version: {__version__}")

        if api_token and profile:
            raise CloudscaleException("API token and profile are mutually exclusive")

        # Read ini configs
        self.config = self._read_from_configfile(profile=profile)

        if api_token:
            self.api_token = api_token
        else:
            self.api_token = self.config.get('api_token')

        if not self.api_token:
            raise CloudscaleException("Missing API key")

        logger.info(f"API Token used: {self.api_token[:4]}...")

        # Configre requests timeout
        self.timeout = self.config.get('timeout', 60)
        logger.debug(f"Timeout is: {self.timeout}")

        self.resource_classes = {
            'server': Server,
            'server_group': ServerGroup,
            'volume': Volume,
            'flavor': Flavor,
            'floating_ip': FloatingIp,
            'image': Image,
            'region': Region,
            'network': Network,
            'subnet': Subnet,
            'objects_user': ObjectsUser,
        }


    def _read_from_configfile(self, profile: str = None) -> dict:
        """Reads from config ini file.

        Args:
            profile (str, optional): Section to read. Defaults to None.

        Raises:
            CloudscaleException: Profile not found.

        Returns:
            dict: Read configs.
        """

        config_file = os.getenv('CLOUDSCALE_CONFIG', CLOUDSCALE_CONFIG)

        paths = (
            os.path.join(XDG_CONFIG_HOME, 'cloudscale', config_file),
            os.path.join(os.path.expanduser('~'), '.{}'.format(config_file)),
            os.path.join(os.getcwd(), config_file),
        )

        conf = configparser.ConfigParser()
        conf.read(paths)

        if profile:
            if profile not in conf._sections:
                raise CloudscaleException("Profile '{}' not found in config files: ({})".format(profile, ', '. join(paths)))
        else:
            profile = os.getenv('CLOUDSCALE_PROFILE', 'default')

        logger.info(f"Using profile {profile}")

        if not conf._sections.get(profile):
            return dict()

        return dict(conf.items(profile))


    def __getattr__(self, name: str) -> object:
        """Instantiates resource class.

        Args:
            name (str): Resource class name.

        Raises:
            NotImplementedError: Resource class not available.

        Returns:
            object: Resource class
        """
        try:
            client = RestAPIClient(
                api_token=self.api_token,
                api_url=CLOUDSCALE_API_URL,
                user_agent=f'cloudscale-sdk {__version__}',
                timeout=self.timeout,
            )
            obj = self.resource_classes[name]()
            obj._client = client
            return obj
        except KeyError as e:
            raise NotImplementedError(f"{e} not implemented")
