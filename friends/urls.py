# friends/urls.py
from django.urls import path
from . import views 
from .views import block_friend, unblock_friend, list_block_friends, send_friend_request, accept_friend_request, delete_friend_request, friend_requests, list_friends,send_or_cancel_friend_request,search_friends
from authy.views import UserProfile



urlpatterns = [
    path('send_friend_request/<int:user_id>/', send_friend_request, name='send_friend_request'),

    path('requests/', friend_requests, name='friend_requests'),
      path('profile/<str:username>/', UserProfile, name='profile'),
      path('list_friends/', list_friends, name='list_friends'), 
      path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
      path('friend-request/<int:user_id>/', send_or_cancel_friend_request, name='send_or_cancel_friend_request'),
       path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('delete-friend-request/<int:request_id>/', views.delete_friend_request, name='delete_friend_request'),

     path('block/<int:user_id>/', views.block_friend, name='block_friend'),

    path('unblock/<int:blocked_user_id>/', unblock_friend, name='unblock_friend'),
    path('list_block_friends/', list_block_friends, name='list_block_friends'),
       path('search/', views.search_friends, name='search_friends'),
]
