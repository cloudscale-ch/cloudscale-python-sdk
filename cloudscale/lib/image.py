from . import CloudscaleBase

class Image(CloudscaleBase):

    def __init__(self):
        """Image
        """
        super(Image, self).__init__()
        self.resource = 'images'
