from django.contrib import admin

from .models import User, Post, Followers, Like

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")

class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "content")

class FollowersAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following")

class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Followers, FollowersAdmin)
admin.site.register(Like, LikeAdmin)
