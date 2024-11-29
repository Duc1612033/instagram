from django.contrib import admin
from .models import FriendRequest, Friend, BlockedUser

admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(BlockedUser)
# Register your models here.
