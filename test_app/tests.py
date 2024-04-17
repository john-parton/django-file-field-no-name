import base64

from django.test import TestCase
from django.core.files.base import ContentFile
from .models import TestModel


# See https://commons.wikimedia.org/wiki/File:ISS062-E-125302_-_View_of_Earth.jpg
IMAGE_CONTENTS = b"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"


class AnimalTestCase(TestCase):
    def test_ken_hypothesis_1(self):
        instance = TestModel()

        instance.image = ContentFile(
            base64.b64decode(IMAGE_CONTENTS),
        )

        instance.image.name = "XXXX"

        # Make sure file is still there
        self.assertEqual(
            instance.image.read(),
            IMAGE_CONTENTS,
        )

    def test_ken_hypothesis_2(self):
        instance = TestModel()

        instance.image = ContentFile(
            base64.b64decode(IMAGE_CONTENTS),
        )
        # Data thrown away here silently
        instance.save()

        instance = TestModel.objects.get(id=instance.id)

        instance.image.name = "XXXX"

        # Make sure file is still there
        self.assertEqual(
            instance.image.read(),
            IMAGE_CONTENTS,
        )

    def test_ken_hypothesis_3(self):
        instance = TestModel()

        instance.image = ContentFile(
            base64.b64decode(IMAGE_CONTENTS),
        )

        instance.image.name = "XXXX"

        instance.save()

        self.assertEqual(
            instance.image.read(),
            IMAGE_CONTENTS,
        )

    def test_content_file_reasonable_error_after_explicit_re_init(self):
        instance = TestModel()

        instance.image = ContentFile(
            base64.b64decode(IMAGE_CONTENTS),
        )

        # Data thrown away here silently
        instance.save()

        instance = TestModel.objects.get(id=instance.id)

        # Image is well and truly gone
        self.assertEqual(
            instance.__dict__["image"],
            "",
        )

        instance.image.read()

    def test_can_reread_content_file(self):
        instance = TestModel()

        instance.image = ContentFile(
            base64.b64decode(IMAGE_CONTENTS),
        )

        # Even before saving, the image is gone

        self.assertEqual(
            instance.image.read(),
            IMAGE_CONTENTS,
        )
