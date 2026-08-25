![license](https://img.shields.io/pypi/l/cloudscale-sdk.svg)
![python versions](https://img.shields.io/pypi/pyversions/cloudscale-sdk.svg)
![status](https://img.shields.io/pypi/status/cloudscale-sdk.svg)
[![pypi version](https://img.shields.io/pypi/v/cloudscale-sdk.svg)](https://pypi.org/project/cloudscale-sdk/)
![PyPI - Downloads](https://img.shields.io/pypi/dw/cloudscale-sdk)
[![Codecov](https://img.shields.io/codecov/c/github/cloudscale-ch/cloudscale-python-sdk)](https://codecov.io/gh/cloudscale-ch/cloudscale-python-sdk)

# Python SDK for cloudscale.ch

A Python library for [cloudscale.ch](https://www.cloudscale.ch), requires Python 3.10 or newer.

## Install / Update

~~~shell
pip install -U cloudscale-sdk
~~~

## Usage

~~~python
from cloudscale import Cloudscale

with Cloudscale(api_token="...") as cloudscale:
    server = cloudscale.server.create(
        name="db-master", flavor="flex-4", image="debian-12"
    )
    cloudscale.server.stop(uuid=server["uuid"])
    for volume in cloudscale.volume.get_all(filter_tag="project=apollo"):
        print(volume["name"])
~~~

Resources available as attributes: `custom_image`, `flavor`, `floating_ip`, `image`,
`network`, `objects_user`, `region`, `server`, `server_group`, `subnet`, `volume`.
Depending on the resource they offer `get_all()`, `get_by_uuid()`, `create()`,
`update()` and `delete()`.

Errors are raised as `CloudscaleException` (configuration problems) and
`CloudscaleApiException` (API errors, carrying `status_code` and `response`).

### Authentication

The API token is taken from the `api_token` argument, or from a `cloudscale.ini`
looked up in this order, later files winning:

1. `$XDG_CONFIG_HOME/cloudscale/cloudscale.ini` (`~/.config/...` by default)
2. `~/.cloudscale.ini`
3. `./cloudscale.ini`

~~~ini
[default]
api_token = ...

[production]
api_token = ...
timeout = 30
~~~

Select a section with `Cloudscale(profile="production")` or `$CLOUDSCALE_PROFILE`.

### Environment variables

| Variable | Description |
| --- | --- |
| `CLOUDSCALE_API_URL` | API endpoint, defaults to `https://api.cloudscale.ch/v1` |
| `CLOUDSCALE_CONFIG` | Config file name, defaults to `cloudscale.ini` |
| `CLOUDSCALE_PROFILE` | Config section to use, defaults to `default` |
| `CLOUDSCALE_LOG_LEVEL` | Log level, defaults to `ERROR` |

## Development

This project uses [uv](https://docs.astral.sh/uv/) and
[ruff](https://docs.astral.sh/ruff/).

~~~shell
make install   # create the virtualenv
make test      # run the tests
make coverage  # run the tests with a coverage report
make lint      # lint and format check
make format    # apply lint fixes and formatting
~~~
