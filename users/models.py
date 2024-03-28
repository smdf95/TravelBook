from django.contrib.auth.models import User
from django.db import models
import cloudinary.uploader

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='profile_pics',
        blank=True
    )
    f_name = models.CharField(max_length=100, default='')
    l_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return f'{self.user.username} Profile'
