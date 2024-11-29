# page/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('pages/', views.page_list, name='page_list'),
    path('pages/new/', views.page_create, name='page_create'),
    path('pages/<int:pk>/', views.page_detail, name='page_detail'),  # Đường dẫn trang chi tiết
    path('pages/<int:pk>/edit/', views.page_update, name='page_update'),
    path('pages/<int:pk>/delete/', views.page_delete, name='page_delete'),
      path('<int:post_id>/update/', views.post_update, name='post_update'),
    path('<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/create/', views.post_create, name='post_create'),
    path('pages/<int:pk>/like/', views.toggle_like, name='toggle_like'),


    
    path('page/<int:page_id>/join/', views.join_page_request, name='join_page_request'),
    path('page/<int:page_id>/manage_requests/', views.manage_page_requests, name='manage_page_requests'),
    path('page/approve_request/<int:membership_id>/<str:action>/', views.approve_page_request, name='approve_page_request'),
    path('page/<int:page_id>/remove_member/<int:member_id>/', views.remove_page_member, name='remove_page_member'),
    
    path('page/<int:page_id>/toggle_membership/', views.toggle_page_membership, name='toggle_page_membership'),
    path('page/<int:page_id>/view_members/', views.view_members, name='view_members'),
    path('pages/<int:page_id>/toggle_post_permission/<int:member_id>/', views.toggle_post_permission, name='toggle_post_permission'),
    path('search/', views.search_pages, name='search_pages'),
]
