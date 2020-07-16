from . import CloudscaleBaseExt

class Subnet(CloudscaleBaseExt):

    def __init__(self):
        """Subnet
        """
        super().__init__()
        self.resource = 'subnets'
