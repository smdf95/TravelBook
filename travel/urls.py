from django.urls import path
from . import views
from .views import (
    TripListView,
    TripCreateView,
    TripDetailView,
    TripUpdateView,
    TripDeleteView,
    PostCreateView,
    PostView,
    PostDeleteView,
)

urlpatterns = [
    path('', TripListView.as_view(), name='travel-home'),
    
    # Trip URLs
    path('trip/new', TripCreateView.as_view(), name='trip-create'),
    path('trip/<int:pk>', TripDetailView.as_view(), name='trip-detail'),
    path('trip/<int:pk>/update', TripUpdateView.as_view(), name='trip-update'),
    path('trip/<int:pk>/delete', TripDeleteView.as_view(), name='trip-delete'),
    path('trip/<int:pk>/add_traveller', views.AddTraveller, name='add-traveller'),
    path('trip/<int:pk>/create-traveller', views.CreateTraveller, name='create-traveller'),
    path('trip/<int:pk>/add-viewer', views.AddViewer, name='add-viewer'),
    path('trip/<int:pk>/create-viewer', views.CreateViewer, name='create-viewer'),
    path('trip/<int:pk>/leave-trip', views.LeaveTrip, name='leave-trip'),
    
    # Post URLs
    path('trip/<int:pk>/post/new', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>', PostView.as_view(), name='post-detail'),
    path('post/<int:pk>/like', views.PostLike, name='post-like'),
    path('trip/post/<int:pk>/like', views.PostLikeTripView, name='post-like-trip'),
    path('post/<int:pk>/like_count', views.PostLikeCount, name='post-like-count'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    
    
    # Comment URLs
    path('post/<int:pk>/comment', views.AddComment, name='add-comment'),
    path('comment/<int:pk>/like', views.CommentLike, name='comment-like'),
    path('comment/<int:pk>/like_count', views.CommentLikeCount, name='comment-like-count'),
    path('comment/<int:pk>/delete', views.DeleteComment, name='comment-delete'),
    path('comment/<int:pk>/reply', views.AddReply, name='add-reply'),
    
    # Reply URLs
    path('reply/<int:pk>/like', views.ReplyLike, name='reply-like'),
    path('reply/<int:pk>/like_count', views.ReplyLikeCount, name='reply-like-count'),
    path('reply/<int:pk>/delete', views.DeleteReply, name='reply-delete'),
    
    # Map URL
    path('map/<str:location>', views.show_map, name='maps'),
    
    # Like and Reply Like List URLs
    path('like_list/<int:pk>', views.like_list, name='like_list'),
    path('reply_like_list/<int:pk>', views.reply_like_list, name='reply_like_list'),
    path('post_like_list/<int:pk>', views.post_like_list, name='post_like_list'),
    path('post_like_list_trip/<int:pk>', views.post_like_list_trip, name='post_like_list_trip'),
    
    # Close Like URL
    path('close_like/<int:pk>', views.close_like, name='close_like'),
]
