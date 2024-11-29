# friends/models.py
from django.db import models
from django.contrib.auth.models import User

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('from_user', 'to_user') 
        
class Friend(models.Model):
    name = models.CharField(max_length=100,null=True)
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friends_with', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"


class BlockedUser(models.Model):
    user = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User, related_name='blocked_users', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} has blocked {self.blocked_user.username}"
