from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image, ExifTags


class Trip(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='trip_pics',
        blank=True,
    )
    travellers = models.ManyToManyField(User, related_name='travelled_trips')
    viewers = models.ManyToManyField(User, related_name='viewed_trips')
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    traveller_invitation_link = models.CharField(max_length=10, unique=True, null=True, blank=True)
    viewer_invitation_link = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if the object already exists (updating) and if an image has been uploaded
        if self.pk and self.image:
            existing = Trip.objects.get(pk=self.pk)
            if existing.image != self.image:
                existing.image.delete()  # Delete the old image
        super(Trip, self).save(*args, **kwargs)
        

    def __str__(self):
        return self.title

    def get_absolute_url(self): # Change here
        return reverse('trip-detail', kwargs={'pk': self.pk})
    

class Post(models.Model):

    image = models.ImageField(
        upload_to='post_pics',
        blank=True,
    )
    content = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()


    def get_absolute_url(self): # Change here
        return reverse('trip-detail', kwargs={'pk': self.trip_id})

class Comment(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()
    
    def get_absolute_url(self): # Change here
        return reverse('post-detail', kwargs={'pk': self.post_id})
    
class Reply(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='reply_likes', blank=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()

    