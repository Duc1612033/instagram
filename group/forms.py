from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description"]  # Các trường mà bạn muốn người dùng nhập




