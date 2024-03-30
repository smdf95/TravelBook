import os
import requests
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView,
    View,
)
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timesince import timesince
from django.urls import reverse_lazy
from geopy.geocoders import Nominatim
from .models import Trip, Post, Comment, Reply
from .filters import TripFilter
from .forms import TripCreateForm, AddTravellerForm, AddViewerForm, PostCreateForm, CommentForm, ReplyForm
import uuid

# Function for calculating time difference between when post/comment/reply was created and when the user is viewing it

def calculate_time_diff(current_time, target_time):
    time_diff = current_time - target_time

    time_diff_hours = int(time_diff.total_seconds() / 3600)
    time_diff_minutes = int(time_diff.total_seconds() / 60)
    time_diff_days = time_diff.days

    if time_diff_minutes < 1:
        return "Just now"
    elif time_diff_minutes == 1:
        return "1 min"
    elif time_diff_minutes < 60:
        return f"{time_diff_minutes} min"
    elif time_diff_hours == 1:
        return "1 hr"
    elif time_diff_hours < 24:
        return f"{time_diff_hours} hr"
    elif time_diff_days == 1:
        return "Yesterday"
    else:
        return None

def home(request):
    
    return render(request, 'travel/home.html')


# Trips views

class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'travel/home.html'
    
    def get_queryset(self):
        # Filter Trips based on the logged-in user
        user = self.request.user
        return Trip.objects.filter(travellers=user) | Trip.objects.filter(viewers=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = TripFilter(self.request.GET, queryset=self.get_queryset())
        return context
    
    
class TripDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Trip


    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Access assigned_users within get_context_data
        travellers = self.object.travellers.all()
        context['travellers'] = travellers

        viewers = self.object.viewers.all()
        context['viewers'] = viewers

        posts = self.object.posts.all().order_by('-created_on')
        context['posts'] = posts

        current_time = timezone.now()

        for post in posts:
            post_time_diff = calculate_time_diff(current_time, post.created_on)
            post.time_diff = post_time_diff


            if post.comments:
                comments = post.comments.all()
                comments_num = comments.count()


                for comment in comments:
                    replies = comment.replies.all()
                    comment.replies_num = replies.count()
                    comments_num += comment.replies_num

                post.comments_num = comments_num


        if posts:
            context['post'] = post

        
        return context

    def test_func(self):
        trip = self.get_object()
        if self.request.user in trip.travellers.all() or self.request.user in trip.viewers.all():
            return True
        return False



class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripCreateForm
    login_url = '/login/'

    def form_valid(self, form):
        trip = form.save(commit=False)
        trip.created_by = self.request.user
        trip.save()
        trip.travellers.add(self.request.user)

        
        return super().form_valid(form)
    
class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    fields = ['title', 'image', 'date_from', 'date_to']
    login_url = '/login/'


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    
    
class TripDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Trip
    success_url = "/"
    login_url = '/login/'


    def test_func(self):
        trip = self.get_object()
        if self.request.user == trip.created_by:
            return True
        return False
    


# Trip interactions (Add travellers/viewers, leave)

def CreateTraveller(request, pk):
    trip = Trip.objects.get(pk=pk)
    
    if request.method == 'POST':
        data = create_invitation_link(request, trip, 'add-traveller')
        return JsonResponse(data)

    context = {'trip': trip}
    return render(request, 'partials/traveller_form.html', context)

def CreateViewer(request, pk):
    trip = Trip.objects.get(pk=pk)
    
    if request.method == 'POST':
        data = create_invitation_link(request, trip, 'add-viewer')
        return JsonResponse(data)

    context = {'trip': trip}
    return render(request, 'partials/viewer_form.html', context)

def create_invitation_link(request, trip, action):
    if action == 'add-traveller':
        unique_link = uuid.uuid4().hex[:10]  # Generate a unique 10-character link
        trip.traveller_invitation_link = unique_link
        link = request.build_absolute_uri(reverse('join-trip', kwargs={'link': unique_link}))
    elif action == 'add-viewer':
        unique_link = uuid.uuid4().hex[:10]  # Generate a unique 10-character link
        trip.viewer_invitation_link = unique_link
        link = request.build_absolute_uri(reverse('join-trip-viewer', kwargs={'link': unique_link}))
    else:
        link = ''

    trip.save()
    return {'link': link}

@login_required
def join_trip(request, link):
    try:
        trip = Trip.objects.get(traveller_invitation_link=link)
    except Trip.DoesNotExist:
        trip = None

    if trip is not None:
        context = {'trip': trip, 'link': link}
        return render(request, 'travel/invite_traveller.html', context)
    else:
        # Invalid link
        return HttpResponse('Invalid invitation link')


def join_trip_final(request, link):
    try:
        trip = Trip.objects.get(traveller_invitation_link=link)
    except Trip.DoesNotExist:
        trip = None

    if trip is not None:
        if request.user not in trip.travellers.all():
            if request.user in trip.viewers.all():
                trip.viewers.remove(request.user)
                trip.travellers.add(request.user)
                trip.save()
                messages.success(request, 'You have successfully joined the trip!')
            else:
                trip.travellers.add(request.user)
                trip.save()
                messages.success(request, 'You have successfully joined the trip!')

            return redirect('trip-detail', pk=trip.pk)
        else:
            messages.warning(request, 'You are already part of this trip!')
            return redirect('trip-detail', pk=trip.pk)
    else:
        # Invalid link
        return HttpResponse('Invalid invitation link')

@login_required
def join_trip_viewer(request, link):
    try:
        trip = Trip.objects.get(viewer_invitation_link=link)
    except Trip.DoesNotExist:
        trip = None

    if trip is not None:
        context = {'trip': trip, 'link': link}
        return render(request, 'travel/invite_viewer.html', context)
    else:
        # Invalid link
        return HttpResponse('Invalid invitation link')

def join_trip_viewer_final(request, link):
    try:
        trip = Trip.objects.get(viewer_invitation_link=link)
    except Trip.DoesNotExist:
        trip = None

    if trip is not None:
        if request.user not in trip.travellers.all() or request.user not in trip.viewers.all():
            trip.viewers.add(request.user)
            trip.save()
            messages.success(request, 'You have successfully joined the trip!')
            return redirect('trip-detail', pk=trip.pk)
        else:
            messages.warning(request, 'You are already part of this trip!')
            return redirect('trip-detail', pk=trip.pk)
    else:
        # Invalid link
        return HttpResponse('Invalid invitation link')



def LeaveTrip(request, pk):
    trip = Trip.objects.get(pk=pk)

    if request.method == 'POST':
        user = request.user
        if user in trip.travellers.all():
            trip.travellers.remove(user)
        elif user in trip.viewers.all():
            trip.viewers.remove(user)
        trip.save()
        return redirect('travel-home')
    
    return render(request, 'travel/leave_confirm.html', {'trip': trip})


# Posts views

class PostCreateView(CreateView):
    model = Post
    form_class = PostCreateForm

    def form_valid(self, form):
        trip_id = self.kwargs['pk']
        trip = Trip.objects.get(pk=trip_id)
        
        post = form.save(commit=False)
        post.created_by = self.request.user
        post.trip = trip  

        geolocator = Nominatim(user_agent="travel_app")
        location = geolocator.geocode(post.location)
        
        if location:
            post.latitude = location.latitude
            post.longitude = location.longitude

        post.save()
        

        
        return super().form_valid(form)
    
class PostView(LoginRequiredMixin, View):
    template_name = "travel/post_detail.html"
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        if post.comments:
            comments = post.comments.all()
            comments_num = comments.count()


            for comment in comments:
                replies = comment.replies.all()
                comment.replies_num = replies.count()
                comments_num += comment.replies_num

            post.comments_num = comments_num

        current_time = timezone.now()

        # Calculate time difference for the post
        post_time_diff = calculate_time_diff(current_time, post.created_on)

        comments_with_replies = []
        # Calculate time difference for comments and replies
        for comment in post.comments.all():
            comment.time_diff = calculate_time_diff(current_time, comment.created_on)
            comment.replies_list = []

            for reply in comment.replies.all():
                reply.time_diff = calculate_time_diff(current_time, reply.created_on)
                comment.replies_list.append(reply)

            comments_with_replies.append(comment)

        context = {
            'post': post,
            'post_time_diff': post_time_diff,
            'comments': comments_with_replies,
            'form': self.form_class
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        post = self.get_object()  # Get the post object
        form = self.form_class(request.POST)  # Initialize the form with POST data

        if form.is_valid():  # Check if the form is valid
            comment = form.save(commit=False)  # Save the form data to a new Comment object without committing to the database
            comment.post = post  # Associate the comment with the current post
            comment.created_by = request.user  # Set the comment's creator to the current user
            comment.save()  # Save the comment to the database
            return redirect('post-detail', pk=post.pk)  # Redirect to the post detail page
            
        # If form is invalid or if it's not a POST request, render the template with the form
        return self.render_to_response(self.get_context_data(form=form))


def PostLike(request, pk):
    instance = get_object_or_404(Post, id=pk)
    form_class = CommentForm()

    if request.method == "POST":
        if not instance.likes.filter(pk=request.user.id).exists():
            instance.likes.add(request.user)
        else:
            instance.likes.remove(request.user)

        instance.save()

    current_time = timezone.now()

    # Calculate time difference for the post
    post_time_diff = calculate_time_diff(current_time, instance.created_on)

    comments_with_replies = []
    # Calculate time difference for comments and replies
    for comment in instance.comments.all():
        comment.time_diff = calculate_time_diff(current_time, comment.created_on)
        comment.replies_list = []

        for reply in comment.replies.all():
            reply.time_diff = calculate_time_diff(current_time, reply.created_on)
            comment.replies_list.append(reply)

        comments_with_replies.append(comment)

    context = {
        'post': instance,
        'post_time_diff': post_time_diff,
        'comments': comments_with_replies,
        'form': form_class
    }

    # If the request is POST, return the rendered template
    if request.method == "POST":
        return render(request, 'travel/post_detail.html', context)

    # If the request is GET, return the rendered template
    return render(request, 'travel/post_detail.html', context)


def PostLikeTripView(request, pk):
    instance = get_object_or_404(Post, id=pk)

    trip = get_object_or_404(Trip, id=instance.trip_id)
    posts = trip.posts.all().order_by('-created_on')

    if request.method == "POST":
        if not instance.likes.filter(pk=request.user.id).exists():
            instance.likes.add(request.user)
        else:
            instance.likes.remove(request.user)

        instance.save()

    current_time = timezone.now()

    for post in posts:
        post_time_diff = calculate_time_diff(current_time, post.created_on)
        post.time_diff = post_time_diff

        if post.comments:
            comments = post.comments.all()
            comments_num = comments.count()

            for comment in comments:
                replies = comment.replies.all()
                comment.replies_num = replies.count()
                comments_num += comment.replies_num

            post.comments_num = comments_num

    context = {
        'trip': trip,
        'posts': posts,
        'post': instance,
    }

    # If the request is POST, return the rendered template
    if request.method == "POST":
        return render(request, 'travel/trip_detail.html', context)

    # If the request is GET, return the rendered template
    return render(request, 'travel/trip_detail.html', context)

        


def PostLikeCount(request, pk):
    instance = get_object_or_404(Post, id=pk)
    likes_count = instance.likes.count()
    return (JsonResponse(likes_count, safe=False))


def CommentLikeCount(request, pk):
    instance = get_object_or_404(Comment, id=pk)
    likes_count = instance.likes.count()
    return (JsonResponse(likes_count, safe=False))

def DeleteComment(request, pk):
    instance = get_object_or_404(Comment, id=pk)
    post = instance.post
    instance.delete()

    comments = post.comments.all()

    current_time = timezone.now()

    comments_with_replies = []

    for comment in comments:
        comment.time_diff = calculate_time_diff(current_time, comment.created_on)

        likes_count = comment.likes.count()
        comment.likes_count = likes_count

        comment.replies_list = []
        for reply in comment.replies.all():
            reply.time_diff = calculate_time_diff(current_time, reply.created_on)
            comment.replies_list.append(reply)

        comments_with_replies.append(comment)



    return render(request, 'partials/comment.html', context={'comments': comments_with_replies})
        
        
        
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('/')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.created_by:
            return True
        return False
    
    def get_success_url(self):
        # Redirect to the trip detail page after successfully deleting the post
        return reverse_lazy('trip-detail', kwargs={'pk': self.object.trip_id})
    
    

# Comments views


def AddComment(request, pk):
    
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, initial={'post_id': post.id})  # Initialize form with POST data
        if form.is_valid():
            comment = form.save(commit=False)  # Save the form data to a new Comment object without committing to the database
            comment.post = post  # Associate the post with the current post
            comment.created_by = request.user  # Set the post's creator to the current user
            comment.save()

            
            post = get_object_or_404(Post, pk=comment.post.id)
            form_class = CommentForm


            if post.comments:
                comments = post.comments.all()
                comments_num = comments.count()


                for comment in comments:
                    replies = comment.replies.all()
                    comment.replies_num = replies.count()
                    comments_num += comment.replies_num

                post.comments_num = comments_num

            current_time = timezone.now()

            # Calculate time difference for the post
            post_time_diff = calculate_time_diff(current_time, post.created_on)

            comments_with_replies = []
            # Calculate time difference for comments and replies
            for comment in post.comments.all():
                comment.time_diff = calculate_time_diff(current_time, comment.created_on)
                comment.replies_list = []

                for reply in comment.replies.all():
                    reply.time_diff = calculate_time_diff(current_time, reply.created_on)
                    comment.replies_list.append(reply)

                comments_with_replies.append(comment)

            context = {
                'post': post,
                'post_time_diff': post_time_diff,
                'comments': comments_with_replies,
                'form': form_class
            }
            return render(request, 'travel/post_detail.html', context)

    else:
        form = CommentForm()  # Initialize an empty form
        context = {'post': post, 'form': form}
        return render(request, 'partials/comment_form.html', context)

    
def CommentLike(request, pk):
    if request.method == "POST":
        instance = Comment.objects.get(id=pk)
        if not instance.likes.filter(pk=request.user.id).exists():
            instance.likes.add(request.user)
            instance.save()
            
            return render(request, 'partials/likes_area.html', context={'comment':instance})
        else:
            instance.likes.remove(request.user)
            instance.save() 

            return render(request, 'partials/likes_area.html', context={'comment':instance})
        


def CommentLikeCount(request, pk):
    instance = get_object_or_404(Comment, id=pk)
    likes_count = instance.likes.count()
    return (JsonResponse(likes_count, safe=False))

def DeleteComment(request, pk):
    instance = get_object_or_404(Comment, id=pk)
    post = instance.post
    instance.delete()

    comments = post.comments.all()

    current_time = timezone.now()

    comments_with_replies = []

    for comment in comments:
        comment.time_diff = calculate_time_diff(current_time, comment.created_on)

        likes_count = comment.likes.count()
        comment.likes_count = likes_count

        comment.replies_list = []
        for reply in comment.replies.all():
            reply.time_diff = calculate_time_diff(current_time, reply.created_on)
            comment.replies_list.append(reply)

        comments_with_replies.append(comment)



    return render(request, 'partials/comment.html', context={'comments': comments_with_replies})


# Reply views


def AddReply(request, pk):
    
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.method == 'POST':
        reply_form = ReplyForm(request.POST, initial={'comment_id': comment.id})  # Initialize form with POST data
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)  # Save the form data to a new Comment object without committing to the database
            reply.comment = comment  # Associate the comment with the current post
            reply.created_by = request.user  # Set the comment's creator to the current user
            reply.save()

            replies = comment.replies.all()
            
            post = get_object_or_404(Post, pk=comment.post.id)
            form_class = CommentForm


            if post.comments:
                comments = post.comments.all()
                comments_num = comments.count()


                for comment in comments:
                    replies = comment.replies.all()
                    comment.replies_num = replies.count()
                    comments_num += comment.replies_num

                post.comments_num = comments_num

            current_time = timezone.now()

            # Calculate time difference for the post
            post_time_diff = calculate_time_diff(current_time, post.created_on)

            comments_with_replies = []
            # Calculate time difference for comments and replies
            for comment in post.comments.all():
                comment.time_diff = calculate_time_diff(current_time, comment.created_on)
                comment.replies_list = []

                for reply in comment.replies.all():
                    reply.time_diff = calculate_time_diff(current_time, reply.created_on)
                    comment.replies_list.append(reply)

                comments_with_replies.append(comment)

            context = {
                'post': post,
                'post_time_diff': post_time_diff,
                'comments': comments_with_replies,
                'form': form_class
            }
            return render(request, 'travel/post_detail.html', context)

    else:
        reply_form = ReplyForm()  # Initialize an empty form
        context = {'comment': comment, 'reply_form': reply_form}
        return render(request, 'partials/reply_form.html', context)
    
def ReplyLike(request, pk):
    if request.method == "POST":
        instance = Reply.objects.get(id=pk)
        if not instance.likes.filter(pk=request.user.id).exists():
            instance.likes.add(request.user)
            instance.save()
            
            return render(request, 'partials/reply_likes_area.html', context={'reply':instance})
        else:
            instance.likes.remove(request.user)
            instance.save() 

            return render(request, 'partials/reply_likes_area.html', context={'reply':instance})
        
def ReplyLikeCount(request, pk):
    instance = get_object_or_404(Reply, id=pk)
    reply_likes_count = instance.likes.count()
    return (JsonResponse(reply_likes_count, safe=False))


    
def DeleteReply(request, pk):
    instance = get_object_or_404(Reply, id=pk)
    comment = instance.comment
    instance.delete()

    replies = comment.replies.all()
    current_time = timezone.now()

    reply_form = ReplyForm()

    comments_with_replies = []

    post = get_object_or_404(Post, pk=comment.post.id)

    comments = post.comments.all()

    for comment in comments:
        comment.time_diff = calculate_time_diff(current_time, comment.created_on)

        likes_count = comment.likes.count()
        comment.likes_count = likes_count

        comment.replies_list = []
        for reply in comment.replies.all():
            reply.time_diff = calculate_time_diff(current_time, reply.created_on)
            comment.replies_list.append(reply)

        comments_with_replies.append(comment)

    context = {'comments': comments_with_replies, 'reply_form': reply_form, 'replies': replies}
    return render(request, 'partials/comment.html', context)


# Map view

@login_required
def show_map(request, location):
    
    location_clean = location.replace(' ', '+')

    location = location

    # Use Google Maps Geocoding API to get latitude and longitude from the location name
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_clean}&key=AIzaSyDY3be2hUJrCXPUE-SAOCEAN8P0UjmB8lk"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
    else:
        latitude = None
        longitude = None

    return render(request, 'travel/map.html', {'latitude': latitude, 'longitude': longitude, 'location': location})

# Like Lists

def like_list(request, pk):
    instance = get_object_or_404(Comment, id=pk)
    comment = instance
    context = {
        'comment': comment,
        'likes': comment.likes.all()
    }
    return render(request, 'partials/likes.html', context)

def post_like_list(request, pk):
    instance = get_object_or_404(Post, id=pk)
    post = instance
    context = {
        'post': post,
        'likes': post.likes.all()
    }
    return render(request, 'partials/post_likes.html', context)

def post_like_list_trip(request, pk):
    instance = get_object_or_404(Post, id=pk)
    post = instance
    context = {
        'post': post,
        'likes': post.likes.all()
    }
    return render(request, 'partials/post_likes_trip.html', context)

def reply_like_list(request, pk):
    instance = get_object_or_404(Reply, id=pk)
    reply = instance
    context = {
        'reply': reply,
        'likes': reply.likes.all()
    }
    return render(request, 'partials/reply_likes.html', context)


def close_like(request, pk):
    
    comment = get_object_or_404(Comment, pk=pk)
    
    form_class = CommentForm()
    
    post = get_object_or_404(Post, pk=comment.post.id)


    if post.comments:
        comments = post.comments.all()
        comments_num = comments.count()


        for comment in comments:
            replies = comment.replies.all()
            comment.replies_num = replies.count()
            comments_num += comment.replies_num

        post.comments_num = comments_num

    current_time = timezone.now()

    # Calculate time difference for the post
    post_time_diff = calculate_time_diff(current_time, post.created_on)

    comments_with_replies = []
    # Calculate time difference for comments and replies
    for comment in post.comments.all():
        comment.time_diff = calculate_time_diff(current_time, comment.created_on)
        comment.replies_list = []

        for reply in comment.replies.all():
            reply.time_diff = calculate_time_diff(current_time, reply.created_on)
            comment.replies_list.append(reply)

        comments_with_replies.append(comment)

    context = {
        'post': post,
        'post_time_diff': post_time_diff,
        'comments': comments_with_replies,
        'form': form_class
    }
    return render(request, 'travel/post_detail.html', context)

