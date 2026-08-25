class CloudscaleException(Exception):
    """Raised for SDK level errors, e.g. configuration problems."""


class CloudscaleApiException(Exception):
    """Raised when the API answered with an unexpected HTTP status code.

    Attributes:
        response (dict): The parsed response, with ``status_code`` and ``data``.
        status_code (int): The HTTP status code returned by the API.
    """

    def __init__(self, *args, response: dict, status_code: int):
        super().__init__(*args)
        self.response = response
        self.status_code = status_code
