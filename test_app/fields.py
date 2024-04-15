

from django.core.files.images import get_image_dimensions
from django.db.models.fields.files import ImageFieldFile, ImageField



class FixedImageFieldFile(ImageFieldFile):

    # This is my attempt to delegate the dimensions to the underlying field
    # Doesn't sem to work
    def _get_image_dimensions(self):
        if not hasattr(self, "_dimensions_cache"):
            if hasattr(self, "_file"):
                file = self._file

                # Duck type image-like objects

                if hasattr(file, "_get_image_dimensions"):
                    self._dimensions_cache = file._get_image_dimensions()
                    return self._dimensions_cache
        
        return super()._get_image_dimensions()



class FixedImageField(ImageField):
    attr_class = FixedImageFieldFile