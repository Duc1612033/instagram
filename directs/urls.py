from directs.views import inbox,delete_message,delete_message_view,update_message,delete_message, Directs, send_directs, UserSearch, NewConversation,search_all
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', inbox, name="message"),
    path('direct/<username>', Directs, name="directs"),
    
    path('send/', send_directs, name='send-directs'),
    path('new/<username>', NewConversation, name="conversation"),
    path('search/', search_all, name='search_all'),
    path('message/update/<int:message_id>/', update_message, name='update-message'),
  
    
      path('delete-message/<int:message_id>/', delete_message_view, name='delete-message'),
        path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)