from django.db import models

class StegImage(models.Model):
    image = models.ImageField(upload_to='images/')
    hidden_message = models.TextField(blank=True, null=True)
    encoded_image = models.ImageField(upload_to='images/', blank=True, null=True)
