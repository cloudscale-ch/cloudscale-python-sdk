"""A Python SDK for the cloudscale.ch API."""

from .client import CLOUDSCALE_API_URL, Cloudscale
from .config import CLOUDSCALE_CONFIG
from .error import CloudscaleApiException, CloudscaleException
from .version import __version__

__all__ = [
    "CLOUDSCALE_API_URL",
    "CLOUDSCALE_CONFIG",
    "Cloudscale",
    "CloudscaleApiException",
    "CloudscaleException",
    "__version__",
]
