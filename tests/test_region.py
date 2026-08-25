from .conftest import API_URL

REGION_RESP = {
    "slug": "lpg",
    "zones": [{"slug": "lpg1"}],
}


def test_region_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/regions", json=[REGION_RESP], status=200)

    regions = cloudscale.region.get_all()
    assert regions[0]["slug"] == "lpg"
    assert regions[0]["zones"] == [{"slug": "lpg1"}]
