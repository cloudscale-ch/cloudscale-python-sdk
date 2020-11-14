from . import CloudscaleMutable

class Volume(CloudscaleMutable):

    def __init__(self):
        """Volume
        """
        super(Volume, self).__init__()
        self.resource = 'volumes'

    def create(
        self,
        name: str,
        server_uuids: list,
        size_gb: int,
        volume_type: str = None,
        zone: str = None,
        tags: dict = None,
    ) -> dict:
        """Creates a Volume.

        Args:
            name (str): The display name of the volume.
            server_uuids (list): A list of server UUIDs the volume is attached to. Currently, only single server possible.
            size_gb (int): The size of the volume in GiB (1024^3).
            volume_type (str, optional): Type of the volume. Defaults to None.
            zone (str, optional): The slug of the zone. Defaults to None.
            tags (dict, optional): The tags assigned to the volume. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            'name': name,
            'server_uuids': server_uuids,
            'size_gb': size_gb,
            'type': volume_type,
            'zone': zone,
            'tags': tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        name: str = None,
        server_uuids: list = None,
        size_gb: int = None,
        tags: dict = None,
    ) -> dict:
        """Updates a volume.

        Args:
            uuid (str): The UUID of the volume.
            name (str): The display name of the volume. Defaults to None.
            server_uuids (list): A list of server UUIDs the volume is attached to. Currently, only single server possible. Defaults to None.
            size_gb (int): The size of the volume in GiB (1024^3).
            tags (dict, optional): The tags assigned to the volume. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            'name': name,
            'server_uuids': server_uuids,
            'size_gb': size_gb,
            'tags': tags,
        }
        return super().update(uuid=uuid, payload=payload)
