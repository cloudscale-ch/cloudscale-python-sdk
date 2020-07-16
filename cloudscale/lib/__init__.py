from ..error import CloudscaleApiException

class CloudscaleBase:

    def __init__(self):
        """CloudscaleBase
        """
        self._client = None
        self.resource: str = None

    def _process_response(self, response: dict) -> dict:
        """Processes of HTTP response.

        Args:
            response (dict): HTTP response data.

        Raises:
            CloudscaleApiException: Raise if not HTTP 2xx.

        Returns:
            dict: JSON data object.
        """
        status_code = response.get('status_code')
        data = response.get('data', dict())
        if status_code not in (200, 201, 204):
            raise CloudscaleApiException(
                f"API Response Error ({status_code}): {data.get('detail', data)}",
                response=response,
                status_code=status_code,
            )
        return data

    def get_all(self, filter_tag: str = None) -> list:
        """Lists all API resources.

        Args:
            filter_tag (str, optional): Filter by tag in format <key>=<value> or <key>. Defaults to None.

        Returns:
            list: API data response.
        """
        if filter_tag is not None:
            if '=' in filter_tag:
                tag_key, tag_value = filter_tag.split('=')
            else:
                tag_key = filter_tag
                tag_value = None

            if not tag_key.startswith('tag:'):
                tag_key = f'tag:{tag_key}'

            payload = {
                tag_key: tag_value
            }
        else:
            payload = None

        result = self._client.get_resources(self.resource, payload=payload)
        return self._process_response(result) or []


class CloudscaleBaseExt(CloudscaleBase):

    def get_by_uuid(self, uuid: str) -> dict:
        """Queries an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.

        Returns:
            dict: API data response.
        """
        response = self._client.get_resources(self.resource, resource_id=uuid)
        return self._process_response(response)


class CloudscaleMutable(CloudscaleBaseExt):

    def delete(self, uuid: str) -> dict:
        """Deletes an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.

        Returns:
            dict: API data response.
        """
        response = self._client.delete_resource(self.resource, resource_id=uuid)
        return self._process_response(response)

    def update(self, uuid: str, payload: dict) -> dict:
        """Updates an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            payload (dict): API arguments.

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(self.resource, resource_id=uuid, payload=payload)
        return self._process_response(response)

    def create(self, payload: dict) -> dict:
        """Creates an API resource.

        Args:
            payload (dict): API arguments.

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(self.resource, payload=payload)
        return self._process_response(response)
