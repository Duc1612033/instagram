from django.contrib import admin
from comment.models import Comment,Reply

admin.site.register(Comment)
admin.site.register(Reply)