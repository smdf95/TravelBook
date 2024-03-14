import os
import hashlib

from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ExifTags

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    f_name = models.CharField(max_length=100, default='')
    l_name = models.CharField(max_length=100, default='')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path) # Open image

        if hasattr(img, '_getexif') and img._getexif() is not None:
            exif = dict(img._getexif().items())
            if 0x0112 in exif:
                orientation = exif[0x0112]
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

        # resize image
        if img.height > 600 or img.width > 600:
            output_size = (600, 600)
            img.thumbnail(output_size) # Resize image
            
        img.save(self.image.path)

    def __str__(self):
        return f'{self.user.username} Profile'
