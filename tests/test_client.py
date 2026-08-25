import logging
from unittest import mock

import pytest

from cloudscale import Cloudscale, CloudscaleException
from cloudscale.client import CLOUDSCALE_API_URL
from cloudscale.log import logger


def write_config(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_api_token_argument():
    cloudscale = Cloudscale(api_token="token")
    assert cloudscale.api_token == "token"
    assert cloudscale.api_url == CLOUDSCALE_API_URL
    assert cloudscale.timeout == 60
    assert cloudscale.config == {}


def test_missing_api_token():
    with pytest.raises(CloudscaleException, match=r"^Missing API key$"):
        Cloudscale()


def test_api_token_and_profile_are_mutually_exclusive():
    with pytest.raises(
        CloudscaleException, match=r"^API token and profile are mutually exclusive$"
    ):
        Cloudscale(api_token="token", profile="test")


def test_api_token_from_default_profile(isolated_env):
    write_config(
        isolated_env / ".cloudscale.ini", "[default]\napi_token = default_token\n"
    )

    cloudscale = Cloudscale()
    assert cloudscale.api_token == "default_token"


def test_api_token_from_named_profile(isolated_env):
    write_config(isolated_env / ".cloudscale.ini", "[test]\napi_token = test_token\n")

    cloudscale = Cloudscale(profile="test")
    assert cloudscale.api_token == "test_token"


def test_timeout_from_profile(isolated_env):
    write_config(
        isolated_env / ".cloudscale.ini",
        "[default]\napi_token = default_token\ntimeout = 5\n",
    )

    cloudscale = Cloudscale()
    assert cloudscale.timeout == 5
    assert cloudscale._client.timeout == 5


def test_unknown_profile_raises(isolated_env):
    with pytest.raises(CloudscaleException, match="Profile 'does-not-exist' not found"):
        Cloudscale(profile="does-not-exist")


def test_debug_enables_debug_logging():
    original_level = logger.level
    try:
        Cloudscale(api_token="token", debug=True)
        assert logger.level == logging.DEBUG
    finally:
        logger.setLevel(original_level)


def test_deprecated_read_from_configfile(isolated_env):
    write_config(
        isolated_env / ".cloudscale.ini", "[default]\napi_token = default_token\n"
    )

    cloudscale = Cloudscale(api_token="token")
    assert cloudscale._read_from_configfile() == {"api_token": "default_token"}


def test_all_resources_share_one_http_client(cloudscale):
    assert cloudscale.custom_image._client is cloudscale._client
    assert cloudscale.volume._client is cloudscale._client


@pytest.mark.parametrize(
    "name",
    [
        "custom_image",
        "flavor",
        "floating_ip",
        "image",
        "network",
        "objects_user",
        "region",
        "server",
        "server_group",
        "subnet",
        "volume",
    ],
)
def test_resource_attributes(cloudscale, name):
    assert getattr(cloudscale, name).resource


def test_close_is_idempotent():
    cloudscale = Cloudscale(api_token="token")
    cloudscale.close()
    cloudscale.close()


def test_context_manager_closes_session():
    cloudscale = Cloudscale(api_token="token")

    with mock.patch.object(cloudscale._client, "close") as close, cloudscale:
        pass

    close.assert_called_once_with()
