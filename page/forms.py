# page/forms.py
from django import forms
from .models import Page

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['title']

# post/forms.py

from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name','content', 'images','tag']

