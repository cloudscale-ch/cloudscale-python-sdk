import requests
from urllib.parse import urlencode
from .log import logger


class RestAPIClient:

    def __init__(self, api_url: str, api_token: str, user_agent: str, timeout: int = 60):
        """Rest API Client

        Args:
            api_url (str): API HTTP URL
            api_token (str): API bearer token
            user_agent (str): HTTP user agent
            timeout (int, optional): HTTP timeout. Defaults to 60.
        """

        self.api_url = api_url
        self.timeout = timeout
        self.headers = {
            'Authorization': f"Bearer {api_token}",
            'Content-type': "application/json",
            'User-Agent': user_agent,
        }

    def _return_result(self, r: object) -> dict:
        """Parses results from Requests

        Args:
            r (object): Requests object

        Returns:
            dict: Parsed results
        """

        logger.info(f"HTTP status code {r.status_code}")
        result = {
            'status_code': r.status_code,
        }

        try:
            result['data'] = r.json()
        except ValueError:
            result['data'] = None
        return result

    def _handle_payload(self, payload: dict) -> dict:
        """ Filters payload

        Args:
            payload (dict): payload

        Returns:
            dict: payload
        """
        if not payload:
            return

        data = dict()
        for k, v in payload.items():
            if v is not None:
                data[k] = v

        logger.info(f"HTTP payload: {data}")
        return data

    def get_resources(self, resource: str, payload: dict = None, resource_id: str = None) -> dict:
        query_url = f"{self.api_url}/{resource}"
        if resource_id:
            query_url = f"{query_url}/{resource_id}"

        if payload:
            for k, v in payload.items():
                if v is not None:
                    data = urlencode({k: v})
                else:
                    data = k
                break

            query_url = f"{query_url}?{data}"

        logger.info(f"HTTP GET to {query_url}")

        r = requests.get(query_url, headers=self.headers, timeout=self.timeout)
        return self._return_result(r)

    def post_patch_resource(self, resource: str, payload: dict = None, resource_id: str = None, action: str = None) -> dict:
        data = self._handle_payload(payload)
        query_url = f"{self.api_url}/{resource}"

        if not resource_id:
            logger.info(f"HTTP POST to {query_url}")
            r = requests.post(query_url, json=data, headers=self.headers, timeout=self.timeout)
            return self._return_result(r)

        query_url += f"/{resource_id}"
        if action:
            query_url += f"/{action}"
            logger.info(f"HTTP POST to {query_url}")
            r = requests.post(query_url, json=data, headers=self.headers, timeout=self.timeout)
            return self._return_result(r)
        else:
            logger.info(f"HTTP PATCH to {query_url}")
            r = requests.patch(query_url, json=data, headers=self.headers, timeout=self.timeout)
            return self._return_result(r)

    def delete_resource(self, resource: str, resource_id: str) -> dict:
        query_url = f"{self.api_url}/{resource}/{resource_id}"
        logger.info(f"HTTP DELETE to {query_url}")
        r = requests.delete(query_url, headers=self.headers, timeout=self.timeout)
        return self._return_result(r)
