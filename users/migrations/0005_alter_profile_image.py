# Generated by Django 5.0 on 2024-03-28 11:58

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', storage=cloudinary_storage.storage.RawMediaCloudinaryStorage(), upload_to='profile_pics'),
        ),
    ]