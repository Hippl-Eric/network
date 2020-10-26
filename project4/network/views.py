from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Followers


def index(request):

    # New post
    if request.method == "POST":

        # Grab form submission
        content = request.POST.get("content")
        # TODO prevent empty posts

        post = Post(user=request.user, content=content)
        post.save()

        return HttpResponseRedirect(reverse("index"))
    
    # Return all posts page
    else:
        all_posts = Post.objects.all().order_by(F('timestamp').desc())
        return render(request, "network/index.html", {
            "all_posts": all_posts
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    
    # Query username, and return profile page
    try:
        # Query username
        user = User.objects.get(username=username)

        # Grab user's posts, qty of followers, qty following, & list of followers
        posts = user.posts.all().order_by(F('timestamp').desc())
        num_followers = user.followers.count()
        num_following = user.following.count()
        follower_list = user.followers.values_list("follower_id", flat=True)

        # Return profile page
        return render(request, "network/profile.html", {
            "user_profile": user,
            "posts": posts,
            "num_followers": num_followers,
            "num_following": num_following,
            "follower_list": follower_list
        })

    # Invalid username
    except:
        return render(request, "network/profile.html", {
            "message": f"Whoops! Sorry, {username} was not found."
        })

@login_required(login_url='login')
def following_posts(request):

    # Create list of following ids
    following_list = request.user.following.values_list("following_id", flat=True)

    # Get all follower posts
    following_posts = Post.objects.filter(user__in=following_list).order_by(F('timestamp').desc())

    return render(request, "network/following.html", {
        "posts": following_posts
    })
