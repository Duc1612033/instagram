from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from post.models import Post
from django.db.models.signals import post_save, post_delete
from notification.models import Notification


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True) 
    
    @property
    def like_count(self):
        return self.likes.count()

    @staticmethod
    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.body[:90]
        sender = comment.user
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()

    @staticmethod
    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = Notification.objects.filter(post=post, sender=sender, user=post.user, notification_types=2)
        notify.delete()
    

    # def __str__(self):
    #     return self.post
# models.py

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"

    

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_replies", blank=True)
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True) 

    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username} - {self.body[:20]}"    
    
    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.body[:90]
        sender = comment.user
        notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()

    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = Notification.objects.filter(post=post, sender=sender, user=post.user, notification_types=2)
        notify.delete()

post_save.connect(Comment.user_comment_post, sender=Comment)
post_delete.connect(Comment.user_del_comment_post, sender=Comment)
