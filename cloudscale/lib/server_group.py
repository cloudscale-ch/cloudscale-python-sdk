from . import CloudscaleMutable

class ServerGroup(CloudscaleMutable):

    def __init__(self):
        """Server Group
        """
        super().__init__()
        self.resource = 'server-groups'

    def create(
        self,
        name: str,
        group_type: str = None,
        tags: dict = None,
    ) -> dict:
        """Creates a server group.

        Args:
            name (str, optional): The name of the server group.
            group_type (str, optional): The type of a server group. Defaults to None.
            tags (dict, optional): The tags assigned to the server group. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            'name': name,
            'type': group_type,
            'tags': tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        name: str = None,
        tags: dict = None,
    ) -> dict:
        """Updates a server group.

        Args:
            uuid (str): The UUID of the server group.
            name (str, optional): The name of the server group. Defaults to None.
            tags (dict, optional): The tags assigned to the server group. Defaults to None.
        Returns:
            dict: API data response.
        """
        payload = {
            'name': name,
            'tags': tags,
        }
        return super().update(uuid=uuid, payload=payload)
