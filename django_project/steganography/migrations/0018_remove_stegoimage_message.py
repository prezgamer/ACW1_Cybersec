# Generated by Django 5.0.6 on 2024-06-11 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('steganography', '0017_remove_stegodecodeimage_message_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stegoimage',
            name='message',
        ),
    ]
