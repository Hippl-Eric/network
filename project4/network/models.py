from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F


class User(AbstractUser):

    def __str__(self):
        return f"{self.id}, {self.username}"

class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(F('timestamp').desc())

class Post(models.Model):
    
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=False)
    likes = models.IntegerField(default=0)
    objects = PostManager()

    def __str__(self):
        return f"{self.id}, ({self.user})"

class Followers(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.id}, ({self.follower}), ({self.following})"