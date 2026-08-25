import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

USER_ID = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"

OBJECTS_USER_RESP = {
    "href": f"https://api.cloudscale.ch/v1/objects-users/{USER_ID}",
    "id": USER_ID,
    "display_name": "alan",
    "keys": [
        {
            "access_key": "0ZTAIBKSGYBRHQ09G11W",
            "secret_key": "bn2ufcwbIa0ARLc5CLRSlVaCfFxPHOpHmjKiH34T",
        }
    ],
    "tags": {"project": "apollo"},
}


def test_objects_user_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/objects-users", json=[OBJECTS_USER_RESP], status=200)

    objects_users = cloudscale.objects_user.get_all()
    assert objects_users[0]["display_name"] == "alan"
    assert objects_users[0]["id"] == USER_ID


def test_objects_user_get_all_filtered(responses, cloudscale):
    responses.get(
        f"{API_URL}/objects-users",
        json=[OBJECTS_USER_RESP],
        status=200,
        match=[responses_module.matchers.query_string_matcher("tag:project=apollo")],
    )

    objects_users = cloudscale.objects_user.get_all(filter_tag="project=apollo")
    assert objects_users[0]["tags"]["project"] == "apollo"


def test_objects_user_get_all_error(responses, cloudscale):
    responses.get(f"{API_URL}/objects-users", json={}, status=500)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.objects_user.get_all()

    assert exc_info.value.status_code == 500
    assert str(exc_info.value).startswith("API Response Error (500):")


def test_objects_user_get_by_uuid(responses, cloudscale):
    responses.get(
        f"{API_URL}/objects-users/{USER_ID}", json=OBJECTS_USER_RESP, status=200
    )

    objects_user = cloudscale.objects_user.get_by_uuid(uuid=USER_ID)
    assert objects_user["display_name"] == "alan"
    assert objects_user["id"] == USER_ID


def test_objects_user_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/objects-users/{USER_ID}", status=204)

    assert not cloudscale.objects_user.delete(uuid=USER_ID)


def test_objects_user_delete_not_found(responses, cloudscale):
    responses.delete(f"{API_URL}/objects-users/unknown", json={}, status=404)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.objects_user.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_objects_user_create(responses, cloudscale):
    responses.post(
        f"{API_URL}/objects-users",
        json=OBJECTS_USER_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {"display_name": "alan", "tags": {"project": "apollo"}}
            )
        ],
    )

    objects_user = cloudscale.objects_user.create(
        display_name="alan", tags={"project": "apollo"}
    )
    assert objects_user["id"] == USER_ID


def test_objects_user_create_error(responses, cloudscale):
    responses.post(f"{API_URL}/objects-users", json={}, status=500)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.objects_user.create(display_name="alan")

    assert exc_info.value.status_code == 500


def test_objects_user_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/objects-users/{USER_ID}",
        json=OBJECTS_USER_RESP,
        status=200,
        match=[responses_module.matchers.json_params_matcher({"display_name": "alan"})],
    )

    objects_user = cloudscale.objects_user.update(uuid=USER_ID, display_name="alan")
    assert objects_user["display_name"] == "alan"


def test_objects_user_update_not_found(responses, cloudscale):
    responses.patch(f"{API_URL}/objects-users/unknown", json={}, status=404)

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.objects_user.update(uuid="unknown", display_name="alan")

    assert exc_info.value.status_code == 404
