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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
        

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

    