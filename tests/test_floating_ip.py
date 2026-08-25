import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

NETWORK_ID = "192.0.2.123"

FLOATING_IP_RESP = {
    "href": f"https://api.cloudscale.ch/v1/floating-ips/{NETWORK_ID}",
    "created_at": "2019-05-29T13:18:42.505197Z",
    "network": f"{NETWORK_ID}/32",
    "ip_version": 4,
    "server": {
        "href": "https://api.cloudscale.ch/v1/servers/47cec963-fcd2-482f-bdb6-24461b2d47b1",
        "uuid": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
        "name": "db-master",
    },
    "region": {"slug": "lpg"},
    "next_hop": "198.51.100.1",
    "reverse_ptr": "192.0.2.123.cust.cloudscale.ch",
    "tags": {},
}


def test_floating_ip_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/floating-ips", json=[FLOATING_IP_RESP], status=200)

    floating_ips = cloudscale.floating_ip.get_all()
    assert floating_ips[0]["network"] == f"{NETWORK_ID}/32"
    assert floating_ips[0]["ip_version"] == 4


def test_floating_ip_get_by_uuid(responses, cloudscale):
    responses.get(
        f"{API_URL}/floating-ips/{NETWORK_ID}", json=FLOATING_IP_RESP, status=200
    )

    floating_ip = cloudscale.floating_ip.get_by_uuid(uuid=NETWORK_ID)
    assert floating_ip["network"] == f"{NETWORK_ID}/32"


def test_floating_ip_get_by_uuid_not_found(responses, cloudscale):
    responses.get(
        f"{API_URL}/floating-ips/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.floating_ip.get_by_uuid(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_floating_ip_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/floating-ips/{NETWORK_ID}", status=204)

    assert not cloudscale.floating_ip.delete(uuid=NETWORK_ID)


def test_floating_ip_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/floating-ips",
        json=FLOATING_IP_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "ip_version": 4,
                    "prefix_length": 32,
                    "reverse_ptr": "192.0.2.123.cust.cloudscale.ch",
                    "server": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
                    "type": "regional",
                    "region": "lpg",
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    floating_ip = cloudscale.floating_ip.create(
        ip_version=4,
        prefix_length=32,
        reverse_ptr="192.0.2.123.cust.cloudscale.ch",
        server_uuid="47cec963-fcd2-482f-bdb6-24461b2d47b1",
        scope="regional",
        region="lpg",
        tags={"project": "apollo"},
    )
    assert floating_ip["ip_version"] == 4


def test_floating_ip_create_error(responses, cloudscale):
    responses.post(
        f"{API_URL}/floating-ips", json={"detail": "Bad request."}, status=400
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.floating_ip.create(ip_version=4)

    assert exc_info.value.status_code == 400


def test_floating_ip_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/floating-ips/{NETWORK_ID}",
        json=FLOATING_IP_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "reverse_ptr": "192.0.2.123.cust.cloudscale.ch",
                    "server": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
                    "tags": {},
                }
            )
        ],
    )

    floating_ip = cloudscale.floating_ip.update(
        uuid=NETWORK_ID,
        reverse_ptr="192.0.2.123.cust.cloudscale.ch",
        server_uuid="47cec963-fcd2-482f-bdb6-24461b2d47b1",
        tags={},
    )
    assert floating_ip["network"] == f"{NETWORK_ID}/32"
