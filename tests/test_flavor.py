from .conftest import API_URL

FLAVOR_RESP = {
    "slug": "flex-2",
    "name": "Flex-2",
    "vcpu_count": 1,
    "memory_gb": 2,
    "zones": [{"slug": "rma1"}, {"slug": "lpg1"}],
}


def test_flavor_get_all(responses, cloudscale):
    responses.get(f"{API_URL}/flavors", json=[FLAVOR_RESP], status=200)

    flavors = cloudscale.flavor.get_all()
    assert flavors[0]["slug"] == "flex-2"
    assert flavors[0]["name"] == "Flex-2"
