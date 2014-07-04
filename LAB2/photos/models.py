from datetime import datetime  
from django.db import models

from userprofile.models import CustomUser

class Photo(models.Model):
    # Many to One relationship
    owner = models.ForeignKey(CustomUser, related_name='pics')
    photo = models.ImageField(max_length=200, upload_to='photos/')
    name = models.CharField(max_length=50)
    public = models.BooleanField(default=False)
    like = models.ManyToManyField(CustomUser, related_name='likes')
    tag = models.ManyToManyField(CustomUser, related_name='tags')

class Comment(models.Model):
    photo = models.ForeignKey(Photo, related_name='comments')
    time = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(CustomUser, related_name='comments')
    text = models.CharField(max_length=200)
