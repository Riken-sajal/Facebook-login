
from django.db import models
from django.contrib.auth.models import User

class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Profile(TimeStampModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='user_profile_pictures/', default='profile_pictures/original_default_pic.png')
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    reputation = models.IntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    moderator = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_sent_at = models.DateTimeField(null=True, blank=True)  
    reset_sent_at = models.DateTimeField(null=True, blank=True)  


    def __str__(self):
        return self.user.username
    
