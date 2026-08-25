"""Locks down the public API surface of releases before 0.8.0."""

import cloudscale
import cloudscale.error
import cloudscale.http
import cloudscale.lib
import cloudscale.log
import cloudscale.version


def test_top_level_names():
    from cloudscale import (  # noqa: F401
        CLOUDSCALE_API_URL,
        CLOUDSCALE_CONFIG,
        Cloudscale,
        CloudscaleApiException,
        CloudscaleException,
    )

    assert CLOUDSCALE_CONFIG == "cloudscale.ini"
    assert CLOUDSCALE_API_URL.startswith("http")


def test_base_classes_importable_from_lib():
    from cloudscale.lib import (  # noqa: F401
        CloudscaleApiException,
        CloudscaleBase,
        CloudscaleBaseExt,
        CloudscaleException,
        CloudscaleMutable,
    )


def test_resource_classes_keep_their_modules():
    from cloudscale.lib.custom_image import CustomImage
    from cloudscale.lib.flavor import Flavor
    from cloudscale.lib.floating_ip import FloatingIp
    from cloudscale.lib.image import Image
    from cloudscale.lib.network import Network
    from cloudscale.lib.objects_user import ObjectsUser
    from cloudscale.lib.region import Region
    from cloudscale.lib.server import Server
    from cloudscale.lib.server_group import ServerGroup
    from cloudscale.lib.subnet import Subnet
    from cloudscale.lib.volume import Volume

    assert CustomImage.resource == "custom-images"
    assert Flavor.resource == "flavors"
    assert FloatingIp.resource == "floating-ips"
    assert Image.resource == "images"
    assert Network.resource == "networks"
    assert ObjectsUser.resource == "objects-users"
    assert Region.resource == "regions"
    assert Server.resource == "servers"
    assert ServerGroup.resource == "server-groups"
    assert Subnet.resource == "subnets"
    assert Volume.resource == "volumes"


def test_rest_api_client_and_logger():
    from cloudscale.http import RestAPIClient

    assert RestAPIClient
    assert cloudscale.log.logger.name == "cloudscale.log"


def test_version_module():
    assert cloudscale.version.__version__ == cloudscale.__version__


def test_api_exception_signature():
    error = cloudscale.CloudscaleApiException(
        "boom", response={"status_code": 500, "data": {}}, status_code=500
    )
    assert str(error) == "boom"
    assert error.status_code == 500
    assert error.response == {"status_code": 500, "data": {}}
    assert isinstance(error, Exception)
    assert not isinstance(error, cloudscale.CloudscaleException)
