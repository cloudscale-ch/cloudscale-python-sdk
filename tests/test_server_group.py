import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "e3b63018-fad6-45f2-9f57-3ea0da726d8c"

SERVER_GROUP_RESP = {
    "href": f"https://api.cloudscale.ch/v1/server-groups/{UUID}",
    "uuid": UUID,
    "name": "load balancers",
    "type": "anti-affinity",
    "zone": {"slug": "lpg1"},
    "servers": [
        {
            "href": "https://api.cloudscale.ch/v1/servers/32d2f586-14ff-4da9-81df-134ca45d635f",
            "uuid": "32d2f586-14ff-4da9-81df-134ca45d635f",
            "name": "tesla",
        }
    ],
    "tags": {},
}


def test_server_group_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/server-groups", json=[SERVER_GROUP_RESP], status=200)

    server_groups = cloudscale.server_group.get_all()
    assert server_groups[0]["name"] == "load balancers"
    assert server_groups[0]["uuid"] == UUID


def test_server_group_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/server-groups/{UUID}", json=SERVER_GROUP_RESP, status=200)

    server_group = cloudscale.server_group.get_by_uuid(uuid=UUID)
    assert server_group["type"] == "anti-affinity"


def test_server_group_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/server-groups/{UUID}", status=204)

    assert not cloudscale.server_group.delete(uuid=UUID)


def test_server_group_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/server-groups/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server_group.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_server_group_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/server-groups",
        json=SERVER_GROUP_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "load balancers",
                    "type": "anti-affinity",
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    server_group = cloudscale.server_group.create(
        name="load balancers",
        group_type="anti-affinity",
        tags={"project": "apollo"},
    )
    assert server_group["uuid"] == UUID


def test_server_group_create_error(responses, cloudscale):
    responses.post(f"{API_URL}/server-groups", json={"detail": "Bad."}, status=400)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server_group.create(name="load balancers")

    assert exc_info.value.status_code == 400


def test_server_group_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/server-groups/{UUID}",
        json=SERVER_GROUP_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {"name": "load balancers", "tags": {}}
            )
        ],
    )

    server_group = cloudscale.server_group.update(
        uuid=UUID, name="load balancers", tags={}
    )
    assert server_group["uuid"] == UUID
