import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "33333333-1864-4608-853a-0771b6885a3a"
NETWORK_UUID = "2db69ba3-1864-4608-853a-0771b6885a3a"

SUBNET_RESP = {
    "href": f"https://api.cloudscale.ch/v1/subnets/{UUID}",
    "uuid": UUID,
    "cidr": "192.0.2.123/24",
    "network": {
        "href": f"https://api.cloudscale.ch/v1/networks/{NETWORK_UUID}",
        "uuid": NETWORK_UUID,
        "name": "my-network-name",
    },
    "gateway_address": None,
    "dns_servers": ["185.79.232.101", "185.79.232.102"],
    "tags": {},
}


def test_subnet_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/subnets", json=[SUBNET_RESP], status=200)

    subnets = cloudscale.subnet.get_all()
    assert subnets[0]["cidr"] == "192.0.2.123/24"
    assert subnets[0]["uuid"] == UUID


def test_subnet_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/subnets/{UUID}", json=SUBNET_RESP, status=200)

    subnet = cloudscale.subnet.get_by_uuid(uuid=UUID)
    assert subnet["uuid"] == UUID


def test_subnet_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/subnets/{UUID}", status=204)

    assert not cloudscale.subnet.delete(uuid=UUID)


def test_subnet_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/subnets/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.subnet.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_subnet_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/subnets",
        json=SUBNET_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "cidr": "192.0.2.123/24",
                    "network": NETWORK_UUID,
                    "gateway_address": "192.0.2.1",
                    "dns_servers": ["185.79.232.101"],
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    subnet = cloudscale.subnet.create(
        cidr="192.0.2.123/24",
        network_uuid=NETWORK_UUID,
        gateway_address="192.0.2.1",
        dns_servers=["185.79.232.101"],
        tags={"project": "apollo"},
    )
    assert subnet["uuid"] == UUID


def test_subnet_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/subnets/{UUID}",
        json=SUBNET_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "gateway_address": "192.0.2.1",
                    "dns_servers": ["185.79.232.101", "185.79.232.102"],
                    "tags": {},
                }
            )
        ],
    )

    subnet = cloudscale.subnet.update(
        uuid=UUID,
        gateway_address="192.0.2.1",
        dns_servers=["185.79.232.101", "185.79.232.102"],
        tags={},
    )
    assert subnet["uuid"] == UUID
