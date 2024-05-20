from django.db import models

class ImageUpload(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
