# user_info/models.py

from django.contrib.auth.models import User
from django.db import models


# Creating a Profile model that has a one-to-one relationship with the User model
class UserProfile(models.Model):
    # Linking the Profile to a User model instance
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Adding additional fields to the Profile model
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=(('男', '男'), ('女', '女'), ('未知', '未知')), blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    # String representation of the Profile model
    def __str__(self):
        return self.user.username
