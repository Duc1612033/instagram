from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('groups/', views.list_groups, name='list_groups'),
    path('groupdetail/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group_request, name='join_group_request'),
    path('groups/<int:group_id>/manage_requests/', views.manage_requests, name='manage_requests'),
    path('approve_request/<int:membership_id>/<str:action>/', views.approve_request, name='approve_request'),
    path("create/", views.create_group, name="create_group"),
    path("groups/join/<int:group_id>/", views.join_group, name="join_group"),  
    path('groups/<int:group_id>/remove_member/<int:member_id>/', views.remove_member, name='remove_member'),
    path('group/<int:group_id>/update/', views.update_group, name='update_group'),
    path('group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('group/<int:group_id>/toggle_membership/', views.toggle_membership, name='toggle_membership'),
    path('group/<int:group_id>/toggle_post_permission/<int:member_id>/', views.toggle_post_permission, name='toggle'),
    path('group/<int:group_id>/view_members/', views.view_members, name='view_group_members'),
    path('search/', views.search_groups, name='search_groups'),



  
]
