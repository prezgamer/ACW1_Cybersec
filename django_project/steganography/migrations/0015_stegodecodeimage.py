# Generated by Django 5.0.6 on 2024-06-11 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steganography', '0014_stegoimage_message_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='StegoDecodeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_file', models.FileField(blank=True, null=True, upload_to='upload_message_files')),
            ],
        ),
    ]
