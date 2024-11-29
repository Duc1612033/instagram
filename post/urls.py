from django.urls import path
from .views import index,react_to_post,search_posts, NewPost, PostDetail, Tags, like, favourite,update_post,delete_post,update_privacy


urlpatterns = [
    path('', index, name='index'),
    # urls.py
path('newpost/<str:app_name>/<str:page_name>/', NewPost, name='newpost'),

    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like', like, name='like'),
    path('<uuid:post_id>/favourite', favourite, name='favourite'),
    
     path('post/<uuid:post_id>/update/', update_post, name='update_post'),
     path('post/<uuid:post_id>/delete/', delete_post, name='delete_post'),
    path('post/<uuid:post_id>/update_privacy/', update_privacy, name='update_privacy'),
     path('search/', search_posts, name='search_posts'),
      path('<uuid:post_id>/react/<str:emoji>/', react_to_post, name='react_to_post'),



]
