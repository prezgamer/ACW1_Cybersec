# Generated by Django 5.0.6 on 2024-06-07 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steganography', '0007_remove_stegoimage_stego_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stegoimage',
            name='stego_image',
            field=models.ImageField(blank=True, upload_to='stego_images/stego'),
        ),
        migrations.AlterField(
            model_name='stegoimage',
            name='original_image',
            field=models.ImageField(upload_to='images/input'),
        ),
    ]
