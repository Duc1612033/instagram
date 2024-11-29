from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Các URL khác của bạn
    path('edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('post/<uuid:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
     path('reply/edit/<int:reply_id>/', views.edit_reply, name='edit_reply'),
    path('reply/delete/<int:reply_id>/', views.delete_reply, name='delete_reply'),
    path('like_comment/', views.like_comment, name='like_comment'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
