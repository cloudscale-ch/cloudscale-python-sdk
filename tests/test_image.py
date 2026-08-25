from .conftest import API_URL

IMAGE_RESP = {
    "slug": "debian-10",
    "name": "Debian 10 (Buster)",
    "operating_system": "Debian",
    "default_username": "debian",
    "zones": [{"slug": "rma1"}, {"slug": "lpg1"}],
}


def test_image_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/images", json=[IMAGE_RESP], status=200)

    images = cloudscale.image.get_all()
    assert images[0]["slug"] == "debian-10"
    assert images[0]["operating_system"] == "Debian"
