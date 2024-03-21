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
    LeaveTrip,
    PostCreateView,
    PostDetailView,
    PostLike,
    PostDeleteView,
    CommentLike,
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
    path('trip/<int:pk>/add-viewer', views.AddViewer, name='add-viewer'),
    path('trip/<int:pk>/create-viewer', views.CreateViewer, name='create-viewer'),
    path('trip/<int:pk>/leave-trip', views.LeaveTrip, name='leave-trip'),
    path('trip/<int:pk>/post/new', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/like', PostLike.as_view(), name='post-like'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/like', CommentLike.as_view(), name='comment-like'),


]