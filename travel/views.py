import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
from .models import Trip, Post, Comment, Reply
from .filters import TripFilter
from .forms import TripCreateForm, AddTravellerForm, AddViewerForm, PostCreateForm, CommentForm

# Create your views here.

def home(request):
    
    return render(request, 'travel/home.html')

class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'travel/home.html'
    
    def get_queryset(self):
        # Filter Trips based on the logged-in user
        return Trip.objects.filter(travellers=self.request.user)

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

        posts = self.object.posts.all().order_by('-created_on')
        context['posts'] = posts

        for post in posts:
            current_time = timezone.now()
            time_diff = current_time - post.created_on
            
            time_diff_hours = time_diff.total_seconds() / 3600
            time_diff_minutes = time_diff.total_seconds() / 60
            time_diff_days = time_diff.days
            
            if time_diff_minutes < 1:
                post.time_diff = "Just now"  # Display time difference in hours
            elif time_diff_minutes < 2:
                post.time_diff = f"{int(time_diff_minutes)} minute ago"  # Display time difference in hours
            elif time_diff_minutes < 60:
                post.time_diff = f"{int(time_diff_minutes)} minutes ago"  # Display time difference in hours
            elif time_diff_hours < 2:
                post.time_diff = f"{int(time_diff_hours)} hour ago"  # Display time difference in hours
            elif time_diff_hours <= 24:
                post.time_diff = f"{int(time_diff_hours)} hours ago"  # Display time difference in hours
            elif time_diff_days == 1:
                post.time_diff = "Yesterday"
            else:
                post.time_diff = None

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

    def form_valid(self, form):
        trip = form.save(commit=False)
        trip.created_by = self.request.user
        trip.save()
        trip.travellers.add(self.request.user)

        
        return super().form_valid(form)
    
class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    fields = ['title', 'image']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        trip = self.get_object()
        if self.request.user == trip.created_by:
            return True
        return False
    
class TripDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Trip
    success_url = "/"

    def test_func(self):
        trip = self.get_object()
        if self.request.user == trip.created_by:
            return True
        return False
    
def AddTraveller(request, pk):
    # Assuming Trip is your model
    trip = Trip.objects.get(pk=pk)
    context = {'form': AddTravellerForm, 'trip': trip, 'travellers': trip.travellers.all()}
    return render(request, 'travel/add_traveller.html', context)


def CreateTraveller(request, pk):
    trip = Trip.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = AddTravellerForm(request.POST)  # Initialize form with POST data
        if form.is_valid():
            email = form.cleaned_data['travellers']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                print('No such user with the provided email.')
            else:
                trip.travellers.add(user)
                context = {'traveller': user}
                return render(request, 'partials/traveller.html', context)
    else:
        form = AddTravellerForm()  # Initialize an empty form

    context = {'trip': trip, 'form': form}
    return render(request, 'partials/traveller_form.html', context)

def AddViewer(request, pk):
    # Assuming Trip is your model
    trip = Trip.objects.get(pk=pk)
    context = {'form': AddViewerForm, 'trip': trip, 'viewers': trip.viewers.all()}
    return render(request, 'travel/add_viewer.html', context)


def CreateViewer(request, pk):
    trip = Trip.objects.get(pk=pk)
    
    if request.method == 'POST':
        form = AddViewerForm(request.POST)  # Initialize form with POST data
        if form.is_valid():
            email = form.cleaned_data['viewers']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                print('No such user with the provided email.')
            else:
                trip.viewers.add(user)
                context = {'viewer': user}
                return render(request, 'partials/viewer.html', context)
    else:
        form = AddViewerForm()  # Initialize an empty form

    context = {'trip': trip, 'form': form}
    return render(request, 'partials/viewer_form.html', context)

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

class PostCreateView(CreateView):
    model = Post
    form_class = PostCreateForm

    def form_valid(self, form):
        trip_id = self.kwargs['pk']
        trip = Trip.objects.get(pk=trip_id)
        
        post = form.save(commit=False)
        post.created_by = self.request.user
        post.trip = trip  # Assign the Trip instance, not the trip ID
        post.save()

        

        
        return super().form_valid(form)
    
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "travel/post_detail.html"
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object  # The post object is available as self.object
        
        current_time = timezone.now()
        time_diff = current_time - post.created_on
        
        current_time = timezone.now()
        time_diff = current_time - post.created_on
        
        time_diff_hours = time_diff.total_seconds() / 3600
        time_diff_minutes = time_diff.total_seconds() / 60
        time_diff_days = time_diff.days
        
        if time_diff_minutes < 1:
            post.time_diff = "Just now"  # Display time difference in hours
        elif time_diff_minutes < 2:
            post.time_diff = f"{int(time_diff_minutes)} minute ago"  # Display time difference in hours
        elif time_diff_minutes < 60:
            post.time_diff = f"{int(time_diff_minutes)} minutes ago"  # Display time difference in hours
        elif time_diff_hours < 2:
            post.time_diff = f"{int(time_diff_hours)} hour ago"  # Display time difference in hours
        elif time_diff_hours <= 24:
            post.time_diff = f"{int(time_diff_hours)} hours ago"  # Display time difference in hours
        elif time_diff_days == 1:
            post.time_diff = "Yesterday"
        else:
            post.time_diff = None

        
        
        context['post'] = post  # Add the post object to the context

        comments = post.comments.all()
        context['comments'] = comments
        
        for comment in comments:
            time_diff = current_time - comment.created_on
            
            current_time = timezone.now()
            time_diff = current_time - comment.created_on
            
            time_diff_hours = time_diff.total_seconds() / 3600
            time_diff_minutes = time_diff.total_seconds() / 60
            time_diff_days = time_diff.days
            
            if time_diff_minutes < 1:
                comment.time_diff = "Just now"  # Display time difference in hours
            elif time_diff_minutes < 2:
                comment.time_diff = f"{int(time_diff_minutes)} minute ago"  # Display time difference in hours
            elif time_diff_minutes < 60:
                comment.time_diff = f"{int(time_diff_minutes)} minutes ago"  # Display time difference in hours
            elif time_diff_hours < 2:
                comment.time_diff = f"{int(time_diff_hours)} hour ago"  # Display time difference in hours
            elif time_diff_hours <= 24:
                comment.time_diff = f"{int(time_diff_hours)} hours ago"  # Display time difference in hours
            elif time_diff_days == 1:
                comment.time_diff = "Yesterday"
            else:
                comment.time_diff = None

        if comments:
            context['comment'] = comment

            
        

        form = CommentForm()

        context['form'] = form

        return context
    
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
    


class PostLike(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        # Redirect to the previous page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('post-detail', pk=pk)
        
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
        return reverse_lazy('travel-detail', kwargs={'pk': self.object.trip_id})
    
class CommentLike(View):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)

        
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)

       
        return redirect('post-detail', pk=comment.post_id)
    

        


