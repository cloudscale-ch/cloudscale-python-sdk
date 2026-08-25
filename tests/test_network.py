import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "2db69ba3-1864-4608-853a-0771b6885a3a"

NETWORK_RESP = {
    "href": f"https://api.cloudscale.ch/v1/networks/{UUID}",
    "uuid": UUID,
    "name": "my-network-name",
    "created_at": "2019-05-29T13:18:42.511407Z",
    "zone": {"slug": "lpg1"},
    "mtu": 9000,
    "subnets": [
        {
            "href": "https://api.cloudscale.ch/v1/subnets/33333333-1864-4608-853a-0771b6885a3a",
            "uuid": "33333333-1864-4608-853a-0771b6885a3a",
            "cidr": "172.16.0.0/24",
        }
    ],
    "tags": {},
}


def test_network_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/networks", json=[NETWORK_RESP], status=200)

    networks = cloudscale.network.get_all()
    assert networks[0]["name"] == "my-network-name"
    assert networks[0]["uuid"] == UUID


def test_network_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/networks/{UUID}", json=NETWORK_RESP, status=200)

    network = cloudscale.network.get_by_uuid(uuid=UUID)
    assert network["name"] == "my-network-name"


def test_network_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/networks/{UUID}", status=204)

    assert not cloudscale.network.delete(uuid=UUID)


def test_network_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/networks/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.network.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_network_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/networks",
        json=NETWORK_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "my-network-name",
                    "zone": "lpg1",
                    "mtu": 9000,
                    "auto_create_ipv4_subnet": False,
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    network = cloudscale.network.create(
        name="my-network-name",
        zone="lpg1",
        mtu=9000,
        auto_create_ipv4_subnet=False,
        tags={"project": "apollo"},
    )
    assert network["uuid"] == UUID


def test_network_create_minimal(responses, cloudscale):
    responses.post(
        f"{API_URL}/networks",
        json=NETWORK_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher({"name": "my-network-name"})
        ],
    )

    cloudscale.network.create(name="my-network-name")


def test_network_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/networks/{UUID}",
        json=NETWORK_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {"name": "my-network-name", "mtu": 1500, "tags": {}}
            )
        ],
    )

    network = cloudscale.network.update(
        uuid=UUID, name="my-network-name", mtu=1500, tags={}
    )
    assert network["uuid"] == UUID
