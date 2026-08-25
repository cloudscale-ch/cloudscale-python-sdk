import pytest
import responses as responses_module

from cloudscale import CloudscaleApiException

from .conftest import API_URL

UUID = "11111111-1864-4608-853a-0771b6885a3a"

CUSTOM_IMAGE_RESP = {
    "href": f"https://api.cloudscale.ch/v1/custom-images/{UUID}",
    "created_at": "2020-05-29T13:18:42.511407Z",
    "uuid": UUID,
    "name": "my-image",
    "slug": "my-image-slug",
    "checksums": {
        "md5": "5b3a1f21cde154cfb522b582f44f1a87",
        "sha256": "5b03bcbd00b687e08791694e47d235a487c294e58ca3b1af704120123aa3f4e6",
    },
    "user_data_handling": "pass-through",
    "zones": [{"slug": "lpg1"}],
    "tags": {},
}

CUSTOM_IMAGE_IMPORT_RESP = {
    "href": f"https://api.cloudscale.ch/v1/custom-images/import/{UUID}",
    "uuid": UUID,
    "custom_image": {
        "href": f"https://api.cloudscale.ch/v1/custom-images/{UUID}",
        "uuid": UUID,
        "name": "my-image",
    },
    "url": "https://example.com/foo.raw",
    "status": "in_progress",
}


def test_custom_image_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/custom-images", json=[CUSTOM_IMAGE_RESP], status=200)

    custom_images = cloudscale.custom_image.get_all()
    assert custom_images[0]["name"] == "my-image"
    assert custom_images[0]["uuid"] == UUID


def test_custom_image_get_by_uuid(responses, cloudscale):
    responses.get(f"{API_URL}/custom-images/{UUID}", json=CUSTOM_IMAGE_RESP, status=200)

    custom_image = cloudscale.custom_image.get_by_uuid(uuid=UUID)
    assert custom_image["name"] == "my-image"
    assert custom_image["uuid"] == UUID


def test_custom_image_delete(responses, cloudscale):
    responses.delete(f"{API_URL}/custom-images/{UUID}", status=204)

    assert not cloudscale.custom_image.delete(uuid=UUID)


def test_custom_image_delete_not_found(responses, cloudscale):
    responses.delete(
        f"{API_URL}/custom-images/unknown", json={"detail": "Not found."}, status=404
    )

    with pytest.raises(CloudscaleApiException) as exc_info:
        cloudscale.custom_image.delete(uuid="unknown")

    assert exc_info.value.status_code == 404


def test_custom_image_import_by_url(responses, cloudscale):
    responses.post(
        f"{API_URL}/custom-images/import",
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=201,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "url": "https://example.com/foo.raw",
                    "name": "my-image",
                    "slug": "my-image-slug",
                    "zones": ["lpg1"],
                    "user_data_handling": "pass-through",
                    "source_format": "raw",
                    "tags": {"project": "apollo"},
                }
            )
        ],
    )

    custom_image = cloudscale.custom_image.import_by_url(
        url="https://example.com/foo.raw",
        name="my-image",
        slug="my-image-slug",
        user_data_handling="pass-through",
        source_format="raw",
        zones=["lpg1"],
        tags={"project": "apollo"},
    )
    assert custom_image["status"] == "in_progress"


def test_custom_image_create_is_not_implemented(cloudscale):
    with pytest.raises(NotImplementedError):
        cloudscale.custom_image.create(name="my-image")


def test_custom_image_update(responses, cloudscale):
    responses.patch(
        f"{API_URL}/custom-images/{UUID}",
        json=CUSTOM_IMAGE_RESP,
        status=200,
        match=[
            responses_module.matchers.json_params_matcher(
                {
                    "name": "my-image",
                    "slug": "my-image-slug",
                    "user_data_handling": "pass-through",
                    "tags": {},
                }
            )
        ],
    )

    custom_image = cloudscale.custom_image.update(
        uuid=UUID,
        name="my-image",
        slug="my-image-slug",
        user_data_handling="pass-through",
        tags={},
    )
    assert custom_image["name"] == "my-image"


def test_custom_image_get_import_by_uuid(responses, cloudscale):
    responses.get(
        f"{API_URL}/custom-images/import/{UUID}",
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=200,
    )

    custom_image = cloudscale.custom_image.get_import_by_uuid(uuid=UUID)
    assert custom_image["custom_image"]["name"] == "my-image"
    assert custom_image["uuid"] == UUID
    assert custom_image["status"] == "in_progress"
