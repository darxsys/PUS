from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# CustomUser is used as an extension to the existing Django user.
class CustomUser(models.Model):
    user = models.OneToOneField(User, related_name='customuser')
    friends = models.ManyToManyField('self', default=None, 
        related_name='friend_list', symmetrical=False)

    def __unicode__(self):
        return self.user.username

def create_profile(sender, **kw):
    user = kw['instance']
    if kw['created']:
        profile = CustomUser(user=user)
        profile.save()

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, related_name='notification')
    source = models.ForeignKey(CustomUser, related_name='notification_src')
# post_save.connect(create_profile, sender=User)
