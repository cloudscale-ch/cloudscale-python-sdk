import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "2db69ba3-1864-4608-853a-0771b6885a3a"
SERVER_UUID = "9e1f9a7f-e8d0-4086-ad7e-fea161d7c5f7"

VOLUME_RESP = {
    "href": f"https://api.cloudscale.ch/v1/volumes/{UUID}",
    "created_at": "2019-05-29T13:18:42.511407Z",
    "uuid": UUID,
    "name": "capitano-root",
    "zone": {"slug": "lpg1"},
    "size_gb": 150,
    "type": "ssd",
    "server_uuids": [SERVER_UUID],
    "tags": {},
}


def test_volume_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/volumes", json=[VOLUME_RESP], status=200)

    volumes = cloudscale.volume.get_all()
    assert volumes[0]["name"] == "capitano-root"
    assert volumes[0]["uuid"] == UUID


def test_volume_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/volumes/{UUID}", json=VOLUME_RESP, status=200)

    volume = cloudscale.volume.get_by_uuid(uuid=UUID)
    assert volume["size_gb"] == 150


def test_volume_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/volumes/{UUID}", status=204)

    assert not cloudscale.volume.delete(uuid=UUID)


def test_volume_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/volumes/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.volume.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_volume_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/volumes",
        json=VOLUME_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "capitano-root",
                    "server_uuids": [SERVER_UUID],
                    "size_gb": 150,
                    "type": "ssd",
                    "zone": "lpg1",
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    volume = cloudscale.volume.create(
        name="capitano-root",
        server_uuids=[SERVER_UUID],
        size_gb=150,
        volume_type="ssd",
        zone="lpg1",
        tags={"project": "apollo"},
    )
    assert volume["uuid"] == UUID


def test_volume_create_error(responses, cloudscale):
    responses.post(f"{API_URL}/volumes", json={"detail": "Bad."}, status=400)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.volume.create(
            name="capitano-root", server_uuids=[SERVER_UUID], size_gb=150
        )

    assert exc_info.value.status_code == 400


def test_volume_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/volumes/{UUID}",
        json=VOLUME_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "capitano-root",
                    "server_uuids": [SERVER_UUID],
                    "size_gb": 200,
                    "tags": {},
                }
            )
        ],
    )

    volume = cloudscale.volume.update(
        uuid=UUID,
        name="capitano-root",
        server_uuids=[SERVER_UUID],
        size_gb=200,
        tags={},
    )
    assert volume["uuid"] == UUID
