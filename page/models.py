# page/models.py
from django.db import models
from django.contrib.auth.models import User
import random


# Định nghĩa hàm để lấy người dùng ngẫu nhiên
def get_random_user():
    users = User.objects.all()
    return random.choice(users).id if users else None

class Page(models.Model):
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100,null=True)
    owner = models.CharField(max_length=100,null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_pages')
    likes = models.ManyToManyField(User, related_name='liked_pages', blank=True)  # This tracks users who liked the page

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class PageMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    can_post = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.page.title}"        
        
class Post(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    images = models.ImageField(upload_to='posts/')
    content = models.TextField(default="Nội dung mặc định") 
      # Liên kết với Page
    page = models.ForeignKey(Page, related_name='posts', on_delete=models.CASCADE, null=True) 
    def __str__(self):
        return self.name

