"""Thin HTTP layer translating resource calls into API requests."""

import contextlib
from types import TracebackType
from urllib.parse import urlencode

import requests

from .log import logger

#: HTTP status codes the API uses to signal success.
SUCCESS_STATUS_CODES = frozenset({200, 201, 204})


class RestAPIClient:
    def __init__(
        self, api_url: str, api_token: str, user_agent: str, timeout: int = 60
    ):
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
            "Authorization": f"Bearer {api_token}",
            "Content-type": "application/json",
            "User-Agent": user_agent,
        }
        self._session = requests.Session()

    def close(self) -> None:
        """Closes the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "RestAPIClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def _build_url(self, resource: str, *parts: str | None) -> str:
        """Joins the API URL, the resource and any additional path segments."""
        segments = [self.api_url, resource, *(p for p in parts if p)]
        return "/".join(segments)

    @staticmethod
    def _build_query(payload: dict) -> str:
        """Encodes a payload as query string, keys with a ``None`` value stay bare."""
        return "&".join(
            key if value is None else urlencode({key: value})
            for key, value in payload.items()
        )

    def _request(self, method: str, url: str, json: dict | None = None) -> dict:
        """Sends a request and returns the parsed result."""
        logger.info("HTTP %s to %s", method, url)
        response = self._session.request(
            method, url, json=json, headers=self.headers, timeout=self.timeout
        )
        return self._return_result(response)

    def _return_result(self, r: requests.Response) -> dict:
        """Parses results from Requests

        Args:
            r (object): Requests object

        Returns:
            dict: Parsed results
        """
        logger.info("HTTP status code %s", r.status_code)
        result: dict = {
            "status_code": r.status_code,
            "data": {},
        }

        with contextlib.suppress(ValueError):
            result["data"] = r.json()

        return result

    def get_resources(
        self,
        resource: str,
        payload: dict | None = None,
        resource_id: str | None = None,
    ) -> dict:
        """Requests one resource by id, or the list of all resources."""
        query_url = self._build_url(resource, resource_id)

        if payload:
            query_url = f"{query_url}?{self._build_query(payload)}"

        return self._request("GET", query_url)

    def post_patch_resource(
        self,
        resource: str,
        payload: dict | None = None,
        resource_id: str | None = None,
        action: str | None = None,
    ) -> dict:
        """Creates (POST), updates (PATCH) or acts (POST) on a resource.

        Without a ``resource_id`` the resource is created, with an ``action`` the
        action is triggered on it, otherwise the resource is updated.
        """
        data = {k: v for k, v in (payload or {}).items() if v is not None}

        query_url = self._build_url(resource, resource_id, action)
        method = "PATCH" if resource_id and not action else "POST"

        return self._request(method, query_url, json=data)

    def delete_resource(self, resource: str, resource_id: str) -> dict:
        """Deletes a resource by id."""
        return self._request("DELETE", self._build_url(resource, resource_id))
