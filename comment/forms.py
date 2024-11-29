from django.contrib.auth.models import User
from .models import Comment
from django import forms
from .models import Reply

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ("body","image")

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body","image")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body',]