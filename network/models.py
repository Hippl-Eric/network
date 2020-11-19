from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
from django.core.paginator import Paginator

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
    objects = PostManager()

    @property
    def like_user_ids(self):
        like_ids = self.likes.values_list('id', flat=True)
        return Like.objects.filter(id__in=like_ids).values_list('user_id', flat=True)

    def __str__(self):
        return f"{self.id}, ({self.user})"

class Followers(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follower')
        ]

    def __str__(self):
        return f"{self.id}, ({self.follower}), ({self.following})"

class Like(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="likes")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_like')
        ]

    def __str__(self):
        return f"user: {self.user}, post: {self.post}"