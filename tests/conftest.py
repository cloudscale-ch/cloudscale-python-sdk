"""Shared fixtures.

Every test runs against a throw-away ``$HOME``/CWD so that a real
``cloudscale.ini`` on the developer's machine can never influence the outcome.
"""

import pytest
import responses as responses_module

from cloudscale import CLOUDSCALE_API_URL, Cloudscale

API_URL = CLOUDSCALE_API_URL


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Isolates config file discovery from the machine running the tests."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.delenv("CLOUDSCALE_CONFIG", raising=False)
    monkeypatch.delenv("CLOUDSCALE_PROFILE", raising=False)
    monkeypatch.chdir(tmp_path)
    return home


@pytest.fixture
def responses():
    """Mocks out requests, asserting that every registered response is used."""
    with responses_module.RequestsMock() as mock:
        yield mock


@pytest.fixture
def cloudscale():
    """A client authenticated with a dummy token."""
    with Cloudscale(api_token="token") as client:
        yield client
