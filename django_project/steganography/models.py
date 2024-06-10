from django.db import models

class StegoImage(models.Model):
    original_image = models.ImageField(upload_to='stego_images/original')
    message = models.TextField()
    stego_image = models.ImageField(upload_to='stego_images/', null=True, blank=True)


class StegoAudio(models.Model):
    original_audio = models.FileField(upload_to='stego_audio/original')
    message = models.TextField()
    stego_audio = models.FileField(upload_to='stego_audio/', null=True, blank=True)