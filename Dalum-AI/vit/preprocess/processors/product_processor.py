import numpy as np
from rembg import remove


class ProductProcessor:
    def process(self, image):
        rgba = np.array(remove(image))
        return rgba
