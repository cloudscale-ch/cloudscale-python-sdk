import pytest

from cloudscale import CLOUDSCALE_CONFIG, CloudscaleException
from cloudscale.config import config_file_paths, read_config


def test_config_file_paths_order(isolated_env, tmp_path):
    paths = config_file_paths()
    assert paths == (
        str(isolated_env / ".config" / "cloudscale" / CLOUDSCALE_CONFIG),
        str(isolated_env / f".{CLOUDSCALE_CONFIG}"),
        str(tmp_path / CLOUDSCALE_CONFIG),
    )


def test_config_file_paths_without_xdg_config_home(isolated_env, monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME")
    assert config_file_paths()[0] == str(
        isolated_env / ".config" / "cloudscale" / CLOUDSCALE_CONFIG
    )


def test_config_file_name_from_env(isolated_env, monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDSCALE_CONFIG", "other.ini")
    assert config_file_paths()[2] == str(tmp_path / "other.ini")


def test_read_config_without_any_config_file():
    assert read_config() == {}


def test_read_config_cwd_takes_precedence(isolated_env, tmp_path):
    (isolated_env / f".{CLOUDSCALE_CONFIG}").write_text("[default]\napi_token = home\n")
    (tmp_path / CLOUDSCALE_CONFIG).write_text("[default]\napi_token = cwd\n")

    assert read_config() == {"api_token": "cwd"}


def test_read_config_xdg_location(isolated_env):
    path = isolated_env / ".config" / "cloudscale" / CLOUDSCALE_CONFIG
    path.parent.mkdir(parents=True)
    path.write_text("[default]\napi_token = xdg\n")

    assert read_config() == {"api_token": "xdg"}


def test_read_config_profile_from_env(isolated_env, monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDSCALE_PROFILE", "staging")
    (tmp_path / CLOUDSCALE_CONFIG).write_text("[staging]\napi_token = staging_token\n")

    assert read_config() == {"api_token": "staging_token"}


def test_read_config_missing_profile_raises(tmp_path):
    (tmp_path / CLOUDSCALE_CONFIG).write_text("[default]\napi_token = token\n")

    with pytest.raises(CloudscaleException) as exc_info:
        read_config(profile="nope")

    message = str(exc_info.value)
    assert message.startswith("Profile 'nope' not found in config files: (")
    assert str(tmp_path / CLOUDSCALE_CONFIG) in message


def test_read_config_default_profile_may_be_absent(tmp_path):
    (tmp_path / CLOUDSCALE_CONFIG).write_text("[other]\napi_token = token\n")

    assert read_config() == {}
