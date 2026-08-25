"""Tests for the behaviour shared by all resources."""

import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException
from cloudscale.lib import CloudscaleBase, CloudscaleBaseExt, CloudscaleMutable
from cloudscale.lib.base import _tag_filter_payload

from .conftest import API_URL


def test_inheritance_chain():
    assert issubclass(CloudscaleMutable, CloudscaleBaseExt)
    assert issubclass(CloudscaleBaseExt, CloudscaleBase)


@pytest.mark.parametrize(
    ("filter_tag", "expected"),
    [
        ("project=gemini", {"tag:project": "gemini"}),
        ("project", {"tag:project": None}),
        ("tag:project=gemini", {"tag:project": "gemini"}),
        ("tag:project", {"tag:project": None}),
        ("project=", {"tag:project": ""}),
    ],
)
def test_tag_filter_payload(filter_tag, expected):
    assert _tag_filter_payload(filter_tag) == expected


@pytest.mark.parametrize(
    ("filter_tag", "query_string"),
    [
        ("project=gemini", "tag:project=gemini"),
        ("project", "tag:project"),
    ],
)
def test_get_all_sends_the_tag_filter(responses, cloudscale, filter_tag, query_string):
    responses.get(
        f"{API_URL}/servers",
        json=[],
        status=200,
        match=[responses_module.matchers.query_string_matcher(query_string)],
    )

    assert cloudscale.server.get_all(filter_tag=filter_tag) == []


def test_get_all_returns_empty_list_without_data(responses, cloudscale):
    responses.get(f"{API_URL}/servers", body="", status=200)

    assert cloudscale.server.get_all() == []


def test_get_by_uuid_returns_empty_dict_without_data(responses, cloudscale):
    responses.get(f"{API_URL}/servers/1", body="", status=200)

    assert cloudscale.server.get_by_uuid(uuid="1") == {}


def test_error_message_uses_the_detail_field(responses, cloudscale):
    responses.get(f"{API_URL}/servers/1", json={"detail": "Not found."}, status=404)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server.get_by_uuid(uuid="1")

    error = exc_info.value
    assert str(error) == "API Response Error (404): Not found."
    assert error.status_code == 404
    assert error.response == {"status_code": 404, "data": {"detail": "Not found."}}


def test_error_message_falls_back_to_the_payload(responses, cloudscale):
    responses.get(f"{API_URL}/servers/1", json={}, status=500)

    with pytest.raises(
        CloudscaleApiException, match=r"^API Response Error \(500\): \{\}$"
    ):
        cloudscale.server.get_by_uuid(uuid="1")


def test_error_message_handles_a_list_payload(responses, cloudscale):
    responses.get(f"{API_URL}/servers/1", json=["boom"], status=400)

    with pytest.raises(
        CloudscaleApiException, match=r"^API Response Error \(400\): \['boom'\]$"
    ):
        cloudscale.server.get_by_uuid(uuid="1")


def test_error_message_without_a_body(responses, cloudscale):
    responses.get(f"{API_URL}/servers/1", body="", status=502)

    with pytest.raises(
        CloudscaleApiException, match=r"^API Response Error \(502\): \{\}$"
    ):
        cloudscale.server.get_by_uuid(uuid="1")


class DummyConfig:
    """A duck-typed stand-in for Cloudscale, as accepted before v0.8.0."""

    api_token = "token"
    api_url = API_URL
    version = "0.0.0"
    timeout = 12


def test_resource_accepts_a_duck_typed_config(responses):
    servers = CloudscaleBaseExt(DummyConfig())
    servers.resource = "servers"

    responses.get(f"{API_URL}/servers/1", json={"uuid": "1"}, status=200)

    assert servers.get_by_uuid(uuid="1") == {"uuid": "1"}
    assert servers._client.timeout == 12
    assert servers._client.headers["User-Agent"] == "cloudscale-sdk 0.0.0"
    servers._client.close()
