import os
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.models import User
from .models import Trip
from .filters import TripFilter
from .forms import TripCreateForm, AddTravellerForm, AddViewerForm

# Create your views here.

def home(request):
    
    return render(request, 'travel/home.html')

class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'travel/home.html'
    allowed_hosts = os.environ.get('ALLOWED_HOSTS')

    print('ALLOWED_HOSTS:', allowed_hosts)
    
    def get_queryset(self):
        # Filter Trips based on the logged-in user
        return Trip.objects.filter(travellers=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = TripFilter(self.request.GET, queryset=self.get_queryset())
        return context
    
class TripDetailView(DetailView):
    model = Trip
    print('Hello')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Access assigned_users within get_context_data
        travellers = self.object.travellers.all()
        context['travellers'] = travellers


        return context

class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripCreateForm

    def form_valid(self, form):
        trip = form.save(commit=False)
        trip.created_by = self.request.user
        trip.save()
        trip.travellers.add(self.request.user)

        
        return super().form_valid(form)
    
class TripUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Trip
    fields = ['title']

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

