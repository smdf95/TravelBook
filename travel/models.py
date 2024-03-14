from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

class Trip(models.Model):
    title = models.CharField(max_length=100)
    travellers = models.ManyToManyField(User, related_name='travelled_trips')
    viewers = models.ManyToManyField(User, related_name='viewed_trips')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self): # Change here
        return reverse('travel-detail', kwargs={'pk': self.pk})