"""Base classes shared by all API resources."""

from ..error import CloudscaleApiException
from ..http import SUCCESS_STATUS_CODES, RestAPIClient


class CloudscaleBase:
    """A read-only API resource, listable via :meth:`get_all`."""

    resource: str = ""

    def __init__(self, config):
        """
        Args:
            config: The :class:`~cloudscale.Cloudscale` instance owning this
                resource. Any object exposing ``api_token``, ``api_url``,
                ``version`` and ``timeout`` is accepted as well, in which case a
                private HTTP client is created for it.
        """
        client = getattr(config, "_client", None)
        if client is None:
            client = RestAPIClient(
                api_token=config.api_token,
                api_url=config.api_url,
                user_agent=f"cloudscale-sdk {config.version}",
                timeout=config.timeout,
            )
        self._client: RestAPIClient = client

    def _process_response(self, response: dict):
        """Unwraps the API data, raising on unexpected HTTP status codes.

        Args:
            response (dict): The result of a :class:`~cloudscale.http.RestAPIClient` call.

        Raises:
            CloudscaleApiException: The API returned an error status code.

        Returns:
            The ``data`` part of the response.
        """
        status_code = int(response.get("status_code") or 0)
        data = response.get("data") or {}

        if status_code not in SUCCESS_STATUS_CODES:
            detail = data.get("detail", data) if isinstance(data, dict) else data
            raise CloudscaleApiException(
                f"API Response Error ({status_code}): {detail}",
                response=response,
                status_code=status_code,
            )

        return response.get("data")

    def get_all(self, path: str = "", filter_tag: str | None = None) -> list:
        """Lists all API resources.

        Args:
            path (str, optional): Path the resource is located under. Default to "".
            filter_tag (str, optional): Filter by tag in format <key>=<value> or <key>. Defaults to None.

        Returns:
            list: API data response.
        """
        payload = _tag_filter_payload(filter_tag) if filter_tag is not None else None
        response = self._client.get_resources(self.resource + path, payload=payload)
        return self._process_response(response) or []


class CloudscaleBaseExt(CloudscaleBase):
    """A read-only API resource that can also be queried by UUID."""

    def get_by_uuid(self, uuid: str, path: str = "") -> dict:
        """Queries an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.get_resources(self.resource + path, resource_id=uuid)
        return self._process_response(response) or {}


class CloudscaleMutable(CloudscaleBaseExt):
    """An API resource that can be created, updated and deleted."""

    def delete(self, uuid: str, path: str = ""):
        """Deletes an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.delete_resource(self.resource + path, resource_id=uuid)
        return self._process_response(response)

    def update(self, uuid: str, payload: dict, path: str = "") -> dict:
        """Updates an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            payload (dict): API arguments.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(
            self.resource + path, resource_id=uuid, payload=payload
        )
        return self._process_response(response) or {}

    def create(self, payload: dict, path: str = "") -> dict:
        """Creates an API resource.

        Args:
            payload (dict): API arguments.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(
            self.resource + path, payload=payload
        )
        return self._process_response(response) or {}


def _tag_filter_payload(filter_tag: str) -> dict[str, str | None]:
    """Turns a ``<key>=<value>`` or ``<key>`` filter into a query payload."""
    tag_key, _, tag_value = filter_tag.partition("=")

    if not tag_key.startswith("tag:"):
        tag_key = f"tag:{tag_key}"

    return {tag_key: tag_value if "=" in filter_tag else None}
