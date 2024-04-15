from django.db import models

class TestModel(models.Model):
    image = models.ImageField(
        upload_to='images/', 
    )