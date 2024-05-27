from django.db import models

class ImageUpload(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Payload(models.Model):
    description = models.TextField()
    file = models.FileField(upload_to='payloads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class StegoObject(models.Model):
    cover_image = models.ForeignKey(ImageUpload, on_delete=models.CASCADE)
    payload = models.ForeignKey(Payload, on_delete=models.CASCADE)
    stego_image = models.ImageField(upload_to='stego_images/')
    created_at = models.DateTimeField(auto_now_add=True)
