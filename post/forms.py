from django import forms
from post.models import Post



class PostPrivacyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['privacy']


class NewPostform(forms.ModelForm):
    # content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}), required=True)

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']


# Trong forms.py của app post
from django import forms
from .models import Post  # Giả sử model của bài viết tên là Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'picture', 'tags'] 
