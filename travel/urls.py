from django.urls import path
from .views import (
    TripListView,
    TripCreateView,
    TripDetailView,
    TripUpdateView,
    TripDeleteView,
    AddTraveller,
    CreateTraveller,
    AddViewer,
    CreateViewer,
)
from . import views

urlpatterns = [
    path('', TripListView.as_view(), name='travel-home'),
    path('trip/new', TripCreateView.as_view(), name='travel-create'),
    path('trip/<int:pk>', TripDetailView.as_view(), name='travel-detail'),
    path('trip/<int:pk>/update', TripUpdateView.as_view(), name='travel-update'),
    path('trip/<int:pk>/delete', TripDeleteView.as_view(), name='travel-delete'),
    path('trip/<int:pk>/add_traveller', views.AddTraveller, name='add-traveller'),
    path('trip/<int:pk>/create-traveller', views.CreateTraveller, name='create-traveller'),
    path('trip/<int:pk>/add_viewer', views.AddViewer, name='add-viewer'),
    path('trip/<int:pk>/create-viewer', views.CreateViewer, name='create-viewer'),
]