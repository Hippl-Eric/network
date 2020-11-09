import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, InvalidPage

from .models import User, Post, Followers, Like


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

        # Paginate posts
        all_posts = Post.objects.all()
        p = Paginator(all_posts, 10)

        # Check for page number, default 1
        page = request.GET.get("page", 1)

        # Return posts for page number, if error return page 1
        try:
            posts = p.page(page)
        except InvalidPage:
            posts = p.page(1)
        return render(request, "network/index.html", {
            "posts": posts
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
    
    # Query username
    try:
        user = User.objects.get(username=username)
    
    # Invalid username
    except User.DoesNotExist:
        return render(request, "network/profile.html", {
            "message": f"Whoops! Sorry, {username} was not found."
        })

    # Return profile page
    if request.method == "GET":

        # Grab user's posts, qty of followers, qty following, & list of followers
        posts = user.posts.all()
        num_followers = user.followers.count()
        num_following = user.following.count()
        is_following = user.followers.filter(follower_id=request.user.id).exists()

        # Return
        return render(request, "network/profile.html", {
            "user_profile": user,
            "posts": posts,
            "num_followers": num_followers,
            "num_following": num_following,
            "is_following": is_following
        })
        
    # Toggle following
    # TODO login required
    elif request.method == "PUT":

        # User is already following, change to un-following
        try:
            user_following = Followers.objects.get(follower=request.user, following=user)
            user_following.delete()
            following = False

        # User is not following, change to following
        except Followers.DoesNotExist:
            create_follower = Followers(follower=request.user, following=user)
            create_follower.save()
            following = True

        return JsonResponse ({
            "following": following
        }, status=201)

    # Invalid request
    else:
        return JsonResponse ({
            "error": "GET or PUT request required."
        }, status=400)


@login_required(login_url='login')
def following_posts(request):

    # Create list of following ids
    following_list = request.user.following.values_list("following_id", flat=True)

    # Get all follower posts
    following_posts = Post.objects.filter(user__in=following_list)

    return render(request, "network/following.html", {
        "posts": following_posts
    })

@login_required(login_url='login')
def edit_post(request, post_id):

    if request.method == "PUT":
        data = json.loads(request.body)
        post_user_id = data["userID"]

        # Ensure post and user exist
        try:
            post = Post.objects.get(pk=post_id)
            post_user = User.objects.get(pk=post_user_id)
        except (Post.DoesNotExist, User.DoesNotExist):
            return JsonResponse({
                "error": "Invalid request"
            }, status=400)

        # Edit post content
        if data.get("postContent") is not None:

            # Ensure active user matches the post_user and the post.user
            if request.user.id != post_user.id or request.user.id != post.user.id:
                return JsonResponse({
                    "error": "Invalid request"
                }, status=400)
            
            # Update the post content
            else:
                post.content = data["postContent"]
                post.save(update_fields=['content'])
                return JsonResponse({
                    "message": "Post updated"
                }, status=201)

        # Like post
        if data.get("like") is not None:

            # User already likes post, change to unlike
            try:
                user_likes = Like.objects.get(post=post, user=request.user)
                user_likes.delete()
                like = False

            # User does not like post, change to like
            except Like.DoesNotExist:
                create_like = Like(post=post, user=request.user)
                create_like.save()
                like = True

            return JsonResponse ({
                "like": like
            }, status=201)

    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)
