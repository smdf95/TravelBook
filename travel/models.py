from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image, ExifTags


class Trip(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(default='default_trip.png', upload_to='trip_pics')
    travellers = models.ManyToManyField(User, related_name='travelled_trips')
    viewers = models.ManyToManyField(User, related_name='viewed_trips')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    created_on = models.DateTimeField(auto_now_add=True, editable=False)


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
        return self.title

    def get_absolute_url(self): # Change here
        return reverse('travel-detail', kwargs={'pk': self.pk})
    

class Post(models.Model):

    image = models.ImageField(upload_to='post_pics', blank=True)
    content = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='posts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:

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
        
        else:
            self.image = None

    def get_absolute_url(self): # Change here
        return reverse('travel-detail', kwargs={'pk': self.trip_id})

class Comment(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()
    
class Reply(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='reply_likes', blank=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def number_of_likes(self):
        return self.likes.count()

    