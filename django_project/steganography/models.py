from django.db import models

class StegoImage(models.Model):
    original_image = models.ImageField(upload_to='stego_images/original')
    message = models.TextField()
    stego_image = models.ImageField(upload_to='stego_images/', null=True, blank=True)
