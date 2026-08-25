from unittest import mock

import pytest
import responses as responses_module

from cloudscale.http import RestAPIClient

API_URL = "https://api.example.com/v1"


@pytest.fixture
def client():
    with RestAPIClient(
        api_url=API_URL, api_token="token", user_agent="test-agent", timeout=3
    ) as client:
        yield client


def test_headers(client):
    assert client.headers == {
        "Authorization": "Bearer token",
        "Content-type": "application/json",
        "User-Agent": "test-agent",
    }


def test_get_collection(responses, client):
    responses.get(f"{API_URL}/servers", json=[{"uuid": "1"}], status=200)

    assert client.get_resources("servers") == {
        "status_code": 200,
        "data": [{"uuid": "1"}],
    }


def test_get_by_id(responses, client):
    responses.get(f"{API_URL}/servers/1", json={"uuid": "1"}, status=200)

    assert client.get_resources("servers", resource_id="1")["data"] == {"uuid": "1"}


def test_get_with_query(responses, client):
    responses.get(
        f"{API_URL}/servers",
        json=[],
        status=200,
        match=[responses_module.matchers.query_string_matcher("tag:project=gemini")],
    )

    client.get_resources("servers", payload={"tag:project": "gemini"})


def test_get_with_valueless_query_key(responses, client):
    responses.get(
        f"{API_URL}/servers",
        json=[],
        status=200,
        match=[responses_module.matchers.query_string_matcher("tag:project")],
    )

    client.get_resources("servers", payload={"tag:project": None})


def test_non_json_body_yields_empty_data(responses, client):
    responses.delete(f"{API_URL}/servers/1", body="", status=204)

    assert client.delete_resource("servers", resource_id="1") == {
        "status_code": 204,
        "data": {},
    }


def test_create_posts_to_collection(responses, client):
    responses.post(
        f"{API_URL}/servers",
        json={"uuid": "1"},
        status=201,
        match=[responses_module.matchers.json_params_matcher({"name": "db"})],
    )

    client.post_patch_resource("servers", payload={"name": "db", "zone": None})


def test_update_patches_the_resource(responses, client):
    responses.patch(
        f"{API_URL}/servers/1",
        json={"uuid": "1"},
        status=200,
        match=[responses_module.matchers.json_params_matcher({"name": "db"})],
    )

    client.post_patch_resource("servers", resource_id="1", payload={"name": "db"})


def test_action_posts_to_the_sub_path(responses, client):
    responses.post(
        f"{API_URL}/servers/1/start",
        status=204,
        match=[responses_module.matchers.json_params_matcher({})],
    )

    client.post_patch_resource("servers", resource_id="1", action="start")


def test_timeout_is_passed_through(responses, client):
    responses.get(f"{API_URL}/servers", json=[], status=200)

    client.get_resources("servers")
    assert responses.calls[0].request.req_kwargs["timeout"] == 3


def test_close_closes_the_session():
    client = RestAPIClient(api_url=API_URL, api_token="token", user_agent="test-agent")
    assert client.timeout == 60

    with mock.patch.object(client._session, "close") as close:
        client.close()

    close.assert_called_once_with()
