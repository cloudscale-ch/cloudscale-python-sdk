import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "47cec963-fcd2-482f-bdb6-24461b2d47b1"

SERVER_RESP = {
    "uuid": UUID,
    "name": "db-master",
    "status": "running",
    "zone": {"slug": "lpg1"},
    "flavor": {"slug": "flex-4"},
    "image": {"slug": "debian-9"},
    "server_groups": [],
    "anti_affinity_with": [],
    "tags": {"project": "gemini"},
}


def test_server_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/servers", json=[SERVER_RESP], status=200)

    servers = cloudscale.server.get_all()
    assert servers[0]["name"] == "db-master"
    assert servers[0]["uuid"] == UUID
    assert servers[0]["tags"]["project"] == "gemini"


def test_server_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/servers/{UUID}", json=SERVER_RESP, status=200)

    server = cloudscale.server.get_by_uuid(uuid=UUID)
    assert server["name"] == "db-master"
    assert server["uuid"] == UUID


def test_server_get_by_uuid_not_found(responses, cloudscale):
    responses.get(
        f"{API_URL}/servers/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server.get_by_uuid(uuid="unknown")

    assert exc_info.value.status_code == 404
    assert str(exc_info.value) == "API Response Error (404): Not found."


def test_server_get_unauthenticated(responses, cloudscale):
    responses.get(
        f"{API_URL}/servers/unknown",
        json={"detail": "Authentication credentials were not provided."},
        status=401,
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server.get_by_uuid(uuid="unknown")

    assert exc_info.value.status_code == 401
    assert str(exc_info.value) == (
        "API Response Error (401): Authentication credentials were not provided."
    )


def test_server_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/servers/{UUID}", status=204)

    assert not cloudscale.server.delete(uuid=UUID)


def test_server_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/servers/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_server_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {"name": "db-master", "flavor": "flex-4", "image": "debian-9"}
            )
        ],
    )

    server = cloudscale.server.create(
        name="db-master", flavor="flex-4", image="debian-9"
    )
    assert server["uuid"] == UUID


def test_server_create_with_all_options(responses, cloudscale):
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "db-master",
                    "flavor": "flex-4",
                    "image": "debian-9",
                    "zone": "lpg1",
                    "volume_size_gb": 50,
                    "volumes": [{"size_gb": 100}],
                    "interfaces": [{"network": "public"}],
                    "ssh_keys": ["ssh-rsa AAAA"],
                    "password": "secret",
                    "use_public_network": True,
                    "use_private_network": False,
                    "use_ipv6": True,
                    "server_groups": ["group-uuid"],
                    "user_data": "#cloud-config",
                    "tags": {"project": "gemini"},
                }
            )
        ],
    )

    cloudscale.server.create(
        name="db-master",
        flavor="flex-4",
        image="debian-9",
        zone="lpg1",
        volume_size_gb=50,
        volumes=[{"size_gb": 100}],
        interfaces=[{"network": "public"}],
        ssh_keys=["ssh-rsa AAAA"],
        password="secret",
        use_public_network=True,
        use_private_network=False,
        use_ipv6=True,
        server_groups=["group-uuid"],
        user_data="#cloud-config",
        tags={"project": "gemini"},
    )


def test_server_create_error(responses, cloudscale):
    responses.post(f"{API_URL}/servers", json={"detail": "Server error."}, status=500)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.server.create(name="db-master", flavor="flex-4", image="debian-9")

    assert exc_info.value.status_code == 500


def test_server_create_with_volume_size_gb(responses, cloudscale):
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "db-master",
                    "flavor": "flex-4",
                    "image": "debian-9",
                    "volume_size_gb": 100,
                }
            )
        ],
    )

    cloudscale.server.create(
        name="db-master", flavor="flex-4", image="debian-9", volume_size_gb=100
    )


def test_server_create_with_deprecated_volume_size(responses, cloudscale):
    """The legacy name still works, but is sent as volume_size_gb."""
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "db-master",
                    "flavor": "flex-4",
                    "image": "debian-9",
                    "volume_size_gb": 100,
                }
            )
        ],
    )

    with pytest.warns(DeprecationWarning, match="use volume_size_gb instead"):
        cloudscale.server.create(
            name="db-master", flavor="flex-4", image="debian-9", volume_size=100
        )


def test_server_create_volume_size_gb_wins_over_the_alias(responses, cloudscale):
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "db-master",
                    "flavor": "flex-4",
                    "image": "debian-9",
                    "volume_size_gb": 100,
                }
            )
        ],
    )

    with pytest.warns(DeprecationWarning):
        cloudscale.server.create(
            name="db-master",
            flavor="flex-4",
            image="debian-9",
            volume_size_gb=100,
            volume_size=50,
        )


def test_server_create_without_volume_size_omits_it(responses, cloudscale):
    responses.post(
        f"{API_URL}/servers",
        json=SERVER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {"name": "db-master", "flavor": "flex-4", "image": "debian-9"}
            )
        ],
    )

    cloudscale.server.create(name="db-master", flavor="flex-4", image="debian-9")


def test_server_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/servers/{UUID}",
        json=SERVER_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "db-master",
                    "flavor": "flex-8",
                    "interfaces": {"network": "public"},
                    "tags": {"project": "gemini"},
                }
            )
        ],
    )

    server = cloudscale.server.update(
        uuid=UUID,
        name="db-master",
        flavor="flex-8",
        interfaces={"network": "public"},
        tags={"project": "gemini"},
    )
    assert server["uuid"] == UUID


@pytest.mark.parametrize("action", ["start", "stop", "reboot"])
def test_server_actions(responses, cloudscale, action):
    responses.post(f"{API_URL}/servers/{UUID}/{action}", status=204)

    assert getattr(cloudscale.server, action)(uuid=UUID) == {}


@pytest.mark.parametrize("action", ["start", "stop", "reboot"])
def test_server_action_error(responses, cloudscale, action):
    responses.post(
        f"{API_URL}/servers/{UUID}/{action}",
        json={"detail": "Server error."},
        status=500,
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        getattr(cloudscale.server, action)(uuid=UUID)

    assert exc_info.value.status_code == 500
