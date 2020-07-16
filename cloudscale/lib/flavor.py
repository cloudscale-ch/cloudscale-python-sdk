from . import CloudscaleBase

class Flavor(CloudscaleBase):

    def __init__(self):
        """Flavor
        """
        super().__init__()
        self.resource = 'flavors'
